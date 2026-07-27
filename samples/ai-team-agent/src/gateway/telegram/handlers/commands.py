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

async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    allowed = context.bot_data.get("allowed_users", [])
    access_hint = (
        f"\n\n⚠️ <b>你尚未在白名單中</b>\n"
        f"你的 Chat ID：<code>{uid}</code>\n"
        f"請在 team.yaml → access.allowed_users 加入此 ID"
    ) if allowed and uid not in allowed else ""
    text = (
        "🤖 <b>Ark Agent Platform</b>\n\n"
        "一個由 AI Agent 組成的專案團隊，常駐運行。\n"
        "你只需要用自然語言下達需求，團隊會自動分工完成。\n\n"
        "<b>團隊成員</b>\n"
        "⚙️ admin — 服務監控、成本控制\n"
        "🧠 pm — 需求分析、派工、驗收\n"
        "🤖 ai-dev — LLM / Agent / RAG\n"
        "💻 coder — 全端開發\n"
        "🧪 qa — 測試、品質保證\n"
        "📰 market — 市場研究\n"
        "📊 data — 數據分析\n"
        "📋 report — 報告產出\n\n"
        "<b>使用方式</b>\n"
        "• 直接打字 → leader-agent 接收並分派\n"
        "• /help → 查看所有指令\n\n"
        f"你的 Chat ID：<code>{uid}</code>"
        f"{access_hint}"
    )
    await update.message.reply_text(text, parse_mode="HTML")


# ── /help ──

async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "📖 <b>基本指令</b>（所有人）\n"
        "/start — 歡迎 + Chat ID\n"
        "/status — 團隊狀態\n"
        "/help — 本說明\n\n"
        "🔒 <b>進階功能</b>（需白名單）\n"
        "直接打字 → leader-agent 接收\n"
        "/agents — Agent 列表\n"
        "/board — 任務看板\n"
        "/costs — 費用追蹤\n"
        "/assign — 派工\n"
        "/restart — 重啟 agent\n"
        "/stop — 停止 agent\n"
    )
    await update.message.reply_text(text, parse_mode="HTML")


# ── /status ──

async def cmd_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    agents = await _get(context, "/api/agents")
    stats = await _get(context, "/api/admin/dashboard/stats")
    text = fmt_status(agents, stats)
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
