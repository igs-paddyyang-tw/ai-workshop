"""Persistent Daemon — 常駐進程生命週期管理、健康巡檢、訊息佇列。

整合 ManagedProcess + KiroBackend + FailureMemory + MessageOverflow + Heartbeat。
"""
from __future__ import annotations

import asyncio
import hashlib
import logging
import time
from dataclasses import dataclass, field
from enum import StrEnum
from pathlib import Path
from typing import Callable, Awaitable

from .config import TeamConfig, InstanceConfig, load_config
from .failure_memory import FailureMemory
from .heartbeat import heartbeat_loop
from .kiro_backend import KiroBackend, KiroBackendConfig
from .managed_process import ManagedProcess, register, unregister
from .message_overflow import MessageOverflow

log = logging.getLogger(__name__)


class InstanceStatus(StrEnum):
    STOPPED = "stopped"
    STARTING = "starting"
    RUNNING = "running"
    CRASHED = "crashed"
    PAUSED = "paused"


@dataclass
class InstanceState:
    """單一 agent instance 的 runtime 狀態。"""
    config: InstanceConfig
    status: InstanceStatus = InstanceStatus.STOPPED
    process: ManagedProcess | None = None
    crash_count: int = 0
    last_activity: float = 0.0
    last_task: str = ""
    _msg_queue: asyncio.Queue = field(default_factory=lambda: asyncio.Queue(maxsize=50))
    _queue_task: asyncio.Task | None = field(default=None, repr=False)


class PersistentDaemon:
    """管理所有常駐 Kiro CLI instance 的 Daemon。"""

    def __init__(self, config_path: str = "team.yaml") -> None:
        self.config = load_config(config_path)
        self.backend = KiroBackend()
        self.instances: dict[str, InstanceState] = {}
        self._failure_memory = FailureMemory()
        self._overflow: MessageOverflow | None = None
        self._health_loop_task: asyncio.Task | None = None
        self._heartbeat_task: asyncio.Task | None = None
        self._last_output_count: dict[str, int] = {}
        self._cooldown_until: dict[str, float] = {}
        self._last_output_hash: dict[str, str] = {}
        # Callbacks
        self.on_hang_detected: Callable[[str, float], Awaitable[None]] | None = None

    # ── Lifecycle ───────────────────────────────────────────────

    async def start_instance(self, name: str, *, skip_resume: bool = False) -> None:
        """啟動單一 agent instance。"""
        ic = self.config.instances.get(name)
        if not ic:
            raise ValueError(f"Unknown instance: {name}")

        state = self.instances.get(name)
        if state and state.status == InstanceStatus.RUNNING:
            log.warning("Instance %s already running", name)
            return

        if not state:
            state = InstanceState(config=ic)
            self.instances[name] = state

        state.status = InstanceStatus.STARTING

        # 確保工作目錄存在
        cwd = Path(ic.working_directory)
        cwd.mkdir(parents=True, exist_ok=True)

        # 偵測 MCP config 是否變更
        actual_skip = skip_resume or ic.skip_resume
        if not actual_skip:
            actual_skip = self._should_skip_resume(name, cwd)

        # 建構命令
        cfg = KiroBackendConfig(
            working_directory=ic.working_directory,
            instance_name=name,
            skip_resume=actual_skip,
            model=ic.model if ic.model != "auto" else None,
        )
        cmd = self.backend.build_command(cfg)

        # 啟動進程
        mp = ManagedProcess(name=name)
        if state.process and state.process.is_alive():
            await state.process.kill()
            unregister(name)

        await mp.start(cmd, cwd=ic.working_directory)
        register(mp)
        state.process = mp

        # 等待就緒
        ready = await self._wait_for_ready(state, timeout=60.0)
        if ready:
            state.status = InstanceStatus.RUNNING
            state.last_activity = time.time()
            self._failure_memory.clear(name)
            log.info("Instance %s is ready (pid=%s)", name, mp.pid)
            # 啟動 queue worker
            if state._queue_task and not state._queue_task.done():
                state._queue_task.cancel()
            state._queue_task = asyncio.create_task(self._queue_worker(name))
            self._ensure_health_loop()
        else:
            state.status = InstanceStatus.CRASHED
            log.error("Instance %s failed to start", name)

    async def stop_instance(self, name: str) -> None:
        """停止單一 instance。"""
        state = self.instances.get(name)
        if not state or state.status == InstanceStatus.STOPPED:
            return

        # 送 /quit
        if state.process and state.process.is_alive():
            try:
                await state.process.send_input(self.backend.quit_command())
                await asyncio.sleep(2)
            except (RuntimeError, OSError):
                pass

        # Kill
        if state.process:
            await state.process.kill()
            unregister(name)

        # 停止 queue
        if state._queue_task:
            state._queue_task.cancel()
            state._queue_task = None

        state.status = InstanceStatus.STOPPED
        log.info("Instance %s stopped", name)

    async def restart_instance(self, name: str) -> None:
        """重啟 instance。"""
        await self.stop_instance(name)
        await asyncio.sleep(1)
        await self.start_instance(name)

    # ── Message delivery ────────────────────────────────────────

    async def send_message(self, name: str, text: str) -> bool:
        """送訊息給 agent（加入 queue，backpressure 時持久化）。"""
        state = self.instances.get(name)
        if not state:
            log.warning("Cannot send to %s: not defined", name)
            return False
        if state.status != InstanceStatus.RUNNING or not state.process:
            log.warning("Cannot send to %s: status=%s", name, state.status.value)
            return False

        try:
            if state._msg_queue.qsize() >= 5 and self._overflow:
                log.warning("Backpressure: %s queue at %d, persisting", name, state._msg_queue.qsize())
                self._overflow.store(name, text)
                return True
            state._msg_queue.put_nowait(text)
            state.last_task = text[:60]
            return True
        except asyncio.QueueFull:
            if self._overflow:
                self._overflow.store(name, text)
            return True

    async def _queue_worker(self, name: str) -> None:
        """Per-instance: 從 queue 取訊息 → send_input → 動態 delay。"""
        state = self.instances[name]
        while True:
            try:
                # 嘗試從 queue 取（timeout 後檢查 overflow）
                try:
                    text = await asyncio.wait_for(state._msg_queue.get(), timeout=5.0)
                except asyncio.TimeoutError:
                    # Replay overflow
                    if self._overflow:
                        pending = self._overflow.pending(name, limit=1)
                        if pending and state.status == InstanceStatus.RUNNING and state.process:
                            msg_id, text = pending[0]
                            await state.process.send_input(text)
                            state.last_activity = time.time()
                            self._overflow.mark_delivered(msg_id)
                            await asyncio.sleep(2.0)
                    continue

                if state.status == InstanceStatus.RUNNING and state.process:
                    await state.process.send_input(text)
                    state.last_activity = time.time()
                    # 動態間隔
                    qsize = state._msg_queue.qsize()
                    delay = 1.0 if qsize <= 2 else min(2.0 + qsize * 0.5, 5.0)
                    await asyncio.sleep(delay)
                state._msg_queue.task_done()

            except asyncio.CancelledError:
                return
            except RuntimeError as e:
                log.warning("Queue worker pipe error for %s: %s", name, e)
                try:
                    state._msg_queue.task_done()
                except ValueError:
                    pass
                await asyncio.sleep(5)
                if state.process and state.process._pipe_broken:
                    state.status = InstanceStatus.CRASHED
                    return
                if not state.process or not state.process.is_alive():
                    return
            except Exception as e:
                log.warning("Queue worker error for %s: %s", name, e)
                try:
                    state._msg_queue.task_done()
                except ValueError:
                    pass

    # ── Health Loop ─────────────────────────────────────────────

    def _ensure_health_loop(self) -> None:
        if not self._health_loop_task or self._health_loop_task.done():
            self._health_loop_task = asyncio.create_task(self._global_health_loop())

    async def _global_health_loop(self) -> None:
        """30 秒巡檢所有 instance。"""
        interval = 30
        cooldown_seconds = 600
        max_retries = 3

        while True:
            await asyncio.sleep(interval)

            for name, state in list(self.instances.items()):
                if state.status in (InstanceStatus.STOPPED, InstanceStatus.PAUSED):
                    continue

                # Cooldown 中
                cooldown_until = self._cooldown_until.get(name, 0)
                if cooldown_until > 0:
                    if time.time() < cooldown_until:
                        continue
                    log.info("🔄 %s 冷卻結束，重啟", name)
                    state.crash_count = 0
                    self._cooldown_until.pop(name, None)
                    self._failure_memory.clear(name)
                    if state.process and state.process.is_alive():
                        continue
                    try:
                        await self.start_instance(name, skip_resume=True)
                    except Exception as e:
                        log.error("Failed to restart %s after cooldown: %s", name, e)
                    continue

                # 崩潰偵測
                if not state.process or not state.process.is_alive():
                    if state.status == InstanceStatus.RUNNING:
                        log.warning("Instance %s process died", name)
                        state.status = InstanceStatus.CRASHED
                        state.crash_count += 1

                    if state.status == InstanceStatus.CRASHED:
                        if state.crash_count <= max_retries:
                            delay = min(2 ** state.crash_count, 300)
                            log.info("Restarting %s in %ds (attempt %d)", name, delay, state.crash_count)
                            await asyncio.sleep(delay)
                            try:
                                await self.start_instance(name, skip_resume=True)
                            except Exception as e:
                                log.error("Failed to restart %s: %s", name, e)
                        else:
                            log.warning("Instance %s exceeded max retries, cooldown %ds", name, cooldown_seconds)
                            self._cooldown_until[name] = time.time() + cooldown_seconds
                    continue

                # 活動偵測（有新 output → 重置 crash count）
                if state.process:
                    current_count = state.process.output_count
                    last_count = self._last_output_count.get(name, 0)
                    if current_count > last_count:
                        state.last_activity = time.time()
                        if state.crash_count > 0:
                            state.crash_count = 0
                    self._last_output_count[name] = current_count

                # Error pattern 偵測
                output = state.process.capture(lines=30) if state.process else ""
                if output:
                    _output_hash = hashlib.md5(output.encode()).hexdigest()
                    if _output_hash != self._last_output_hash.get(name):
                        self._last_output_hash[name] = _output_hash
                        error = KiroBackend.detect_error(output)
                        if error:
                            err_type, err_msg = error
                            is_repeating = self._failure_memory.record(name, err_type, err_msg)
                            if is_repeating:
                                log.warning("Failure pattern: %s", self._failure_memory.summary(name))
                                if err_type == "rate_limit":
                                    consecutive = self._failure_memory.consecutive_count(name)
                                    if consecutive >= 3:
                                        self._cooldown_until[name] = time.time() + 90
                                        log.warning("Rate limit soft-pause: %s 90s", name)

                # Runtime dialog 處理
                if state.process and KiroBackend.has_runtime_dialog(output):
                    try:
                        await state.process.send_input("\x1b[B")
                        await asyncio.sleep(0.3)
                        await state.process.send_input("")
                    except (RuntimeError, OSError):
                        pass

    # ── Team operations ─────────────────────────────────────────

    async def start_all(self) -> dict[str, bool]:
        """啟動所有 instance。"""
        # 初始化 overflow DB
        state_dir = Path("state")
        state_dir.mkdir(parents=True, exist_ok=True)
        self._overflow = MessageOverflow(state_dir / "message_overflow.db")

        # 啟動 heartbeat
        self._heartbeat_task = asyncio.create_task(heartbeat_loop(state_dir))

        results: dict[str, bool] = {}
        for name in self.config.instances:
            try:
                await self.start_instance(name)
                results[name] = True
            except Exception as e:
                log.error("Failed to start %s: %s", name, e)
                results[name] = False
            await asyncio.sleep(2)  # stagger
        return results

    async def stop_all(self) -> None:
        """停止所有 instance。"""
        for name in list(self.instances):
            await self.stop_instance(name)
        if self._health_loop_task:
            self._health_loop_task.cancel()
        if self._heartbeat_task:
            self._heartbeat_task.cancel()
        if self._overflow:
            self._overflow.close()

    def get_status(self) -> list[dict]:
        """取得所有 instance 狀態。"""
        return [
            {
                "name": name,
                "status": state.status.value,
                "pid": state.process.pid if state.process else None,
                "crash_count": state.crash_count,
                "last_activity": state.last_activity,
            }
            for name, state in self.instances.items()
        ]

    # ── Internal helpers ────────────────────────────────────────

    async def _wait_for_ready(self, state: InstanceState, timeout: float = 60.0) -> bool:
        """等待 kiro-cli 就緒（偵測 READY_PATTERN）。"""
        deadline = time.time() + timeout
        while time.time() < deadline:
            if not state.process or not state.process.is_alive():
                return False

            output = state.process.capture(lines=50)

            if KiroBackend.has_startup_dialog(output):
                log.info("Instance %s: dismissing trust dialog", state.config.name)
                try:
                    await state.process.send_input("\x1b[B")
                    await asyncio.sleep(0.3)
                    await state.process.send_input("")
                except (RuntimeError, OSError):
                    pass
                await asyncio.sleep(2)
                continue

            if KiroBackend.is_ready(output):
                return True

            err = KiroBackend.detect_error(output)
            if err and err[0] in ("auth_error", "quota"):
                log.error("Instance %s fatal: %s", state.config.name, err[1])
                return False

            await asyncio.sleep(2)

        log.error("Instance %s startup timeout (%.0fs)", state.config.name, timeout)
        return False

    def _should_skip_resume(self, name: str, cwd: Path) -> bool:
        """偵測 MCP config 變更 → 強制 skip_resume。"""
        mcp_path = cwd / ".kiro" / "settings" / "mcp.json"
        hash_file = cwd / ".kiro" / ".mcp_hash"

        if not mcp_path.exists():
            return False
        try:
            current_hash = hashlib.md5(mcp_path.read_bytes()).hexdigest()
        except OSError:
            return False

        if hash_file.exists():
            stored_hash = hash_file.read_text(encoding="utf-8").strip()
            if current_hash != stored_hash:
                log.info("MCP config changed for %s, forcing clean session", name)
                hash_file.write_text(current_hash, encoding="utf-8")
                return True
            return False
        else:
            hash_file.parent.mkdir(parents=True, exist_ok=True)
            hash_file.write_text(current_hash, encoding="utf-8")
            return False
