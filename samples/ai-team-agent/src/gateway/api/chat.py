"""Chat API — 統一對話系統（目前實作 Telegram 通道）。

Agent 透過 MCP tool 呼叫這些 endpoint 與使用者互動：
  POST /api/chat/reply   — 回覆使用者
  POST /api/chat/notify  — 進度通知
"""
from __future__ import annotations

import logging
from fastapi import APIRouter, Request
from pydantic import BaseModel

log = logging.getLogger(__name__)

router = APIRouter()


class ReplyPayload(BaseModel):
    """Agent 回覆使用者。"""
    instance: str       # 發話的 agent
    text: str           # 回覆內容
    summary: str = ""   # Agent 整理的摘要（≤80 字，optional）
    chat_id: int = 0    # 目標 chat_id（多使用者時指定，0=用預設）


class NotifyPayload(BaseModel):
    """進度通知（轉派、中間狀態等）。"""
    text: str           # 通知文字
    from_agent: str = ""  # 來源 agent（用於 trace route_path）
    to_agent: str = ""    # 目標 agent
    chat_id: int = 0    # 目標 chat_id（0=用預設）


class SendPayload(BaseModel):
    """Agent 間訊息傳遞（走 daemon.send_message）。"""
    target: str         # 目標 agent instance name
    message: str        # 訊息內容
    from_agent: str = ""
    reply_to: str = ""  # 回覆完成後通知誰（A2A callback）


# ── Chat Channel 抽象 ──────────────────────────────────────────

class ChatChannel:
    """對話通道介面。目前只有 TG，未來可擴展 Web / Slack。"""

    async def reply(self, instance: str, text: str, chat_id: int = 0) -> bool:
        """發送回覆給使用者。"""
        return False

    async def notify(self, text: str, chat_id: int = 0) -> bool:
        """發送進度通知給使用者。"""
        return False

    async def complete(self, chat_id: int = 0, success: bool = True) -> None:
        """標記對話完成（reaction 切換）。"""
        pass


class TelegramChannel(ChatChannel):
    """Telegram 通道實作 — 支援多使用者 routing。"""

    def __init__(self) -> None:
        self._bot = None
        self._default_chat_id: int = 0
        self._allowed_chat_ids: list[int] = []

    def configure(self, bot, chat_id: int, allowed_chat_ids: list[int] | None = None) -> None:
        self._bot = bot
        self._default_chat_id = chat_id
        self._allowed_chat_ids = allowed_chat_ids or ([chat_id] if chat_id else [])

    def _resolve_chat_id(self, chat_id: int = 0) -> int:
        """解析目標 chat_id：指定值 > pending message chat > 預設值。"""
        if chat_id and chat_id != 0:
            return chat_id
        # 嘗試從 pending messages 取得最近的 chat_id
        try:
            from gateway.telegram.handlers.messages import get_latest_pending_chat_id
            pending_chat = get_latest_pending_chat_id()
            if pending_chat:
                return pending_chat
        except Exception:
            pass
        return self._default_chat_id

    async def reply(self, instance: str, text: str, chat_id: int = 0) -> bool:
        resolved_id = self._resolve_chat_id(chat_id)
        if not self._bot or not resolved_id:
            log.warning("TelegramChannel not configured: bot=%s chat_id=%s", bool(self._bot), resolved_id)
            return False
        try:
            full_text = f"💬 {instance}：\n{text}"
            for i in range(0, len(full_text), 4000):
                await self._bot.send_message(
                    chat_id=resolved_id,
                    text=full_text[i:i+4000],
                )
            await self.complete(chat_id=resolved_id, success=True)
            return True
        except Exception as e:
            log.warning("TG reply failed: %s", e)
            return False

    async def notify(self, text: str, chat_id: int = 0) -> bool:
        resolved_id = self._resolve_chat_id(chat_id)
        if not self._bot or not resolved_id:
            log.warning("TelegramChannel not configured: bot=%s chat_id=%s", bool(self._bot), resolved_id)
            return False
        try:
            await self._bot.send_message(
                chat_id=resolved_id,
                text=text[:4000],
            )
            return True
        except Exception as e:
            log.warning("TG notify failed: %s", e)
            return False

    async def complete(self, chat_id: int = 0, success: bool = True) -> None:
        """完成對話 — 停 typing + 切 reaction。"""
        resolved_id = self._resolve_chat_id(chat_id)
        try:
            from gateway.telegram.handlers.messages import complete_by_chat
            await complete_by_chat(resolved_id, success)
        except Exception as e:
            log.debug("Complete failed: %s", e)


# ── 全域 channel 實例 ──

_channel: ChatChannel = ChatChannel()


def get_channel() -> ChatChannel:
    return _channel


def set_channel(ch: ChatChannel) -> None:
    global _channel
    _channel = ch


# ── API Endpoints ──────────────────────────────────────────────

@router.post("/reply")
async def chat_reply(body: ReplyPayload, request: Request):
    """Agent 回覆使用者 + trace 完成。"""
    ch = get_channel()
    ok = await ch.reply(body.instance, body.text, chat_id=body.chat_id)

    log.info("✅ reply from %s (%d chars, summary=%s)", body.instance, len(body.text), body.summary[:30] if body.summary else "-")

    # Trace: 標記成功
    try:
        from gateway.chat_trace import get_trace_store
        from gateway.telegram.handlers.messages import get_any_pending_trace_id
        trace_id = get_any_pending_trace_id()
        if trace_id:
            summary = body.summary or body.text[:80]
            get_trace_store().complete(trace_id, reply_summary=summary, success=True)
    except Exception as e:
        log.debug("Trace complete failed: %s", e)

    return {"status": "replied" if ok else "no_channel", "instance": body.instance}


@router.post("/notify")
async def chat_notify(body: NotifyPayload, request: Request):
    """進度通知 + trace route_path 追加。"""
    ch = get_channel()
    ok = await ch.notify(body.text, chat_id=body.chat_id)

    # Trace: 追加路徑
    if body.to_agent:
        try:
            from gateway.chat_trace import get_trace_store
            from gateway.telegram.handlers.messages import get_any_pending_trace_id
            trace_id = get_any_pending_trace_id()
            if trace_id:
                get_trace_store().append_route(trace_id, body.to_agent)
        except Exception:
            pass

    return {"status": "notified" if ok else "no_channel"}


@router.get("/traces")
async def chat_traces(limit: int = 20):
    """查詢最近對話軌跡。"""
    try:
        from gateway.chat_trace import get_trace_store
        return get_trace_store().recent(limit=limit)
    except Exception as e:
        return {"error": str(e)}


@router.post("/send")
async def chat_send(body: SendPayload, request: Request):
    """Agent 間訊息傳遞 — 透過 daemon.send_message 實際送達。

    支援 A2A callback：reply_to 欄位指定完成後通知的 agent。
    回覆指示以獨立 JSON header 注入，不污染訊息本文。
    """
    daemon = getattr(request.app.state, "persistent_daemon", None)
    if not daemon:
        return {"status": "no_daemon", "target": body.target}

    # A2A metadata 以 JSON header 行注入首行，Agent SOUL.md 可解析
    # 格式：[A2A] from=xxx reply_to=yyy
    if body.reply_to or body.from_agent:
        header_parts = []
        if body.from_agent:
            header_parts.append(f"from={body.from_agent}")
        if body.reply_to:
            header_parts.append(f"reply_to={body.reply_to}")
        message = f"[A2A] {' '.join(header_parts)}\n{body.message}"
    else:
        message = body.message

    ok = await daemon.send_message(body.target, message)
    if ok:
        log.info("📋 send: %s → %s (%d chars, reply_to=%s)", body.from_agent, body.target, len(body.message), body.reply_to or "-")
    else:
        log.warning("❌ send failed: %s → %s", body.from_agent, body.target)

    return {"status": "sent" if ok else "failed", "target": body.target}
