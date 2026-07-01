"""Telegram Bot 入口 — 建立 Bot Application。"""
from __future__ import annotations

import os

from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
)

from src.gateway.handlers import cmd_start, cmd_help, cmd_status, cmd_agents, cmd_assign, cmd_board, handle_message


def create_app():
    """建立並回傳 Bot Application。"""
    token = os.getenv("TELEGRAM_BOT_TOKEN", "")
    if not token:
        raise ValueError("TELEGRAM_BOT_TOKEN 未設定")

    app = ApplicationBuilder().token(token).build()

    # 基礎指令（01 Agent）
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("help", cmd_help))
    app.add_handler(CommandHandler("status", cmd_status))

    # 團隊指令（04 Agent Team）
    app.add_handler(CommandHandler("agents", cmd_agents))
    app.add_handler(CommandHandler("assign", cmd_assign))
    app.add_handler(CommandHandler("board", cmd_board))

    # 自然語言（Planner 路由）
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    return app
