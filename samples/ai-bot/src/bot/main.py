"""Telegram Bot 入口 — 含 Inline Button 回調 + 指令選單。"""
from __future__ import annotations

import os

from telegram import BotCommand
from telegram.ext import (
    ApplicationBuilder,
    CallbackQueryHandler,
    CommandHandler,
    MessageHandler,
    filters,
)

from src.bot.handlers import (
    callback_switch_agent,
    cmd_agents,
    cmd_help,
    cmd_history,
    cmd_mode,
    cmd_start,
    handle_message,
)

# Bot 指令選單（TG 左下角 / 按鈕）
BOT_COMMANDS = [
    BotCommand("start", "啟動 Bot"),
    BotCommand("agents", "切換 Agent"),
    BotCommand("news", "📰 抓新聞"),
    BotCommand("wiki", "📚 查知識庫"),
    BotCommand("summarize", "📝 摘要"),
    BotCommand("translate", "🌐 翻譯"),
    BotCommand("ingest", "⬆️ 匯入知識"),
    BotCommand("mode", "查看模式"),
    BotCommand("history", "對話歷史"),
    BotCommand("help", "指令說明"),
]


async def _post_init(application) -> None:
    """Bot 啟動後設定指令選單。"""
    await application.bot.set_my_commands(BOT_COMMANDS)


def create_app():
    token = os.getenv("TELEGRAM_BOT_TOKEN", "")
    if not token:
        raise ValueError("TELEGRAM_BOT_TOKEN 未設定")

    app = ApplicationBuilder().token(token).post_init(_post_init).build()

    # 指令
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("help", cmd_help))
    app.add_handler(CommandHandler("agents", cmd_agents))
    app.add_handler(CommandHandler("mode", cmd_mode))
    app.add_handler(CommandHandler("history", cmd_history))

    # Inline Button 回調
    app.add_handler(CallbackQueryHandler(callback_switch_agent, pattern="^switch_agent:"))

    # 自然語言
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    return app
