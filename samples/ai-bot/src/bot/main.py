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
    cmd_chat,
    cmd_help,
    cmd_history,
    cmd_mode,
    cmd_start,
    cmd_status,
    handle_message,
)
from src.memory.tg_handlers import (
    callback_skill_approval,
    cmd_consolidate,
    cmd_recall,
    cmd_skills,
)

# Bot 指令選單（TG 左下角 / 按鈕）
BOT_COMMANDS = [
    BotCommand("start", "歡迎 + Chat ID"),
    BotCommand("status", "團隊狀態"),
    BotCommand("help", "使用說明"),
    BotCommand("agents", "Agent 列表"),
    BotCommand("recall", "搜尋記憶"),
    BotCommand("skills", "技能清單"),
]


async def _post_init(application) -> None:
    """Bot 啟動後強制更新指令選單。"""
    await application.bot.delete_my_commands()
    await application.bot.set_my_commands(BOT_COMMANDS)


def create_app():
    token = os.getenv("TELEGRAM_BOT_TOKEN", "")
    if not token:
        raise ValueError("TELEGRAM_BOT_TOKEN 未設定")

    app = ApplicationBuilder().token(token).post_init(_post_init).build()

    # 指令
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("status", cmd_status))
    app.add_handler(CommandHandler("help", cmd_help))
    app.add_handler(CommandHandler("agents", cmd_agents))
    app.add_handler(CommandHandler("mode", cmd_mode))
    app.add_handler(CommandHandler("history", cmd_history))
    app.add_handler(CommandHandler("chat", cmd_chat))
    app.add_handler(CommandHandler("recall", cmd_recall))
    app.add_handler(CommandHandler("skills", cmd_skills))
    app.add_handler(CommandHandler("consolidate", cmd_consolidate))

    # Inline Button 回調
    app.add_handler(CallbackQueryHandler(callback_switch_agent, pattern="^switch_agent:"))
    app.add_handler(CallbackQueryHandler(callback_skill_approval, pattern="^skill_"))

    # 自然語言
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    return app
