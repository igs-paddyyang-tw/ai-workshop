"""Bot 指令處理。"""
from __future__ import annotations

import os

from telegram import Update
from telegram.ext import ContextTypes


async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "🤖 AI Bot 已就緒！\n\n"
        "• 直接打字 → AI 對話\n"
        "• 「今天新聞」 → 新聞摘要\n"
        "• /help → 指令清單"
    )


async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "📋 指令清單：\n"
        "/start — 歡迎訊息\n"
        "/help — 本清單\n\n"
        "💬 直接輸入文字即可對話"
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = update.message.text.strip()
    # 關鍵字路由：新聞 → NewsSkill
    if any(kw in text for kw in ["新聞", "news", "今天"]):
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
        return
    # Gemini 對話
    gemini_key = os.getenv("GEMINI_API_KEY", "")
    if gemini_key:
        try:
            from src.llm.gemini_chat import ask_gemini
            reply = await ask_gemini(text)
            await update.message.reply_text(reply)
        except Exception as e:
            await update.message.reply_text(f"⚠️ Gemini 錯誤: {e}")
    else:
        await update.message.reply_text(f"🔄 echo: {text}\n\n💡 填入 GEMINI_API_KEY 開啟 AI 對話")
