"""自然語言路由 — 白名單 + typing 狀態 + reaction 回饋 + trace log。"""
from __future__ import annotations

import asyncio
import logging
import re
import time

from telegram import ReactionTypeEmoji, Update
from telegram.ext import ContextTypes

log = logging.getLogger(__name__)

# ── 追蹤進行中的訊息（message_id → context）──
_pending_messages: dict[int, dict] = {}


async def _set_reaction(msg, emoji: str) -> None:
    try:
        await msg.set_reaction(reaction=[ReactionTypeEmoji(emoji=emoji)])
    except Exception:
        pass


async def _typing_loop(chat_id: int, message_id: int, bot) -> None:
    """每 4 秒發送 typing action，直到被 cancel。"""
    try:
        while True:
            await bot.send_chat_action(chat_id=chat_id, action="typing")
            await asyncio.sleep(4)
    except asyncio.CancelledError:
        pass


async def complete_message(message_id: int, success: bool = True) -> None:
    """agent reply 後呼叫：停止 typing + 更新 reaction。"""
    ctx = _pending_messages.pop(message_id, None)
    if not ctx:
        return
    task = ctx.get("typing_task")
    if task and not task.done():
        task.cancel()
    msg = ctx.get("msg")
    if msg:
        await _set_reaction(msg, "👍" if success else "👎")


async def complete_by_chat(chat_id: int, success: bool = True) -> None:
    """依 chat_id 找到最近的 pending message 並完成。"""
    target_mid = None
    for mid, ctx in _pending_messages.items():
        if ctx.get("chat_id") == chat_id:
            target_mid = mid
    if target_mid:
        await complete_message(target_mid, success)


def get_pending_trace_id(chat_id: int) -> str | None:
    """取得目前 pending 的 trace_id。"""
    for ctx in _pending_messages.values():
        if ctx.get("chat_id") == chat_id:
            return ctx.get("trace_id")
    return None


def get_any_pending_trace_id() -> str | None:
    """取得任一 pending trace_id（簡化：單使用者場景）。"""
    for ctx in _pending_messages.values():
        return ctx.get("trace_id")
    return None


def get_latest_pending_chat_id() -> int | None:
    """取得最近一個 pending message 的 chat_id（多使用者 routing 用）。"""
    latest_time = 0.0
    latest_chat = None
    for ctx in _pending_messages.values():
        started = ctx.get("started", 0)
        if started >= latest_time:
            latest_time = started
            latest_chat = ctx.get("chat_id")
    return latest_chat


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """處理自然語言訊息。白名單 → @mention 或 pm-agent → typing + trace。"""
    if not update.message or not update.message.text:
        return
    msg = update.message
    text = msg.text.strip()
    if not text:
        return

    user_id = msg.from_user.id

    # ── 權限檢查 ──
    allowed = context.bot_data.get("allowed_users", [])
    if allowed and user_id not in allowed:
        await msg.reply_text(
            f"🔒 需要白名單權限。\n你的 ID：`{user_id}`\n請聯繫管理員加入。",
            parse_mode="Markdown",
        )
        return

    # ── 路由：@mention → 指定 agent；否則 → pm-agent ──
    mention_match = re.match(r"@([\w-]+)\s*(.*)", text, re.DOTALL)
    if mention_match:
        target = mention_match.group(1)
        message = mention_match.group(2).strip() or text
    else:
        target = "pm-agent"
        message = text

    log.info("📨 user=%s msg=%s → %s", user_id, text[:50], target)

    # ── Trace: 建立紀錄 ──
    trace_id = None
    try:
        from gateway.chat_trace import get_trace_store
        store = get_trace_store()
        trace_id = store.create(user_input=message, target_agent=target)
    except Exception as e:
        log.debug("Trace create failed: %s", e)

    # ── 送出 ──
    daemon = context.bot_data.get("persistent_daemon")
    if daemon:
        # 常駐模式：投遞到 queue，回覆由 MCP reply() tool 異步推送
        ok = await daemon.send_message(target, message)
    else:
        # Spawn 模式：直接執行並等待結果（同步回覆）
        agent_proc = context.bot_data.get("agents", {}).get(target)
        if agent_proc:
            # spawn 模式下直接 await 拿結果，不用 MCP reply
            await _set_reaction(msg, "👀")
            typing_done = asyncio.Event()
            typing_task = asyncio.create_task(
                _typing_loop(msg.chat_id, msg.message_id, context.bot)
            )
            try:
                result = await agent_proc.send(message)
            finally:
                typing_task.cancel()

            if result and result != "queued":
                await _set_reaction(msg, "👍")
                # 簡化顯示（去雜訊）
                display = result[-3000:] if len(result) > 3000 else result
                for i in range(0, len(display), 4000):
                    await msg.reply_text(display[i:i+4000])
            elif result == "queued":
                await msg.reply_text(f"📋 已排入 {target} 佇列，完成後通知。")
            else:
                await _set_reaction(msg, "👎")
                await msg.reply_text(f"⚠️ {target} 處理失敗或超時")
            return  # spawn 模式到此結束，不走 pending 機制
        else:
            ok = False

    # ── 即時回饋 ──
    if ok:
        await _set_reaction(msg, "👀")
        typing_task = asyncio.create_task(
            _typing_loop(msg.chat_id, msg.message_id, context.bot)
        )
        _pending_messages[msg.message_id] = {
            "msg": msg,
            "chat_id": msg.chat_id,
            "typing_task": typing_task,
            "target": target,
            "trace_id": trace_id,
            "started": time.time(),
        }
        asyncio.create_task(_timeout_guard(msg.message_id, target, context, timeout=300))
    else:
        await _set_reaction(msg, "👎")
        await msg.reply_text(f"⚠️ {target} 不可用")
        # trace: 立即標記失敗
        if trace_id:
            try:
                from gateway.chat_trace import get_trace_store
                get_trace_store().fail(trace_id, f"{target} 不可用")
            except Exception:
                pass


async def _timeout_guard(message_id: int, target: str, context: ContextTypes.DEFAULT_TYPE, timeout: float = 300) -> None:
    """超時守衛 — 5 分鐘內沒收到 MCP reply：

    1. 嘗試偵測 agent 是否仍在運行（stdout 仍有活動）
    2. 若已靜默超過 60s → 標記失敗 + 通知使用者
    3. 若仍有活動 → 額外寬限 120s
    """
    await asyncio.sleep(timeout)
    ctx = _pending_messages.get(message_id)
    if not ctx:
        return  # 已由 MCP reply 完成

    # 嘗試偵測 agent 是否仍有活動
    daemon = context.bot_data.get("persistent_daemon") if context else None
    if daemon:
        state = daemon.instances.get(target)
        if state and state.process:
            last_activity = state.last_activity
            # Agent 最後活動在 60 秒內 → 可能還在跑，給額外 120s
            if time.time() - last_activity < 60:
                log.info("⏳ %s still active, extending timeout +120s", target)
                await asyncio.sleep(120)
                # 再次檢查
                ctx = _pending_messages.get(message_id)
                if not ctx:
                    return  # 已完成

    # 確認超時 → 失敗
    trace_id = ctx.get("trace_id")
    if trace_id:
        try:
            from gateway.chat_trace import get_trace_store
            get_trace_store().fail(trace_id, "超時（Agent 未用 reply tool 回覆）")
        except Exception:
            pass

    # 通知使用者
    msg = ctx.get("msg")
    if msg:
        try:
            await msg.reply_text(f"⚠️ {target} 處理超時（未回覆）。可能正在處理複雜任務，稍後會透過通知回報。")
        except Exception:
            pass

    await complete_message(message_id, success=False)
