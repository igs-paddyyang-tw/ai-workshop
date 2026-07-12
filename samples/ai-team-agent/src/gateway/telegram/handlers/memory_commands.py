"""TG 指令 — Memory / Skills / Tier 相關（M6 對齊）。"""
from __future__ import annotations

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes


# ── /recall ──

async def cmd_recall(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """查詢 Agent 記憶。"""
    query = update.message.text.replace("/recall", "").strip()
    if not query:
        await update.message.reply_text("用法：/recall <查詢關鍵字>\n例如：/recall 部署")
        return

    # 加 reaction
    try:
        await update.message.set_reaction("👀")
    except Exception:
        pass

    from coordinator.memory.recall import recall

    # 預設查 pm-agent 或第一個 agent
    agent_name = context.bot_data.get("current_agent", "pm-agent")
    results = await recall(agent_name, query, k=5)

    if not results:
        await update.message.reply_text(f"🔍 <b>{agent_name}</b> 沒有「{query}」的相關記憶", parse_mode="HTML")
        return

    lines = [f"🧠 <b>{agent_name} 記憶查詢</b>：{query}\n"]
    for i, r in enumerate(results, 1):
        lines.append(f"{i}. [{r.date}] {r.title[:50]}")
        if r.body:
            lines.append(f"   {r.body[:80]}")
        lines.append("")

    await update.message.reply_text("\n".join(lines), parse_mode="HTML")

    try:
        await update.message.set_reaction("👍")
    except Exception:
        pass


# ── /consolidate ──

async def cmd_consolidate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """手動蒸餾 daily → memory.md。"""
    try:
        await update.message.set_reaction("🔥")
    except Exception:
        pass

    from coordinator.memory.consolidate import consolidate

    agent_name = context.bot_data.get("current_agent", "pm-agent")

    # 取得 gemini_fn
    gemini_fn = context.bot_data.get("gemini_fn")

    result = await consolidate(agent_name, gemini_fn=gemini_fn)
    preview = result[:300] if result else "（無內容可蒸餾）"

    await update.message.reply_text(
        f"✅ <b>{agent_name}</b> 記憶蒸餾完成\n\n<pre>{preview}</pre>",
        parse_mode="HTML",
    )

    try:
        await update.message.set_reaction("👍")
    except Exception:
        pass


# ── /skills ──

async def cmd_skills(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """列出 Skills + 統計。"""
    arg = update.message.text.replace("/skills", "").strip()

    # /skills pending → 待審提案
    if arg == "pending":
        await _skills_pending(update, context)
        return

    # 列出所有 Skill
    registry = context.bot_data.get("skill_registry")
    if not registry:
        await update.message.reply_text("⚠️ Skills 框架尚未啟動")
        return

    skills = registry.list_skills()
    if not skills:
        await update.message.reply_text("📦 尚無已載入的 Skill")
        return

    # 取得統計
    tracker = registry.tracker
    stats_map: dict[str, dict] = {}
    if tracker:
        all_stats = await tracker.get_stats()
        stats_map = {s["skill_id"]: s for s in all_stats}

    lines = [f"📦 <b>Skills</b>（{len(skills)} 個）\n"]
    for s in skills:
        stat = stats_map.get(s["skill_id"])
        if stat:
            rate = f"{stat['success_rate']:.0%}"
            calls = stat["call_count"]
            lines.append(f"• <b>{s['skill_id']}</b> v{s['version']} — 📞{calls} ✅{rate}")
        else:
            lines.append(f"• <b>{s['skill_id']}</b> v{s['version']} — {s['description'][:30]}")

    await update.message.reply_text("\n".join(lines), parse_mode="HTML")


async def _skills_pending(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """顯示待審 Skill 提案。"""
    growth = context.bot_data.get("growth_detector")
    if not growth:
        await update.message.reply_text("⚠️ 自我成長系統尚未啟動")
        return

    pending = growth.get_pending()
    if not pending:
        await update.message.reply_text("✅ 沒有待審的 Skill 提案")
        return

    for p in pending[:5]:
        text = (
            f"🆕 <b>Skill 提案</b>\n\n"
            f"Agent: {p['agent']}\n"
            f"Skill: {p['skill_id']}\n"
            f"提案時間: {p['proposed_at'][:16]}\n"
        )
        kb = InlineKeyboardMarkup([[
            InlineKeyboardButton("✅ 核准", callback_data=f"skill_approve:{p['id']}"),
            InlineKeyboardButton("❌ 駁回", callback_data=f"skill_reject:{p['id']}"),
        ]])
        await update.message.reply_text(text, parse_mode="HTML", reply_markup=kb)


# ── /mode ──

async def cmd_mode(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """顯示當前 Tier。"""
    from runtime.tier import detect_tier

    status = detect_tier()
    check = "✅"
    empty = "⬚"

    lines = [
        "📊 <b>執行模式</b>\n",
        f"  Tier 0: {check} Skills + Wiki + API",
        f"  Tier 1: {check if status.tg_ok else empty} Telegram Bot",
        f"  Tier 2: {check if status.llm_ok else empty} Gemini AI",
        f"  Tier 3: {check if status.cli_ok else empty} kiro-cli Agent",
        f"  Tier 4: {check if status.team_ok else empty} Team A2A",
        f"\n  🏷️ 當前 Tier: <b>{status.tier}</b>",
    ]
    await update.message.reply_text("\n".join(lines), parse_mode="HTML")
