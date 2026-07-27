"""Ark Agent Platform — 啟動邏輯。

啟動順序：DB + EventBus → Backend API → Agents → A2A Router → TG Bot → Scheduler
"""
from __future__ import annotations

import asyncio
import logging
import os
import time
from pathlib import Path

# 載入 .env
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


async def main() -> None:
    # Logging
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    fmt = "%(asctime)s [%(name)s] %(levelname)s %(message)s"
    logging.basicConfig(
        level=logging.INFO,
        format=fmt,
        handlers=[
            logging.FileHandler(log_dir / "platform.log", encoding="utf-8"),
            logging.StreamHandler(),
        ],
    )
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("uvicorn").setLevel(logging.WARNING)
    log = logging.getLogger("platform")

    # ── Tier 偵測 ──
    from runtime.tier import detect_tier, print_tier_banner
    tier_status = detect_tier()
    print_tier_banner(tier_status)

    # ── 1. DB + EventBus ──
    from coordinator.db.models import init_db, get_async_db, fetch_one, insert, now_iso
    from coordinator.events.bus import EventBus
    from coordinator.events.types import EventType, Event
    from coordinator.services.cost_tracker import on_agent_output
    from coordinator.services.audit_logger import on_any_event

    await init_db()

    # Sync team.yaml agents → DB
    from runtime.config import load_config as _lc
    _tc = _lc("team.yaml")
    _conn = await get_async_db()
    for _name, _ic in _tc.instances.items():
        existing = await fetch_one(_conn, "SELECT id FROM agents WHERE id=?", (_name,))
        if not existing:
            await insert(_conn, "agents", {
                "id": _name, "name": _name, "role": _ic.role,
                "provider": "kiro-cli", "working_dir": _ic.working_directory,
                "model": _ic.model or 'auto',
                "status": "idle", "created_at": now_iso(), "updated_at": now_iso(),
            })
    await _conn.close()

    bus = EventBus()
    bus.subscribe(EventType.AGENT_OUTPUT, on_agent_output)
    for et in EventType:
        bus.subscribe(et, on_any_event)

    # ── Memory 子系統 ──
    from coordinator.memory.daily_log import write_daily_log
    from coordinator.memory.indexer import rebuild_memory_index

    async def _on_agent_output_memory(event: Event):
        """AGENT_OUTPUT → daily_log 自動寫入。"""
        data = event.data
        agent_name = data.get("agent_id") or data.get("agent", "")
        output = data.get("output", "")
        if not agent_name or not output or len(output) < 20:
            return
        try:
            await write_daily_log(
                agent_name=agent_name,
                task_id=data.get("task_id", "auto"),
                conversation=output[:3000],
            )
            await bus.emit(Event(
                type=EventType.MEMORY_WRITTEN,
                data={"agent": agent_name},
            ))
        except Exception as e:
            log.warning("Memory write failed: %s", e)

    bus.subscribe(EventType.AGENT_OUTPUT, _on_agent_output_memory)

    # 啟動時重建記憶索引
    try:
        count = await rebuild_memory_index()
        if count > 0:
            log.info("Memory index: %d entries indexed", count)
    except Exception as e:
        log.warning("Memory index rebuild failed: %s", e)

    await bus.start()
    log.info("DB + EventBus + Memory 已啟動")

    # ── 1b. Skills 框架 ──
    from business.skills import SkillRegistry, SkillTracker

    skill_tracker = SkillTracker()
    skill_registry = SkillRegistry(tracker=skill_tracker)
    skill_count = skill_registry.auto_discover("business.skills.internal")
    log.info("Skills: %d loaded", skill_count)

    # ── 1c. GrowthDetector 已移除（需 Gemini LLM，非必要功能）──

    # ── 2. Backend API ──
    import uvicorn
    from gateway.api.router import app
    app.state.bus = bus
    app.state._external_bus = True

    api_port = int(os.environ.get("API_PORT", "33333"))
    config = uvicorn.Config(app, host="127.0.0.1", port=api_port, log_level="warning")
    server = uvicorn.Server(config)
    api_task = asyncio.create_task(server.serve())
    await asyncio.sleep(1)
    log.info("Backend API 已啟動 (port %d)", api_port)

    # ── 3. Agent Daemon ──
    from runtime.config import load_config
    from runtime.process import AgentProcess

    team_config = load_config("team.yaml")
    agents: dict[str, AgentProcess] = {}

    # === 常駐模式 ===
    persistent_daemon = None
    if team_config.persistent:
        from runtime.persistent_daemon import PersistentDaemon
        persistent_daemon = PersistentDaemon(config_path="team.yaml")
        app.state.persistent_daemon = persistent_daemon
        log.info("使用常駐模式 (PersistentDaemon)")

    # TG reply callback（稍後設定）
    tg_reply_fn = None
    _tg_handled_agents: set[str] = set()  # agents currently handled by TG handler directly

    import re
    _ANSI_RE = re.compile(r"\x1b\[[0-9;]*m|\x1b\[\?[0-9]*[hl]|\x1b\[[0-9]*[A-Z]")

    def _clean_output(text: str) -> str:
        """Strip ANSI codes + kiro-cli prompt markers."""
        text = _ANSI_RE.sub("", text)
        # Remove leading '> ' prompt marker per line
        lines = [l.lstrip("> ") if l.startswith("> ") else l for l in text.splitlines()]
        return "\n".join(lines).strip()

    _DONE_RE = re.compile(r"\[DONE\]\s*summary=(.+?)(?:\s+artifacts=\S+)?$", re.MULTILINE)
    _NOISE_PREFIXES = ("Reading file", "using tool", "Searching", "Looking at",
                       "Let me", "I'll ", "Now I", "Checking", "Found ", "───")

    def _summarize_for_tg(agent_name: str, text: str) -> str:
        """從 output 提取精簡摘要（≤200 字）供 TG 發送。"""
        # 優先使用 [DONE] marker
        m = _DONE_RE.search(text)
        if m:
            return f"✅ {agent_name}: {m.group(1).strip()}"
        # Fallback: 取最後幾行非雜訊內容
        lines = [l for l in text.splitlines()
                 if l.strip() and not any(l.strip().startswith(p) for p in _NOISE_PREFIXES)]
        tail = "\n".join(lines[-3:]) if lines else text[-200:]
        summary = tail[:200]
        return f"📋 {agent_name}:\n{summary}"

    async def _on_agent_output(agent_name: str, text: str, usage=None):
        text = _clean_output(text)
        if not text:
            return
        # 記錄 session
        import uuid
        from coordinator.db.models import get_async_db as _get_db, insert as _insert, now_iso as _now
        conn = await _get_db()
        try:
            # 用實際 token 數計算 cost
            if usage:
                total_tokens = usage.input_tokens + usage.output_tokens
                cost_usd = usage.input_tokens * 0.003 / 1000 + usage.output_tokens * 0.015 / 1000
            else:
                total_tokens = len(text) // 4
                cost_usd = total_tokens * 0.003 / 1000
            await _insert(conn, "agent_sessions", {
                "id": str(uuid.uuid4())[:8],
                "agent_id": agent_name,
                "status": "completed",
                "started_at": _now(),
                "ended_at": _now(),
                "total_tokens": total_tokens,
                "cost_usd": round(cost_usd, 6),
                "output": text[:2000],
            })
        except Exception:
            pass
        finally:
            await conn.close()
        # 常駐模式：回覆由 MCP reply() tool 驅動，不再從 stdout 推 TG
        # spawn 模式：沒有 MCP，仍需 callback 推 TG
        if not persistent_daemon and tg_reply_fn and agent_name not in _tg_handled_agents:
            await tg_reply_fn(agent_name, _summarize_for_tg(agent_name, text))

    # === 啟動 agents ===
    if persistent_daemon:
        # 常駐模式：用 PersistentDaemon 啟動所有 agent
        log.info("啟動 %d agents（常駐模式）...", len(team_config.instances))
        results = await persistent_daemon.start_all()
        for name, ok in results.items():
            if ok:
                log.info("  ✅ %s", name)
            else:
                log.error("  ❌ %s 啟動失敗", name)
        log.info("常駐 agents 已就緒 (%d/%d)", sum(results.values()), len(results))
    else:
        # Spawn 模式（fallback）：維持現有行為
        log.info("啟動 %d agents（spawn 模式）...", len(team_config.instances))
        for name, ic in team_config.instances.items():
            agent_cwd = Path(ic.working_directory).resolve()
            agent_cwd.mkdir(parents=True, exist_ok=True)
            proc = AgentProcess(
                name=name, working_dir=ic.working_directory,
                model=ic.model, skip_resume=ic.skip_resume,
                backend=ic.backend,
            )
            proc.timeout = team_config.timeout_seconds
            proc.on_output = _on_agent_output
            proc.event_bus = bus
            agents[name] = proc
            await proc.start()
            await asyncio.sleep(1)
        log.info("所有 agents 已就緒 (%d)", len(agents))

    # ── 3b. A2A Router + Task Dispatcher ──
    from coordinator.a2a.router import A2ARouter
    from coordinator.a2a.graph import TaskGraph
    from coordinator.a2a.shared_memory import SharedMemory
    from coordinator.a2a.discovery import AgentDiscovery
    from coordinator.a2a.protocol import TaskHandoff

    graph = TaskGraph()
    memory = SharedMemory()
    discovery = AgentDiscovery(memory)

    async def _spawn_fn(agent_name: str, message: str) -> str | None:
        if persistent_daemon:
            ok = await persistent_daemon.send_message(agent_name, message)
            return "queued" if ok else None
        agent = agents.get(agent_name)
        if not agent:
            log.warning("spawn_fn: unknown agent %s", agent_name)
            return None
        return await agent.send(message)

    router = A2ARouter(graph, memory, discovery, spawn_fn=_spawn_fn)

    # 任務完成/失敗時更新 DB issue 狀態
    _original_on_complete = router.on_complete
    _original_on_failed = router.on_failed

    async def _on_complete_with_db(task_id: str, output: str) -> None:
        await _original_on_complete(task_id, output)
        conn = get_db()
        conn.execute(
            "UPDATE issues SET status=?, completed_at=?, updated_at=? WHERE id=?",
            ("completed", now_iso(), now_iso(), task_id))
        conn.commit()

    async def _on_failed_with_db(task_id: str, reason: str) -> None:
        await _original_on_failed(task_id, reason)
        conn = get_db()
        conn.execute(
            "UPDATE issues SET status=?, updated_at=? WHERE id=?",
            ("failed", now_iso(), task_id))
        conn.commit()

    router.on_complete = _on_complete_with_db
    router.on_failed = _on_failed_with_db

    async def _on_task_assigned(event: Event):
        """Issue 被指派後，建立 TaskHandoff → router.dispatch()。"""
        data = event.data
        assignee = data.get("assignee", "")
        issue_id = data.get("issue_id", "")
        if not assignee:
            log.warning("Task %s has no assignee", issue_id)
            return
        conn = get_db()
        issue = fetch_one(conn, "SELECT title, description, priority FROM issues WHERE id=?", (issue_id,))
        if not issue:
            return

        handoff = TaskHandoff(
            task_id=issue_id,
            from_agent="platform",
            to_agent=assignee,
            title=issue["title"],
            context=issue.get("description") or "",
            priority=issue.get("priority") or 3,
            depends_on=data.get("depends_on", []),
        )
        log.info("Dispatching issue %s to %s via A2ARouter: %s", issue_id, assignee, issue["title"][:60])
        await router.dispatch(handoff)

    bus.subscribe(EventType.TASK_ASSIGNED, _on_task_assigned)

    # ── 3c. SYSTEM_RESTART handler + Circuit Breaker ──
    import time as _time
    _restart_history: dict[str, list[float]] = {}
    _circuit_open: set[str] = set()

    async def _on_system_restart(event: Event):
        aid = event.data.get("agent_id", "")
        if persistent_daemon:
            await persistent_daemon.restart_instance(aid)
            log.info("Restarted agent %s (persistent)", aid)
            return
        agent = agents.get(aid)
        if not agent:
            return
        # Circuit Breaker: 5 分鐘內 >3 次 → 熔斷
        now = _time.time()
        history = _restart_history.setdefault(aid, [])
        history[:] = [t for t in history if now - t < 300]
        if len(history) >= 3:
            if aid not in _circuit_open:
                _circuit_open.add(aid)
                log.error("Circuit OPEN for %s (>3 restarts in 5min)", aid)
                if tg_reply_fn:
                    await tg_reply_fn(aid, f"⚠️ {aid} 熔斷：5 分鐘內重啟超過 3 次，已暫停")
            return
        if agent._busy:
            return
        history.append(now)
        await agent.start()
        log.info("Restarted agent %s", aid)

    bus.subscribe(EventType.SYSTEM_RESTART, _on_system_restart)

    # ── 4. Telegram Bot ──
    tg_app = None
    notify_service = None
    token = os.environ.get("TELEGRAM_BOT_TOKEN", "")
    if token:
        from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, filters
        from telegram import BotCommand

        tg_app = ApplicationBuilder().token(token).build()
        tg_app.bot_data["api_base"] = f"http://127.0.0.1:{api_port}"
        tg_app.bot_data["agents"] = agents
        tg_app.bot_data["persistent_daemon"] = persistent_daemon
        tg_app.bot_data["handled_agents"] = _tg_handled_agents
        tg_app.bot_data["skill_registry"] = skill_registry
        tg_app.bot_data["tier_status"] = tier_status  # 供 /mode 使用（解耦 runtime.tier 直接 import）

        # 註冊 handlers
        from gateway.telegram.handlers.commands import (
            cmd_start, cmd_status, cmd_agents, cmd_board, cmd_costs,
            cmd_queue, cmd_assign, cmd_stop, cmd_retry, cmd_logs, cmd_help,
            cmd_restart,
        )
        from gateway.telegram.handlers.callbacks import handle_callback
        from gateway.telegram.handlers.messages import handle_message
        from gateway.telegram.handlers.memory_commands import (
            cmd_recall, cmd_consolidate, cmd_skills, cmd_mode,
        )

        for name_cmd, fn in [
            ("start", cmd_start), ("status", cmd_status), ("agents", cmd_agents),
            ("board", cmd_board), ("costs", cmd_costs), ("queue", cmd_queue),
            ("assign", cmd_assign), ("stop", cmd_stop), ("retry", cmd_retry),
            ("logs", cmd_logs), ("help", cmd_help), ("restart", cmd_restart),
            ("recall", cmd_recall), ("consolidate", cmd_consolidate),
            ("skills", cmd_skills), ("mode", cmd_mode),
        ]:
            tg_app.add_handler(CommandHandler(name_cmd, fn))
        tg_app.add_handler(CallbackQueryHandler(handle_callback))
        tg_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
        tg_app.add_handler(MessageHandler(filters.COMMAND, handle_message))  # catch unregistered /commands

        async def _tg_error(update, context):
            log.error("TG handler error: %s", context.error)
        tg_app.add_error_handler(_tg_error)

        await tg_app.initialize()
        await tg_app.bot.set_my_commands([
            BotCommand("start", "歡迎"),
            BotCommand("status", "團隊狀態"),
            BotCommand("help", "使用說明"),
        ])
        await tg_app.start()
        await tg_app.updater.start_polling(drop_pending_updates=True)

        # 設定 reply callback
        # 優先從 .env ALLOWED_USERS 讀取（逗號分隔 int list），其次 team.yaml
        env_users_raw = os.environ.get("ALLOWED_USERS", "")
        if env_users_raw:
            allowed_users = [int(u.strip()) for u in env_users_raw.split(",") if u.strip().isdigit()]
        else:
            allowed_users = team_config.access.get("allowed_users", [])
        tg_app.bot_data["allowed_users"] = allowed_users
        chat_id = allowed_users[0] if allowed_users else 0
        if not allowed_users:
            log.warning("⚠️  team.yaml access.allowed_users 為空！任何人都能傳訊給 Bot，請填入你的 Telegram user_id")
        else:
            log.info("allowed_users: %s", allowed_users)

        AGENT_TITLES = {
            "admin-agent": "👑 管理員",
            "pm-agent": "🧠 專案經理",
            "ai-dev-agent": "🤖 AI工程師",
            "coder-agent": "💻 工程師",
            "qa-agent": "🧪 測試工程師",
        }

        async def _tg_reply(agent_name: str, text: str):
            if chat_id:
                try:
                    title = AGENT_TITLES.get(agent_name, agent_name)
                    msg = f"{title}\n{text}"
                    await tg_app.bot.send_message(chat_id=chat_id, text=msg[:250])
                except Exception as e:
                    log.warning("TG reply failed: %s", e)

        tg_reply_fn = _tg_reply

        # ── 設定 Chat Channel（TG）──
        from gateway.api.chat import TelegramChannel, set_channel

        tg_channel = TelegramChannel()
        tg_channel.configure(
            bot=tg_app.bot,
            chat_id=chat_id,
            allowed_chat_ids=allowed_users,
        )
        set_channel(tg_channel)

        # NotificationService
        if chat_id:
            from gateway.telegram.notifications import NotificationService
            notify_service = NotificationService(tg_app, [chat_id])
            notify_service.subscribe_to(bus)

        log.info("Telegram Bot 已啟動")
    else:
        log.info("無 TELEGRAM_BOT_TOKEN，跳過 Bot")

    # ── 5. Scheduler ──
    try:
        from runtime.scheduler import Scheduler

        async def _send_to(instance: str, message: str) -> bool:
            if persistent_daemon:
                return await persistent_daemon.send_message(instance, message)
            agent = agents.get(instance)
            if agent:
                asyncio.create_task(agent.send(message))
                return True
            return False

        scheduler = Scheduler(send_fn=_send_to, event_bus=bus)
        count = scheduler.load_yaml("scheduler.yaml")
        if count > 0:
            scheduler.start()
            log.info("Scheduler 已啟動 (%d jobs)", count)
    except Exception as e:
        log.info("Scheduler 未啟動: %s", e)

    # ── 主迴圈 ──
    log.info("✅ Ark Agent Platform 全部服務已啟動")
    try:
        while True:
            await asyncio.sleep(30)
    except (asyncio.CancelledError, KeyboardInterrupt):
        pass
    finally:
        log.info("Shutting down (graceful, timeout=30s)...")

        if persistent_daemon:
            # 常駐模式：PersistentDaemon 負責 graceful stop
            await persistent_daemon.stop_all()
        else:
            # Spawn 模式：設 shutdown flag → 等待 busy → kill
            AgentProcess._shutting_down = True
            deadline = asyncio.get_event_loop().time() + 30
            busy_agents = [name for name, proc in agents.items() if proc._busy]
            if busy_agents:
                log.info("Waiting for busy agents: %s", busy_agents)
            while any(proc._busy for proc in agents.values()):
                if asyncio.get_event_loop().time() > deadline:
                    still_busy = [n for n, p in agents.items() if p._busy]
                    log.warning("Timeout! Force killing busy agents: %s", still_busy)
                    break
                await asyncio.sleep(0.5)
            for proc in agents.values():
                await proc.kill()

        # Drain EventBus queue
        await bus.drain()

        # 關閉服務
        if tg_app:
            await tg_app.updater.stop()
            await tg_app.stop()
            await tg_app.shutdown()
        await bus.stop()
        server.should_exit = True
        log.info("Graceful shutdown complete.")
