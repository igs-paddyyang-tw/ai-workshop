"""InlineKeyboard callback 處理。"""
from __future__ import annotations

import httpx
from telegram import Update
from telegram.ext import ContextTypes


def _api(context: ContextTypes.DEFAULT_TYPE) -> str:
    return context.bot_data.get("api_base", "http://127.0.0.1:33333")


async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "cancel":
        await query.edit_message_text("❌ 已取消")

    elif data.startswith("assign:"):
        # assign:issue_id:agent_id
        parts = data.split(":")
        issue_id, agent_id = parts[1], parts[2]
        if agent_id == "auto":
            # 自動選第一個 worker
            async with httpx.AsyncClient(timeout=10) as c:
                r = await c.get(f"{_api(context)}/api/agents")
                agents = r.json()
            workers = [a for a in agents if a.get("role") == "worker"]
            agent_id = workers[0]["id"] if workers else ""

        if agent_id:
            async with httpx.AsyncClient(timeout=10) as c:
                await c.patch(f"{_api(context)}/api/issues/{issue_id}/assign",
                              json={"assignee": agent_id})
            await query.edit_message_text(
                f"✅ 已指派 <b>#{issue_id}</b> → {agent_id}\n⏳ 開始執行...",
                parse_mode="HTML",
            )
        else:
            await query.edit_message_text("⚠️ 無可用 Agent")

    elif data.startswith("stop_confirm:"):
        agent_name = data.split(":", 1)[1]
        # 實際呼叫 API 停止常駐 agent（persistent=false）
        async with httpx.AsyncClient(timeout=10) as c:
            r = await c.patch(
                f"{_api(context)}/api/agents/{agent_name}/persistent",
                json={"persistent": False},
            )
        if r.status_code == 200:
            result = r.json()
            status = result.get("status", "unknown")
            await query.edit_message_text(
                f"⏹️ <b>{agent_name}</b> 已停止（status: {status}）",
                parse_mode="HTML",
            )
        elif r.status_code == 400:
            # 非常駐模式：emit AGENT_STOPPED via bus（通知機制）
            await query.edit_message_text(
                f"⏹️ {agent_name}：非常駐模式，已發送停止指令",
            )
        else:
            await query.edit_message_text(
                f"⚠️ 停止失敗：{r.status_code}",
            )

    elif data.startswith("agent_detail:"):
        agent_id = data.split(":", 1)[1]
        async with httpx.AsyncClient(timeout=10) as c:
            r = await c.get(f"{_api(context)}/api/agents/{agent_id}")
        if r.status_code == 200:
            a = r.json()
            text = (
                f"🤖 <b>{a['name']}</b>\n\n"
                f"角色: {a['role']}\n"
                f"Provider: {a['provider']}\n"
                f"狀態: {a['status']}\n"
                f"模型: {a['model']}\n"
                f"目錄: {a['working_dir']}"
            )
            await query.edit_message_text(text, parse_mode="HTML")

    elif data == "refresh_board":
        # 改用 /api/board（回傳 kanban 分組格式）而非 /api/issues（flat list）
        async with httpx.AsyncClient(timeout=10) as c:
            r = await c.get(f"{_api(context)}/api/board")
        board = r.json() if r.status_code == 200 else {}
        # board 是 {pending:[...], assigned:[...], completed:[...]} 格式
        # 轉成 fmt_board 接受的 flat list
        from gateway.telegram.formatters import fmt_board
        flat = []
        for status_key, items in board.items():
            if isinstance(items, list):
                for item in items:
                    if isinstance(item, dict) and "status" not in item:
                        item = {**item, "status": status_key}
                    flat.append(item)
        await query.edit_message_text(fmt_board(flat), parse_mode="HTML")

    elif data == "new_issue":
        await query.edit_message_text("請用 /assign 描述 來建立新任務")

    # ── Skill 審批 callbacks ──

    elif data.startswith("skill_approve:"):
        proposal_id = data.split(":", 1)[1]
        growth = context.bot_data.get("growth_detector")
        if growth:
            ok = await growth.approve(proposal_id)
            if ok:
                await query.edit_message_text(f"✅ Skill 已核准並落地 (id={proposal_id})")
            else:
                await query.edit_message_text(f"⚠️ 核准失敗：找不到提案 {proposal_id}")
        else:
            await query.edit_message_text("⚠️ 自我成長系統未啟動")

    elif data.startswith("skill_reject:"):
        proposal_id = data.split(":", 1)[1]
        growth = context.bot_data.get("growth_detector")
        if growth:
            ok = await growth.reject(proposal_id)
            if ok:
                await query.edit_message_text(f"❌ Skill 已駁回 (id={proposal_id})")
            else:
                await query.edit_message_text(f"⚠️ 駁回失敗：找不到提案 {proposal_id}")
        else:
            await query.edit_message_text("⚠️ 自我成長系統未啟動")
