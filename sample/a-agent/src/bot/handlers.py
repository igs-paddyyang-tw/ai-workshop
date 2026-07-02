"""Bot 指令處理 + 意圖路由（雙模式）。

對話流程：
  1. 關鍵字命中 → Skill 直接執行（快速路徑，不需 LLM）
  2. 有 kiro-cli → agent_cli_chat（完整 Agent 模式，.kiro/ 全生效）
  3. 無 kiro-cli → gemini_chat（直呼 API，用 SOUL 作 system prompt）
"""
from __future__ import annotations

import os
from pathlib import Path

from telegram import Update
from telegram.ext import ContextTypes

# ── 載入 SOUL.md（Gemini fallback 模式使用）──
_SOUL_PATH = Path(".kiro/steering/SOUL.md")
_SOUL_CONTENT = _SOUL_PATH.read_text(encoding="utf-8") if _SOUL_PATH.exists() else ""


# ── 指令 ─────────────────────────────────────────────────


async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    from src.agent.cli import is_cli_available
    mode = "🧠 Agent CLI 模式" if is_cli_available() else "⚡ Gemini API 模式"
    await update.message.reply_text(
        f"🤖 AI Agent 已就緒！（{mode}）\n\n"
        "• 直接打字 → AI 對話\n"
        "• 「今天新聞」 → 新聞摘要\n"
        "• /help → 指令清單\n"
        "• /mode → 查看當前模式"
    )


async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "📋 指令清單：\n"
        "/start — 歡迎訊息\n"
        "/help — 本清單\n"
        "/mode — 查看 Agent 模式\n\n"
        "💬 直接輸入文字即可對話\n"
        "📰 輸入「今天新聞」觸發 NewsSkill"
    )


async def cmd_mode(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """顯示當前 Agent 執行模式。"""
    from src.agent.cli import is_cli_available
    if is_cli_available():
        await update.message.reply_text(
            "🧠 **Agent CLI 模式**\n\n"
            "• kiro-cli 已安裝 ✅\n"
            "• .kiro/steering/SOUL.md → 人格生效\n"
            "• .kiro/skills/ → Skills 自動觸發\n"
            "• .kiro/prompts/ → 提詞模板載入\n\n"
            "對話由 kiro-cli 驅動（完整 Agent 能力）",
            parse_mode="Markdown",
        )
    else:
        has_key = "✅" if os.getenv("GEMINI_API_KEY") else "❌"
        await update.message.reply_text(
            "⚡ **Gemini API 模式**（fallback）\n\n"
            f"• kiro-cli 未安裝\n"
            f"• Gemini API Key: {has_key}\n"
            f"• SOUL.md 作為 system prompt 注入\n\n"
            "安裝 kiro-cli 後自動升級為 Agent CLI 模式：\n"
            "`npm i -g kiro-cli && kiro-cli login`",
            parse_mode="Markdown",
        )


# ── 自然語言路由 ─────────────────────────────────────────


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """意圖路由：關鍵字 → Skill / kiro-cli / Gemini fallback。"""
    text = update.message.text.strip()

    # ── 1. 關鍵字快速路由（不需 LLM，毫秒級）──
    if any(kw in text for kw in ["新聞", "news", "今天"]):
        await _handle_news(update)
        return

    # ── 2. Agent CLI 模式（kiro-cli 已安裝）──
    from src.agent.cli import is_cli_available, agent_cli_chat
    if is_cli_available():
        await update.message.reply_text("🧠 思考中...")
        reply = await agent_cli_chat(text)
        if reply:
            await update.message.reply_text(reply)
            return
        # kiro-cli 失敗 → fallback 到 Gemini API

    # ── 3. Gemini API fallback（直呼 API + SOUL 注入）──
    gemini_key = os.getenv("GEMINI_API_KEY", "")
    if gemini_key:
        try:
            from src.llm.gemini_chat import gemini_chat
            reply = await gemini_chat(text, system=_SOUL_CONTENT)
            if reply:
                await update.message.reply_text(reply)
            else:
                await update.message.reply_text("⚠️ Gemini 回覆失敗，請稍後再試")
        except Exception as e:
            await update.message.reply_text(f"⚠️ Gemini 錯誤: {e}")
    else:
        await update.message.reply_text(
            f"🔄 echo: {text}\n\n"
            "💡 開啟 AI 對話：\n"
            "• 方式 A：填入 GEMINI_API_KEY（快速）\n"
            "• 方式 B：安裝 kiro-cli（完整 Agent）"
        )


# ── Skill 處理 ───────────────────────────────────────────


async def _handle_news(update: Update) -> None:
    """新聞 Skill 快速路徑。"""
    await update.message.reply_text("🔍 正在抓取新聞...")
    try:
        from src.skills.internal.news import NewsSkill
        skill = NewsSkill()
        result = await skill.execute({"max_items": 5})
        if result.success:
            lines = [f"📰 *{result.data['source']}* — {result.data['count']} 則\n"]
            for i, art in enumerate(result.data["articles"], 1):
                lines.append(f"{i}. [{art['title']}]({art['url']}) (⬆️{art['score']})")
            await update.message.reply_text(
                "\n".join(lines), parse_mode="Markdown", disable_web_page_preview=True
            )
        else:
            await update.message.reply_text(f"⚠️ {result.error}")
    except Exception as e:
        await update.message.reply_text(f"⚠️ 新聞抓取失敗: {e}")
