"""Agent CLI — Agent 常駐服務（使用 AgentProcess）。

啟動時從 agents.yaml 載入 Agent 定義，建立 AgentProcess 常駐服務。
對話時透過 send() 排隊執行。
"""
from __future__ import annotations

import asyncio
import logging
import shutil
from pathlib import Path

from src.agent.process import AgentProcess

log = logging.getLogger("agent-cli")

# ── 從 agents.yaml 載入 Agent 定義 ──

BASE_DIR = Path(__file__).resolve().parents[2]
_AGENTS_YAML = BASE_DIR / "agents.yaml"


def _load_agents_config() -> dict:
    """從 agents.yaml 載入 Agent 定義。找不到則回傳空 dict。"""
    if not _AGENTS_YAML.exists():
        log.warning("agents.yaml not found at %s", _AGENTS_YAML)
        return {}
    try:
        import yaml
        data = yaml.safe_load(_AGENTS_YAML.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except Exception as e:
        log.error("Failed to load agents.yaml: %s", e)
        return {}


def _get_available_agents() -> dict:
    """取得 AVAILABLE_AGENTS dict（快取）。"""
    global _agents_cache
    if _agents_cache is not None:
        return _agents_cache
    _agents_cache = _load_agents_config()
    return _agents_cache


_agents_cache: dict | None = None

# 向後相容：模組層級 AVAILABLE_AGENTS（lazy property 不可能，用函式 + 延遲載入）
# 其他模組 import AVAILABLE_AGENTS 時會拿到這個 dict
AVAILABLE_AGENTS = _load_agents_config()


def get_dispatchable_agents() -> list[str]:
    """取得可被 dispatch_to_agent 派工的 agent ID 列表。"""
    agents = _get_available_agents()
    return [
        f"{aid}-agent" for aid, info in agents.items()
        if info.get("dispatchable", False)
    ]

# ── Agent 服務管理 ──

_agents: dict[str, AgentProcess] = {}
_started: bool = False


def is_cli_available() -> bool:
    """檢查指定的 CLI backend 是否已安裝。"""
    backend = get_available_backend()
    cmd = _resolve_cmd(backend)
    return cmd is not None


def get_available_backend() -> str:
    """從 CLI_BACKEND 環境變數取得 backend，未設定則自動偵測。"""
    import os
    env_val = os.getenv("CLI_BACKEND", "").strip().lower()
    if env_val in ("kiro", "agy", "claude"):
        return env_val
    # 自動偵測
    if _resolve_cmd("kiro"):
        return "kiro"
    if _resolve_cmd("agy"):
        return "agy"
    if _resolve_cmd("claude"):
        return "claude"
    return "kiro"


def _resolve_cmd(backend: str) -> str | None:
    """解析 backend 對應的可執行檔完整路徑，找不到回傳 None。"""
    import os
    cmd_map = {"kiro": "kiro-cli", "agy": "agy", "claude": "claude"}
    cmd = cmd_map.get(backend, backend)
    # 先查 PATH
    found = shutil.which(cmd)
    if found:
        return found
    # Fallback: 已知安裝路徑（不自動加 PATH 的工具）
    fallback_paths = {
        "agy": os.path.join(os.environ.get("LOCALAPPDATA", ""), "agy", "bin", "agy.exe"),
    }
    fallback = fallback_paths.get(backend)
    if fallback and os.path.isfile(fallback):
        return fallback
    return None


async def start_all_agents() -> int:
    """啟動 8 個 Agent 常駐服務。回傳成功數量。"""
    global _started
    if _started:
        return len(_agents)
    if not is_cli_available():
        log.info("未偵測到任何 CLI backend（kiro-cli / agy / claude），跳過 Agent 服務啟動")
        return 0

    backend = get_available_backend()
    log.info("使用 CLI backend: %s", backend)

    count = 0
    for agent_id, info in AVAILABLE_AGENTS.items():
        # Default (Ark Agent) 走 Gemini agent_loop，不需要 CLI 進程
        if agent_id == "default":
            continue
        name = f"{agent_id}-agent"
        working_dir = info["dir"]
        proc = AgentProcess(
            name=name,
            working_dir=working_dir,
            model="auto",
            skip_resume=True,
            backend=backend,
        )
        proc.timeout = 180
        await proc.start()
        _agents[agent_id] = proc
        count += 1

    _started = True
    log.info("All %d agents registered", count)
    return count


async def stop_all_agents() -> None:
    """停止所有 Agent。"""
    global _started
    for proc in _agents.values():
        await proc.kill()
    _agents.clear()
    _started = False


async def agent_cli_chat(
    message: str,
    *,
    agent_id: str = "admin",
    timeout: int = 120,
) -> str | None:
    """透過 AgentProcess 執行對話。

    如果服務已啟動 → 用 send()（排隊執行）
    如果服務沒啟動 → fallback 到直接 subprocess
    """
    # 優先用常駐服務
    proc = _agents.get(agent_id)
    if proc and proc.is_alive():
        result = await proc.send(message)
        return result if result else None

    # Fallback: 直接 subprocess（相容舊行為）
    if not is_cli_available():
        return None

    info = AVAILABLE_AGENTS.get(agent_id, AVAILABLE_AGENTS["admin"])
    working_dir = Path(info["dir"])
    if not (working_dir / ".kiro" / "steering" / "SOUL.md").exists():
        working_dir = Path(".")

    try:
        import re
        backend = get_available_backend()
        # 根據 backend 組裝 fallback 指令
        if backend == "agy":
            cmd = ["agy", "-p", message, "--dangerously-skip-permissions", "--add-dir", str(working_dir.resolve())]
        elif backend == "claude":
            cmd = ["claude", "-p", message]
        else:
            cmd = ["kiro-cli", "chat", "--no-interactive", "--trust-all-tools", message]

        proc_sub = await asyncio.create_subprocess_exec(
            *cmd,
            cwd=str(working_dir),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await asyncio.wait_for(
            proc_sub.communicate(), timeout=timeout
        )
        if proc_sub.returncode != 0:
            return None
        output = stdout.decode("utf-8").strip()
        output = re.sub(r"\x1b\[[0-9;]*m", "", output)
        lines = [line for line in output.split("\n") if line.strip()]
        return "\n".join(lines) if lines else None
    except asyncio.TimeoutError:
        return None
    except Exception:
        return None
