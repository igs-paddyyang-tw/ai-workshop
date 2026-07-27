"""Telegram 指令 handlers — slash 指令（含白名單權限）。"""
from __future__ import annotations

import functools
import httpx
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from gateway.telegram.formatters import fmt_status, fmt_board, fmt_costs, fmt_queue


def _api(context: ContextTypes.DEFAULT_TYPE) -> str:
    return context.bot_data.get("api_base", "http://127.0.0.1:33333")


def require_whitelist(fn):
    """白名單權限 decorator — 非白名單使用者顯示 ID 提示。"""
    @functools.wraps(fn)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        uid = update.effective_user.id
        allowed = context.bot_data.get("allowed_users", [])
        if allowed and uid not in allowed:
            await update.message.reply_text(
                f"🔒 需要權限。你的 ID：<code>{uid}</code>",
                parse_mode="HTML",
            )
            return
        return await fn(update, context)
    return wrapper


async def _get(context: ContextTypes.DEFAULT_TYPE, path: str) -> dict | list:
    async with httpx.AsyncClient(timeout=10) as c:
        r = await c.get(f"{_api(context)}{path}")
        return r.json()


async def _post(context: ContextTypes.DEFAULT_TYPE, path: str, data: dict) -> dict:
    async with httpx.AsyncClient(timeout=30) as c:
        r = await c.post(f"{_api(context)}{path}", json=data)
        return r.json()


# ── /start ──

APP_VERSION = "1.0.0"  # Platform version（kiro-cli 版本另外顯示）

async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    allowed = context.bot_data.get("allowed_users", [])
    is_authorized = not allowed or uid in allowed

    # Tier 資訊
    tier_status = context.bot_data.get("tier_status")
    tier_str = f"Tier {tier_status.tier}" if tier_status else "Tier ?"
    model_str = "auto"

    # 常駐 / 動態 agent 分類（從 daemon config）
    daemon = context.bot_data.get("persistent_daemon")
    persistent_names, dynamic_names = [], []
    if daemon:
        for name, ic in daemon.config.instances.items():
            (persistent_names if ic.persistent else dynamic_names).append(name)

    persistent_str = ", ".join(persistent_names) if persistent_names else "—"
    dynamic_count = len(dynamic_names)

    auth_line = (
        f"👤 Chat ID：<code>{uid}</code>  ✅ 已授權"
        if is_authorized else
        f"👤 Chat ID：<code>{uid}</code>  ⚠️ 未授權\n"
        f"   請將此 ID 加入 .env ALLOWED_USERS"
    )

    text = (
        f"🤖 <b>Ark Agent Platform</b>  <code>v{APP_VERSION}</code>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"📋 8-agent Team | {tier_str} | model: {model_str}\n"
        f"{auth_line}\n\n"
        f"<b>📌 系統摘要</b>\n"
        f"• 常駐：{persistent_str}\n"
        f"• 動態：{dynamic_count} workers（按需啟動）\n"
        f"• 指令入口：leader-agent\n\n"
        f"<b>🗣️ 使用方式</b>\n"
        f"• 直接打字 → leader-agent 分析並派工\n"
        f"• <code>@agent-name 訊息</code> → 指定特定 agent\n"
        f"• /help → 完整指令說明\n"
        f"• /status → 平台與 Agent 即時狀態"
    )
    await update.message.reply_text(text, parse_mode="HTML")


# ── /help ──

async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    allowed = context.bot_data.get("allowed_users", [])
    is_authorized = not allowed or uid in allowed

    basic = (
        "📖 <b>Ark Agent Platform 使用說明</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "🌐 <b>基本指令</b>（所有人）\n"
        "/start  — 系統資訊、版本、Chat ID\n"
        "/status — 平台狀態 + Agent 運行狀況\n"
        "/mode   — 查看當前 Tier 等級\n"
        "/help   — 本說明\n"
    )

    if not is_authorized:
        await update.message.reply_text(
            basic + f"\n🔒 進階功能需授權。你的 Chat ID：<code>{uid}</code>",
            parse_mode="HTML",
        )
        return

    advanced = (
        "\n🔒 <b>對話（授權後）</b>\n"
        "  直接打字           → leader-agent 接收分派\n"
        "  <code>@agent-name 訊息</code>  → 指定特定 agent\n\n"
        "📋 <b>任務管理</b>\n"
        "  /assign &lt;任務描述&gt;  → 建立任務並選指派對象\n"
        "  /board             → 看板（pending/doing/done）\n"
        "  /queue             → 待處理佇列\n\n"
        "🤖 <b>Agent 管理</b>\n"
        "  /agents            → Agent 列表（可點擊查詳情）\n"
        "  /logs &lt;agent_name&gt; → 最近執行記錄\n"
        "  /restart &lt;agent|all&gt; → 重啟 agent\n"
        "  /stop &lt;agent_name&gt;  → 停止 agent\n\n"
        "💰 <b>監控</b>\n"
        "  /costs             → 費用報告（今日/歷史）\n"
        "  /recall &lt;關鍵字&gt;   → 查詢 leader-agent 記憶\n"
    )
    await update.message.reply_text(basic + advanced, parse_mode="HTML")


# ── /status ──

async def cmd_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    import time as _time

    # ── 平台區塊 ──
    stats = await _get(context, "/api/admin/dashboard/stats")
    health = await _get(context, "/api/health")
    scheduler_ok = stats.get("active_agents", 0) > 0

    cost_today = stats.get("total_cost_today_usd", 0)
    cost_limit = 15.0  # fallback
    try:
        budget = await _get(context, "/api/admin/costs/budget")
        if isinstance(budget, dict):
            cost_limit = budget.get("daily_limit_usd", cost_limit)
    except Exception:
        pass

    api_status = "🟢 正常" if health.get("status") == "ok" else "🔴 異常"

    platform_lines = [
        "⚙️ <b>平台狀態</b>",
        "━━━━━━━━━━━━━━━━━━━",
        f"🟢 API      port 33333 | {api_status}",
        f"🟢 TG Bot   已連線",
        f"{'🟢' if scheduler_ok else '🔴'} Scheduler  {'運行中' if scheduler_ok else '停止'}",
        f"💰 今日費用 ${cost_today:.3f} / ${cost_limit:.1f}",
    ]

    # ── Agent 區塊 ──
    agents = await _get(context, "/api/agents")
    runtime_data = await _get(context, "/api/agents/runtime/status")
    runtime_map = {}
    if isinstance(runtime_data, dict):
        for inst in runtime_data.get("instances", []):
            runtime_map[inst["name"]] = inst

    role_icon = {"admin": "⚙️", "leader": "🧠", "worker": "💻"}
    status_icon = {"idle": "🟢", "busy": "🔵", "running": "🟢", "crashed": "🔴", "stopped": "⏸️", "starting": "🟡"}

    persistent_lines = []
    dynamic_lines = []

    for a in agents:
        name = a["id"]
        role = a.get("role", "worker")
        mode = a.get("mode", "spawn")
        r_icon = role_icon.get(role, "💻")
        rt = runtime_map.get(name, {})
        rt_status = rt.get("status", a.get("status", "idle"))
        s_icon = status_icon.get(rt_status, "⚪")

        if mode == "persistent":
            uptime_s = rt.get("uptime_seconds", 0)
            mem_mb = rt.get("memory_mb", 0)
            if uptime_s > 0:
                h, m = int(uptime_s // 3600), int((uptime_s % 3600) // 60)
                uptime_str = f"{h}h{m:02d}m" if h > 0 else f"{m}m"
            else:
                uptime_str = "—"
            mem_str = f"{mem_mb:.0f}MB" if mem_mb > 0 else "—"
            persistent_lines.append(
                f"  {r_icon} {name:<16} {s_icon} {rt_status:<8} {uptime_str:>6} | {mem_str}"
            )
        else:
            s_icon_dyn = "⏸️" if rt_status == "stopped" else s_icon
            st_str = "待機" if rt_status == "stopped" else rt_status
            dynamic_lines.append(f"  {r_icon} {name:<16} {s_icon_dyn} {st_str}")

    agent_lines = ["", "🤖 <b>Agent 狀態</b>", "━━━━━━━━━━━━━━━━━━━"]
    if persistent_lines:
        agent_lines.append(f"<b>常駐（{len(persistent_lines)}）</b>")
        agent_lines.extend(persistent_lines)
    if dynamic_lines:
        agent_lines.append(f"<b>動態（{len(dynamic_lines)}）</b>")
        agent_lines.extend(dynamic_lines)

    # ── 任務摘要 ──
    completed = stats.get("completed_today", 0)
    running = stats.get("running_tasks", 0)
    task_line = f"\n📊 今日　完成 {completed} | 進行中 {running}"

    text = "\n".join(platform_lines + agent_lines) + task_line
    await update.message.reply_text(text, parse_mode="HTML")


# ── /agents ──

@require_whitelist
async def cmd_agents(update: Update, context: ContextTypes.DEFAULT_TYPE):
    agents = await _get(context, "/api/agents")
    if not agents:
        await update.message.reply_text("尚無 Agent")
        return
    buttons = []
    for a in agents:
        icon = {"idle": "🟢", "busy": "🔵", "offline": "🔴"}.get(a.get("status", "idle"), "⚪")
        buttons.append([InlineKeyboardButton(
            f"{icon} {a['name']} ({a['role']})",
            callback_data=f"agent_detail:{a['id']}"
        )])
    await update.message.reply_text(
        "🤖 <b>Agent 列表</b>（點擊查看詳情）",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(buttons),
    )


# ── /board ──

@require_whitelist
async def cmd_board(update: Update, context: ContextTypes.DEFAULT_TYPE):
    board = await _get(context, "/api/board")
    sections = []
    icons = {"queued": "🔵", "claimed": "🟡", "executing": "🟢", "blocked": "🔴", "failed": "❌"}
    for status, icon in icons.items():
        tasks = board.get(status, [])
        if tasks:
            lines = [f"{icon} <b>{status.upper()}</b> ({len(tasks)})"]
            for t in tasks[:5]:
                assignee = t.get("assignee") or "unassigned"
                lines.append(f"  • [{t['id'][:10]}] {t['title'][:30]} → @{assignee}")
            sections.append("\n".join(lines))
    completed_today = len(board.get("completed", []))
    sections.append(f"✅ COMPLETED today: {completed_today}")
    text = "📋 <b>任務看板</b>\n\n" + "\n\n".join(sections) if sections else "📋 看板為空"
    kb = InlineKeyboardMarkup([[
        InlineKeyboardButton("➕ 新任務", callback_data="new_issue"),
        InlineKeyboardButton("🔄 重新整理", callback_data="refresh_board"),
    ]])
    await update.message.reply_text(text, parse_mode="HTML", reply_markup=kb)


# ── /costs ──

@require_whitelist
async def cmd_costs(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # /api/admin/costs 回傳 {total_usd, total_records, by_agent, by_model}
    data = await _get(context, "/api/admin/costs")
    # 若回傳的是 error dict（端點不存在時 FastAPI 回 {"detail":"..."}），fallback 到空資料
    if "detail" in data or "error" in data:
        data = {"total_usd": 0, "total_records": 0, "by_agent": {}, "by_model": {}}
    text = fmt_costs(data)
    await update.message.reply_text(text, parse_mode="HTML")


# ── /queue ──

@require_whitelist
async def cmd_queue(update: Update, context: ContextTypes.DEFAULT_TYPE):
    issues = await _get(context, "/api/admin/queue")
    text = fmt_queue(issues)
    kb = InlineKeyboardMarkup([[
        InlineKeyboardButton("🎯 批量指派", callback_data="batch_assign"),
    ]]) if issues else None
    await update.message.reply_text(text, parse_mode="HTML", reply_markup=kb)


# ── /assign ──

@require_whitelist
async def cmd_assign(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.replace("/assign", "").strip()
    if not text:
        await update.message.reply_text("用法：/assign 任務描述\n例如：/assign 建立 REST API")
        return

    # 先建立 Issue
    issue = await _post(context, "/api/issues", {"title": text})

    # 顯示 Agent 選擇
    agents = await _get(context, "/api/agents")
    buttons = [[InlineKeyboardButton(
        f"{a['name']}", callback_data=f"assign:{issue['id']}:{a['id']}"
    )] for a in agents if a.get("role") != "admin"]
    buttons.append([InlineKeyboardButton("🤖 自動判斷", callback_data=f"assign:{issue['id']}:auto")])

    await update.message.reply_text(
        f"📋 已建立 <b>#{issue['id']}</b> — {text}\n\n指派給誰？",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(buttons),
    )


# ── /stop ──

@require_whitelist
async def cmd_stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    arg = update.message.text.replace("/stop", "").strip()
    if not arg:
        await update.message.reply_text("用法：/stop agent_name")
        return
    kb = InlineKeyboardMarkup([[
        InlineKeyboardButton("⚠️ 確認中斷", callback_data=f"stop_confirm:{arg}"),
        InlineKeyboardButton("取消", callback_data="cancel"),
    ]])
    await update.message.reply_text(f"確定要中斷 <b>{arg}</b>？", parse_mode="HTML", reply_markup=kb)


# ── /retry ──

@require_whitelist
async def cmd_retry(update: Update, context: ContextTypes.DEFAULT_TYPE):
    arg = update.message.text.replace("/retry", "").strip()
    if not arg:
        await update.message.reply_text("用法：/retry task_id")
        return
    async with httpx.AsyncClient(timeout=10) as c:
        r = await c.patch(f"{_api(context)}/api/tasks/{arg}/retry",
                          json={"actor": str(update.effective_user.id)})
        if r.status_code == 200:
            await update.message.reply_text(f"🔄 任務 {arg} 已重新排入佇列")
        else:
            await update.message.reply_text(f"❌ 無法重試：{r.json().get('detail', 'unknown')}")


# ── /unblock ──

async def cmd_unblock(update: Update, context: ContextTypes.DEFAULT_TYPE):
    arg = update.message.text.replace("/unblock", "").strip()
    if not arg:
        await update.message.reply_text("用法：/unblock task_id")
        return
    async with httpx.AsyncClient(timeout=10) as c:
        r = await c.patch(f"{_api(context)}/api/tasks/{arg}/unblock",
                          json={"actor": str(update.effective_user.id)})
        if r.status_code == 200:
            await update.message.reply_text(f"✅ 任務 {arg} 已解除阻礙，重新排入佇列")
        else:
            await update.message.reply_text(f"❌ 無法 unblock：{r.json().get('detail', 'unknown')}")


# ── /runtimes ──

async def cmd_runtimes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = await _get(context, "/api/runtimes")
    if not data:
        await update.message.reply_text("⚠️ 無可用 Runtime")
        return
    icons = {"available": "🟢", "busy": "🔵", "unavailable": "🔴"}
    lines = ["🖥️ <b>Runtime 狀態</b>\n"]
    for rt in data:
        icon = icons.get(rt.get("status", ""), "⚪")
        lines.append(f"{icon} {rt['provider']} ({rt['cli_command']}) — {rt['status']}")
    await update.message.reply_text("\n".join(lines), parse_mode="HTML")


# ── /logs ──

@require_whitelist
async def cmd_logs(update: Update, context: ContextTypes.DEFAULT_TYPE):
    arg = update.message.text.replace("/logs", "").strip()
    if not arg:
        await update.message.reply_text("用法：/logs agent_name")
        return
    sessions = await _get(context, f"/api/admin/sessions?agent_id={arg}&limit=3")
    if not sessions:
        await update.message.reply_text(f"📝 {arg} 尚無執行記錄")
        return
    lines = [f"📝 <b>{arg} 最近記錄</b>\n"]
    for s in sessions[:3]:
        output = (s.get("output") or "")[:200]
        lines.append(f"• {s.get('started_at', '')[:16]} — {output or '(無輸出)'}")
    await update.message.reply_text("\n".join(lines), parse_mode="HTML")



# ── /restart ──

@require_whitelist
async def cmd_restart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """重啟 agent 或平台（常駐模式走 API rotate，spawn 模式走本地物件）。"""
    arg = update.message.text.replace("/restart", "").strip()
    if not arg:
        await update.message.reply_text("用法：/restart <agent_name|all|platform>")
        return

    if arg == "platform":
        await update.message.reply_text("🔄 平台重啟中...")
        from pathlib import Path
        Path("restart.flag").touch()
        import sys
        sys.exit(0)

    if arg == "all":
        # 取得所有 agent id 再逐一 rotate
        agents_list = await _get(context, "/api/agents")
        if isinstance(agents_list, list):
            failed = []
            for a in agents_list:
                r = await _post(context, f"/api/agents/{a['id']}/rotate", {})
                if not r.get("rotated"):
                    failed.append(a["id"])
            msg = f"✅ 已重啟全部 {len(agents_list)} 個 Agent"
            if failed:
                msg += f"\n⚠️ 失敗：{', '.join(failed)}"
        else:
            msg = "❌ 無法取得 Agent 列表"
        await update.message.reply_text(msg)
        return

    # 單一 agent：優先走 POST /api/agents/{id}/rotate
    r = await _post(context, f"/api/agents/{arg}/rotate", {})
    if "detail" in r:
        # API 回 404：agent 不存在
        await update.message.reply_text(f"❌ 找不到 Agent: {arg}")
    elif r.get("rotated") is False:
        await update.message.reply_text(f"⚠️ {arg} rotate 失敗（可能非常駐模式）")
    else:
        await update.message.reply_text(f"✅ 已重啟 {arg}")
