"""Telegram Bot 入口。"""
from __future__ import annotations

import os

from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters

from src.bot.handlers import cmd_start, cmd_help, cmd_mode, handle_message


def create_app():
    token = os.getenv("TELEGRAM_BOT_TOKEN", "")
    if not token:
        raise ValueError("TELEGRAM_BOT_TOKEN 未設定")
    app = ApplicationBuilder().token(token).build()
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("help", cmd_help))
    app.add_handler(CommandHandler("mode", cmd_mode))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    return app
