"""Bot 指令處理 + 意圖路由。

Workshop 對照：
  01 Agent: cmd_start, cmd_help, handle_message（Planner 路由）
  04 Team:  cmd_agents, cmd_assign, cmd_board
"""
from __future__ import annotations

import os

from telegram import Update
from telegram.ext import ContextTypes


# ─── 01 基礎指令 ─────────────────────────────────────────


async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "🤖 AI Workshop Bot 已就緒！\n\n"
        "💬 直接打字 → AI 對話\n"
        "📰 「今天新聞」 → 新聞摘要\n"
        "👥 /agents → 團隊成員\n"
        "📋 /assign → 派工\n"
        "📊 /board → 看板\n"
        "❓ /help → 指令清單"
    )


async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "📋 指令清單：\n\n"
        "── 基礎 ──\n"
        "/start — 歡迎訊息\n"
        "/help — 本清單\n"
        "/status — 系統狀態\n\n"
        "── 團隊 ──\n"
        "/agents — 列出成員\n"
        "/assign <任務> <agent> — 派工\n"
        "/board — 任務看板\n\n"
        "── AI ──\n"
        "直接輸入文字 → Gemini 對話\n"
        "「今天新聞」→ News Skill"
    )


async def cmd_status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    from src.skills.registry import SkillRegistry
    registry = SkillRegistry()
    registry.auto_discover("src.skills.internal")
    skills_count = len(registry.list_skills())

    gemini = "✅" if os.getenv("GEMINI_API_KEY") else "❌"
    await update.message.reply_text(
        f"📊 系統狀態：\n"
        f"  Skills 載入: {skills_count}\n"
        f"  Gemini AI: {gemini}\n"
        f"  Bot: ✅ 運行中"
    )


# ─── 04 團隊指令 ─────────────────────────────────────────


async def cmd_agents(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    from src.coordinator.task_manager import get_team_agents
    agents = get_team_agents()
    lines = [f"• {a['name']} ({a['id']}) — {a['role']}" for a in agents]
    await update.message.reply_text("👥 團隊成員：\n" + "\n".join(lines))


async def cmd_assign(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    from src.coordinator.task_manager import task_manager
    args = context.args or []
    if len(args) < 2:
        await update.message.reply_text("用法：/assign <任務標題> <agent_id>")
        return
    agent_id = args[-1]
    title = " ".join(args[:-1])
    task = task_manager.create_task(title)
    task_manager.assign(task.id, agent_id)
    await update.message.reply_text(f"✅ 任務 {task.id} 已指派給 {agent_id}")


async def cmd_board(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    from src.coordinator.task_manager import task_manager
    tasks = task_manager.list_tasks()
    if not tasks:
        await update.message.reply_text("📋 看板為空")
        return
    lines = [f"• [{t.status}] {t.id}: {t.title} → {t.assignee or '未指派'}" for t in tasks]
    await update.message.reply_text("📋 任務看板：\n" + "\n".join(lines))


# ─── 自然語言路由（Planner）─────────────────────────────


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """意圖路由：關鍵字 → Skill / LLM fallback。"""
    text = update.message.text.strip()

    # 新聞觸發 → NewsSkill
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

    # Wiki 查詢觸發
    if any(kw in text for kw in ["wiki", "知識庫", "查知識"]):
        from src.wiki.engine import WikiEngine
        engine = WikiEngine()
        use_rag = bool(os.getenv("GEMINI_API_KEY"))
        result = await engine.query(text, use_rag=use_rag)
        if result.get("answer"):
            await update.message.reply_text(f"📚 {result['answer']}")
        elif result.get("results"):
            lines = [f"📚 找到 {len(result['results'])} 筆："]
            for r in result["results"][:3]:
                lines.append(f"• {r['title']}: {r['snippet'][:80]}")
            await update.message.reply_text("\n".join(lines))
        else:
            await update.message.reply_text("📚 Wiki 中沒有找到相關內容")
        return

    # Gemini 對話 fallback
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
