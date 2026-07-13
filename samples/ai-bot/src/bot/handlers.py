"""Bot 指令處理 — Inline Button Agent 切換 + Memory 管理。

對話流程：
  /agents → Inline Keyboard → 選 Agent → 對話 → 自動寫 memory
"""
from __future__ import annotations

import asyncio
import os
import re
from pathlib import Path

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from src.agent.session import session_manager
from src.agent.cli import AVAILABLE_AGENTS, is_cli_available, agent_cli_chat

log = __import__("logging").getLogger("bot.handlers")

# ── 白名單：只有 ADMIN_CHAT_IDS 的人能使用 Bot ──
_ALLOWED_USERS: set[int] = set()
_admin_env = os.getenv("ADMIN_CHAT_IDS", "")
if _admin_env:
    _ALLOWED_USERS = {int(x.strip()) for x in _admin_env.split(",") if x.strip().isdigit()}


def _is_authorized(user_id: int) -> bool:
    """檢查使用者是否在白名單中。白名單為空 = 不限制（開發模式）。"""
    if not _ALLOWED_USERS:
        return True  # 未設定白名單 = 所有人可用
    return user_id in _ALLOWED_USERS


# ── 載入 SOUL（fallback 模式用）──
_SOUL_DIR = Path("agents/admin-agent/.kiro/steering")


def _load_soul(agent_id: str) -> str:
    """載入指定 Agent 的 SOUL.md。"""
    path = Path(f"agents/{agent_id}-agent/.kiro/steering/SOUL.md")
    if path.exists():
        return path.read_text(encoding="utf-8")
    # fallback 到根 .kiro/
    root_soul = Path(".kiro/steering/SOUL.md")
    return root_soul.read_text(encoding="utf-8") if root_soul.exists() else ""


# ── 指令 ─────────────────────────────────────────────────


async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    session = session_manager.get_or_create(user_id)
    session.clear_history()

    # 判斷當前模式
    if session.is_default_mode:
        mode_str = "⚡ Gemini（Default）"
        agent_str = "🚀 Ark Agent"
    else:
        agent_name = session.agent_name
        info = AVAILABLE_AGENTS.get(agent_name, {})
        cli_ok = is_cli_available()
        mode_str = "🧠 Agent CLI" if cli_ok else "⚠️ Agent CLI（未安裝）"
        agent_str = f"{info.get('emoji', '🤖')} {info.get('name', agent_name)}"

    # 顯示 Chat ID（供使用者填入 ADMIN_CHAT_IDS）
    auth_status = "✅ 已授權" if _is_authorized(user_id) else "🔒 未授權（自然語言對話需將 Chat ID 加入 .env）"

    await update.message.reply_text(
        f"🤖 AI Agent 已就緒！\n\n"
        f"• 模式：{mode_str}\n"
        f"• 對話：{agent_str}\n"
        f"• 狀態：{auth_status}\n"
        f"• Chat ID：`{user_id}`\n\n"
        "📌 /agents → 切換對話模式（9 選項）\n"
        "💬 直接打字 → 對話\n"
        "🔍 /recall → 查歷史記憶\n"
        "📋 /help → 指令清單",
        parse_mode="Markdown",
    )


async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "📋 **指令清單**\n\n"
        "**對話**\n"
        "💬 直接輸入文字 → 對話\n"
        "/agents → 切換對話模式（Ark Agent / 8 Agent）\n\n"
        "**記憶**\n"
        "/recall `關鍵詞` → 查歷史記憶\n"
        "/skills → 已學會的 Skill\n"
        "/consolidate → 蒸餾記憶\n\n"
        "**其他**\n"
        "/start → 重新開始\n"
        "/mode → 查看執行模式\n"
        "/history → 對話歷史\n"
        "/help → 本清單",
        parse_mode="Markdown",
    )


async def cmd_agents(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """顯示 Inline Keyboard 選擇對話模式（9 選項）。"""
    user_id = update.effective_user.id
    session = session_manager.get_or_create(user_id)

    # Default 按鈕
    default_prefix = "✓ " if session.is_default_mode else ""
    default_btn = InlineKeyboardButton(
        f"{default_prefix}🚀 Ark Agent（Gemini）",
        callback_data="switch_agent:default",
    )

    # Agent 按鈕
    def btn(agent_id):
        info = AVAILABLE_AGENTS[agent_id]
        prefix = "✓ " if session.agent_name == agent_id else ""
        return InlineKeyboardButton(
            f"{prefix}{info['emoji']} {agent_id.capitalize()}",
            callback_data=f"switch_agent:{agent_id}",
        )

    keyboard = [
        [default_btn],
        [btn("admin"), btn("pm")],
        [btn("ai-dev"), btn("coder")],
        [btn("qa"), btn("data")],
        [btn("market"), btn("report")],
        [InlineKeyboardButton("🔙 回到 Ark Agent", callback_data="switch_agent:default")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    mode_str = "🚀 Ark Agent（Gemini）" if session.is_default_mode else f"{AVAILABLE_AGENTS[session.agent_name]['emoji']} {session.agent_name}-agent（Agent CLI）"
    await update.message.reply_text(
        f"當前：{mode_str}\n\n"
        "選擇對話模式：\n"
        "• Ark Agent = Gemini API（零門檻）\n"
        "• Agent 分身 = Agent CLI（需安裝）",
        reply_markup=reply_markup,
    )


async def callback_switch_agent(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Inline Button 回調 — 切換對話模式。"""
    query = update.callback_query
    await query.answer()

    agent_id = query.data.split(":")[1]
    user_id = query.from_user.id

    if agent_id == "default":
        session_manager.switch_agent(user_id, "default")
        await query.edit_message_text(
            "✅ 已切換到 🚀 **Ark Agent**（Gemini）\n\n"
            "直接輸入文字即可對話。",
            parse_mode="Markdown",
        )
        return

    if agent_id not in AVAILABLE_AGENTS:
        await query.edit_message_text("❌ 無效的 Agent")
        return

    # 檢查 Agent CLI
    if not is_cli_available():
        await query.edit_message_text(
            f"⚠️ **{agent_id}-agent** 需要 Agent CLI\n\n"
            "安裝任一即可：\n"
            "• agy: `irm https://antigravity.google/cli/install.ps1 | iex`\n"
            "• kiro-cli: `npm i -g kiro-cli && kiro-cli login`\n"
            "• claude: `npm i -g @anthropic-ai/claude-cli`\n\n"
            "目前請使用 🚀 Ark Agent 模式。",
            parse_mode="Markdown",
        )
        return

    session_manager.switch_agent(user_id, agent_id)
    info = AVAILABLE_AGENTS[agent_id]
    await query.edit_message_text(
        f"✅ 已切換到 {info['emoji']} **{info['name']}**（Agent CLI）\n\n"
        f"{info['desc']}\n\n"
        f"現在開始對話吧！",
        parse_mode="Markdown",
    )


async def cmd_mode(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """顯示當前執行模式。"""
    if is_cli_available():
        from src.agent.cli import get_available_backend
        backend = get_available_backend()
        await update.message.reply_text(
            "🧠 **Agent CLI 模式**\n\n"
            f"• Backend: {backend} ✅\n"
            "• .kiro/ 配置全部生效\n"
            f"• 對話由 {backend} 驅動",
            parse_mode="Markdown",
        )
    else:
        has_key = "✅" if os.getenv("GEMINI_API_KEY") else "❌"
        await update.message.reply_text(
            f"⚡ **Gemini API 模式**\n\n"
            f"• Gemini Key: {has_key}\n"
            f"• SOUL.md 作為 system prompt\n\n"
            "升級：安裝 Agent CLI（agy / kiro-cli / claude）",
            parse_mode="Markdown",
        )


async def cmd_history(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """顯示近期對話歷史。"""
    user_id = update.effective_user.id
    session = session_manager.get_or_create(user_id)
    if not session.history:
        await update.message.reply_text("📭 目前沒有對話歷史")
        return
    lines = [f"📜 對話歷史（{AVAILABLE_AGENTS[session.current_agent]['emoji']} {session.current_agent}）：\n"]
    for turn in session.history[-6:]:  # 最近 6 輪
        prefix = "👤" if turn.role == "user" else "🤖"
        content = turn.content[:80] + "..." if len(turn.content) > 80 else turn.content
        lines.append(f"{prefix} {content}")
    await update.message.reply_text("\n".join(lines))


# ── /chat — 強制 Gemini API（帶完整 context）──────────────


async def cmd_chat(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/chat <問題> — 強制使用 Gemini API 回答（帶完整記憶+知識+技能 context）。"""
    text = " ".join(context.args) if context.args else ""
    if not text:
        await update.message.reply_text(
            "用法：`/chat 你的問題`\n\n"
            "此指令強制使用 Gemini API（2-3 秒回覆），"
            "帶入完整 context：SOUL + 記憶 + 知識庫 + 技能清單 + 對話歷史。",
            parse_mode="Markdown",
        )
        return

    gemini_key = os.getenv("GEMINI_API_KEY", "")
    if not gemini_key:
        await update.message.reply_text("❌ GEMINI_API_KEY 未設定")
        return

    user_id = update.effective_user.id
    session = session_manager.get_or_create(user_id)
    current_agent = session.current_agent
    agent_info = AVAILABLE_AGENTS[current_agent]

    session.add_turn("user", text)
    await _set_reaction(update.message, "🔥")

    # ── 組裝完整 system prompt ──
    system_prompt = await _build_rich_system_prompt(current_agent, text, session)

    # ── 呼叫 Gemini（帶 Tool Calling）──
    try:
        from src.llm.agent_loop import agent_loop
        reply = await agent_loop(text, system=system_prompt)
    except Exception as e:
        log.error("Gemini chat error: %s", e)
        reply = f"⚠️ Gemini 錯誤：{e}"

    if reply:
        if len(reply) > 3000:
            reply = reply[-3000:]
        session.add_turn("agent", reply)
        await _set_reaction(update.message, "👍")
        header = f"⚡ [{current_agent}-agent] (Gemini)\n"
        full_text = header + reply
        for i in range(0, len(full_text), 4000):
            await update.message.reply_text(full_text[i:i+4000])
    else:
        await _set_reaction(update.message, "💔")
        await update.message.reply_text("⚠️ Gemini 無回應，請稍後再試。")


async def _build_rich_system_prompt(agent_id: str, query: str, session) -> str:
    """組裝完整 Gemini system prompt（6 層 context）。

    注入順序：
    1. SOUL.md — Agent 人格
    2. memory.md — 持久事實（蒸餾記憶）
    3. recent.md — 今+昨 daily log
    4. FTS5 recall — 相關歷史記憶 top-3
    5. Wiki context — 知識庫相關段落
    6. Skills list — 可用技能清單
    7. Session history — 對話歷史
    """
    parts: list[str] = []

    # 1. SOUL
    soul = _load_soul(agent_id)
    if soul:
        parts.append(soul)

    # 2. memory.md（蒸餾持久事實）
    memory_path = Path(f"agents/{agent_id}-agent/memory/memory.md")
    if memory_path.exists():
        content = memory_path.read_text(encoding="utf-8")
        if content.strip() and len(content) > 20:
            parts.append(f"\n## 持久記憶\n{content[:1500]}")

    # 3. recent.md（最近經驗）
    recent_path = Path(f"agents/{agent_id}-agent/memory/recent.md")
    if recent_path.exists():
        content = recent_path.read_text(encoding="utf-8")
        if content.strip() and "（尚無記錄）" not in content:
            parts.append(f"\n## 最近經驗\n{content[:1500]}")

    # 4. FTS5 recall（相關歷史）
    try:
        from src.memory.recall import recall
        results = recall(f"{agent_id}-agent", query, k=3)
        if results:
            recall_lines = ["\n## 相關歷史記憶"]
            for r in results:
                recall_lines.append(f"- [{r.date}] {r.title}: {r.body[:100]}")
            parts.append("\n".join(recall_lines))
    except Exception:
        # FTS5 不可用時 fallback
        memory_context = _search_memory(agent_id, query)
        if memory_context:
            parts.append(f"\n## 相關歷史記憶\n{memory_context}")

    # 5. Wiki context（知識庫相關段落，不走 RAG 合成）
    try:
        from src.wiki.engine import WikiEngine
        engine = WikiEngine(agent_id=agent_id)
        wiki_result = await engine.query(query, use_rag=False)
        if wiki_result.get("results"):
            wiki_lines = ["\n## 知識庫參考（搜尋範圍：私有 wiki → knowledge/shared/wiki/）"]
            for r in wiki_result["results"][:3]:
                wiki_lines.append(f"### {r['title']}\n{r['snippet'][:200]}")
            parts.append("\n".join(wiki_lines))
        else:
            parts.append(
                "\n## 知識檢索規則\n"
                "- 回答事實性問題前先查 wiki（私有 → 共用 knowledge/shared/wiki/）\n"
                "- 查無結果才走外部搜尋，並明確告知使用者"
            )
    except Exception:
        pass

    # 6. Skills list（可用技能）
    try:
        from src.skills.registry import SkillRegistry
        registry = SkillRegistry()
        registry.auto_discover("src.skills.internal")
        skills = registry.list_skills()
        if skills:
            skill_lines = ["\n## 可用技能（使用者可用 /skill_id 觸發）"]
            for s in skills[:10]:
                skill_lines.append(f"- /{s['skill_id']} — {s['description'][:40]}")
            parts.append("\n".join(skill_lines))
    except Exception:
        pass

    # 7. Session history
    context_str = session.get_context()
    if context_str:
        parts.append(f"\n{context_str}")

    return "\n\n".join(parts)


async def _build_default_system_prompt(query: str, session) -> str:
    """組裝 Default 模式的 Gemini system prompt（8 層 context + Tool 規則）。

    讀取根目錄的 steering + memory + wiki，不走任何 Agent 私有目錄。
    """
    parts: list[str] = []

    # 1. SOUL.md（根目錄）
    soul_path = Path(".kiro/steering/SOUL.md")
    if soul_path.exists():
        parts.append(soul_path.read_text(encoding="utf-8"))

    # 2. BRAIN.md（根目錄）
    brain_path = Path(".kiro/steering/BRAIN.md")
    if brain_path.exists():
        content = brain_path.read_text(encoding="utf-8")
        # 移除 frontmatter
        if content.startswith("---"):
            _, _, content = content.split("---", 2)
        parts.append(content.strip())

    # 3. USER.md（根目錄）
    user_path = Path(".kiro/steering/USER.md")
    if user_path.exists():
        parts.append(user_path.read_text(encoding="utf-8"))

    # 4. Tool 使用規則
    parts.append("""## 工具使用規則

你有三個工具可用：read_file、write_file、list_files。

### 何時使用 write_file：
- 使用者明確要求：「寫成報告」「存進知識庫」「匯出」「產出文件」「幫我整理成文章」
- 寫入前告訴使用者你要寫什麼、寫到哪裡
- 寫入後回覆確認路徑和大小

### 何時不使用 write_file：
- 一般對話（只是聊天、問答）→ 不寫
- 使用者沒要求保存 → 不寫
- 對話記錄 → 系統自動處理，你不需寫

### 寫入路徑選擇：
- 報告/分析 → output/reports/{date}_{slug}.md
- 知識庫文章（使用者說「存進知識庫」）→ knowledge/shared/raw/{slug}.md（系統會自動匯入索引）
- 匯出資料 → output/exports/{date}_{slug}.csv
- 草稿 → output/drafts/{slug}.md

### Memory vs Wiki 分工：
- Memory（系統自動）= 你經歷過的事（對話記錄、決策）
- Wiki（使用者要求才寫）= 可重複引用的知識（事實、規格、分析）
- Output（使用者要求才寫）= 交付的產出物（報告、匯出檔）
""")

    # 5. memory/memory.md（根目錄持久事實）
    memory_path = Path("memory/memory.md")
    if memory_path.exists():
        content = memory_path.read_text(encoding="utf-8")
        if content.strip() and "（尚無記錄）" not in content:
            parts.append(f"\n## 持久記憶\n{content[:1500]}")

    # 6. memory/recent.md（根目錄最近經驗）
    recent_path = Path("memory/recent.md")
    if recent_path.exists():
        content = recent_path.read_text(encoding="utf-8")
        if content.strip() and "（尚無記錄）" not in content:
            parts.append(f"\n## 最近經驗\n{content[:1500]}")

    # 6b. 今日 daily log 尾部 5 筆（讓 Gemini 知道今天做過什麼）
    from datetime import datetime as _dt
    today_log = Path("memory/daily") / f"{_dt.now().strftime('%Y-%m-%d')}.md"
    if today_log.exists():
        log_content = today_log.read_text(encoding="utf-8")
        log_entries = [e.strip() for e in log_content.split("\n## ") if e.strip()]
        # 取最後 5 筆（跳過 header 行）
        recent_entries = log_entries[-5:] if len(log_entries) > 5 else log_entries
        if recent_entries:
            daily_text = "\n## ".join(recent_entries)
            # 去掉可能的 "# 2026-07-13 Daily Log" header
            if daily_text.startswith("#"):
                lines = daily_text.split("\n", 1)
                daily_text = lines[1] if len(lines) > 1 else ""
            if daily_text.strip():
                parts.append(f"\n## 今日對話紀錄\n## {daily_text.strip()}")

    # 7. FTS5 recall（查 default + shared）
    try:
        from src.memory.recall import recall
        results = recall("_default", query, k=3, include_shared=True)
        if results:
            recall_lines = ["\n## 相關歷史記憶"]
            for r in results:
                recall_lines.append(f"- [{r.date}] {r.title}: {r.body[:100]}")
            parts.append("\n".join(recall_lines))
    except Exception:
        pass

    # 8. Wiki RAG（shared wiki）
    try:
        from src.wiki.engine import WikiEngine
        engine = WikiEngine()
        wiki_result = await engine.query(query, use_rag=False)
        if wiki_result.get("results"):
            wiki_lines = ["\n## 知識庫參考"]
            for r in wiki_result["results"][:3]:
                wiki_lines.append(f"### {r['title']}\n{r['snippet'][:200]}")
            parts.append("\n".join(wiki_lines))
    except Exception:
        pass

    # 9. Skills 清單
    try:
        from src.skills.registry import SkillRegistry
        registry = SkillRegistry()
        registry.auto_discover("src.skills.internal")
        skills = registry.list_skills()
        if skills:
            skill_lines = ["\n## 可用技能（/skill_id 觸發）"]
            for s in skills[:10]:
                skill_lines.append(f"- /{s['skill_id']} — {s['description'][:40]}")
            parts.append("\n".join(skill_lines))
    except Exception:
        pass

    # 10. Session history
    context_str = session.get_context()
    if context_str:
        parts.append(f"\n{context_str}")

    return "\n\n".join(parts)


# ── 自然語言路由 ─────────────────────────────────────────


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """主對話處理：Planner 六層路由 + Wiki RAG + memory。

    路由層級：
      L1: /reset → 清空 session
      L2: /skill_id args → 直接執行 Skill
      L3: keyword → Planner 路由（Skill 或 Wiki）
      L4: 預設 → Wiki RAG → Gemini fallback → 兜底
    """
    text = update.message.text.strip()
    user_id = update.effective_user.id

    # ── 白名單檢查（只擋自然語言對話，指令不擋）──
    if not _is_authorized(user_id):
        log.warning("⛔ Unauthorized user=%s msg=%s", user_id, text[:50])
        await update.message.reply_text(
            f"🔒 自然語言對話需授權。\n\n"
            f"你的 Chat ID：`{user_id}`\n"
            f"請將此 ID 加入 `.env` 的 `ADMIN_CHAT_IDS` 後重啟 Bot。",
            parse_mode="Markdown",
        )
        return

    session = session_manager.get_or_create(user_id)
    current_agent = session.current_agent
    agent_info = AVAILABLE_AGENTS[current_agent]

    # 記錄 user 這輪
    session.add_turn("user", text)
    log.info("📨 user=%s agent=%s msg=%s", user_id, current_agent, text[:100])

    # ── 自動 consolidate：每天首次對話時蒸餾前一天 ──
    await _auto_consolidate_if_needed()

    # ── Reaction: 👀 收到 + 立即 typing ──
    await _set_reaction(update.message, "👀")
    try:
        await context.bot.send_chat_action(chat_id=update.message.chat_id, action="typing")
    except Exception:
        pass

    # ── L1: /reset → 清空 session ──
    if text.lower() in ("/reset", "重置"):
        session.clear_history()
        await _set_reaction(update.message, "👍")
        await update.message.reply_text("🔄 對話已重置。")
        return

    # ── L2: /skill_id [args] → 直接執行 Skill ──
    if text.startswith("/") and not text.startswith("//"):
        parts = text[1:].split(maxsplit=1)
        skill_id = parts[0].lower()
        skill_args = parts[1] if len(parts) > 1 else ""
        result = await _execute_skill_by_id(skill_id, skill_args)
        if result is not None:
            result = _clean_output(result)
            session.add_turn("agent", result)
            await _set_reaction(update.message, "👍")
            header = f"{agent_info['emoji']} [{current_agent}-agent]\n"
            await update.message.reply_text(header + result, parse_mode="Markdown", disable_web_page_preview=True)
            return

    # ── L3: keyword → Planner 路由 ──
    from src.agent.planner import route, IntentType
    plan = route(text)

    if plan.intent == IntentType.SKILL and plan.skill_id:
        reply = await _execute_skill_by_id(plan.skill_id, text)
        if reply:
            reply = _clean_output(reply)
            session.add_turn("agent", reply)
            await _set_reaction(update.message, "👍")
            header = f"{agent_info['emoji']} [{current_agent}-agent]\n"
            await update.message.reply_text(header + reply, parse_mode="Markdown", disable_web_page_preview=True)
            return

    if plan.intent == IntentType.TEAM:
        # 團隊派工 — 走 A2ARouter
        reply = await _handle_team_dispatch(text, update, context)
        if reply:
            reply = _clean_output(reply)
            session.add_turn("agent", reply)
            await _set_reaction(update.message, "👍")
            header = f"🤝 [team]\n"
            await update.message.reply_text(header + reply, disable_web_page_preview=True)
            return

    if plan.intent == IntentType.WIKI:
        # Wiki 查詢不再攔截，統一走 L4 agent_loop 的 search_wiki tool
        pass

    # ── Reaction: 🔥 處理中 + 持續 typing ──
    await _set_reaction(update.message, "🔥")
    done = asyncio.Event()
    timer_task = asyncio.create_task(
        _keep_action_alive(update.message.chat_id, "typing", done, context.bot)
    )

    try:
        reply: str | None = None

        # ── L4: 雙模式對話 ──
        if session.is_default_mode:
            # === Default 模式：ReAct Agent Loop ===
            gemini_key = os.getenv("GEMINI_API_KEY", "") or os.getenv("LLM_PROVIDER", "")
            if gemini_key:
                try:
                    from src.llm.context_builder import build_default_system_prompt
                    from src.llm.agent_loop import agent_loop
                    import src.llm.tools  # 確保 tools 已註冊

                    system_prompt = await build_default_system_prompt(query=text, session=session)
                    result = await agent_loop(
                        user_message=text,
                        system_prompt=system_prompt,
                        session_history=None,  # context_builder 已含 history
                        max_iterations=5,
                    )
                    reply = result.text
                    if reply:
                        log.info("  ✅ Agent Loop reply (%d chars, %d iterations, %d tools)",
                                 len(reply), result.iterations, len(result.tool_calls_log))
                except Exception as e:
                    log.error("  ❌ Agent Loop error: %s", e)
                    # Fallback 到純文字 simple_chat
                    try:
                        from src.llm.chat import simple_chat
                        reply = await simple_chat(text, system=system_prompt if 'system_prompt' in dir() else "")
                    except Exception:
                        reply = None
            else:
                reply = (
                    f"🔄 echo: {text}\n\n"
                    "💡 開啟 AI：填入 GEMINI_API_KEY 或設定 LLM_PROVIDER\n"
                    "或用 `/agents` 切換到 Agent 分身（需 Agent CLI）"
                )
        else:
            # === Agent 模式：Agent CLI ===
            agent_name = session.agent_name
            if is_cli_available():
                log.debug("  → Agent CLI (%s)...", agent_name)
                try:
                    reply = await agent_cli_chat(text, agent_id=agent_name)
                    if reply:
                        log.info("  ✅ CLI reply (%d chars)", len(reply))
                except Exception as e:
                    log.error("  ❌ CLI error: %s", e)
                    reply = None
                if not reply:
                    reply = "⚠️ Agent CLI 無回應（可能超時），請重試。"
            else:
                reply = (
                    f"⚠️ **{agent_name}-agent** 需要 Agent CLI\n\n"
                    "安裝任一即可：\n"
                    "• agy: `irm https://antigravity.google/cli/install.ps1 | iex`\n"
                    "• kiro-cli: `npm i -g kiro-cli && kiro-cli login`\n"
                    "• claude: `npm i -g @anthropic-ai/claude-cli`\n\n"
                    "請先用 `/agents` 切回 🚀 Ark Agent。"
                )

        # ── 回覆 + 記憶 + Reaction ──
        if reply:
            reply = _clean_output(reply)
            if len(reply) > 3000:
                reply = reply[-3000:]
            session.add_turn("agent", reply)
            # 對話記錄寫入 memory/daily（不寫 knowledge/raw）
            try:
                from src.memory.daily_log import write_daily_log
                task_id = f"msg-{update.message.message_id}"
                conversation = f"User: {text[:200]}\nAgent: {reply[:500]}"
                if session.is_default_mode:
                    asyncio.create_task(
                        write_daily_log("_default", task_id, conversation)
                    )
                else:
                    agent_name = session.agent_name or current_agent
                    asyncio.create_task(
                        write_daily_log(f"{agent_name}-agent", task_id, conversation)
                    )
            except Exception as e:
                log.warning("daily_log failed: %s", e)
            # 更新 recent.md（最近 5 輪對話，供下次啟動時注入 system prompt）
            try:
                _update_recent(session)
            except Exception as e:
                log.warning("recent.md update failed: %s", e)
            await _set_reaction(update.message, "👍")
            # Header
            if session.is_default_mode:
                header = "🚀 [Ark Agent]\n"
            else:
                agent_name = session.agent_name
                info = AVAILABLE_AGENTS.get(agent_name, {})
                header = f"{info.get('emoji', '🤖')} [{agent_name}-agent]\n"
            full_text = header + reply
            for i in range(0, len(full_text), 4000):
                await update.message.reply_text(full_text[i:i+4000])
            log.info("  📤 sent reply to user=%s (%d chars)", user_id, len(reply))
        else:
            await _set_reaction(update.message, "💔")
            await update.message.reply_text("⚠️ 抱歉，我暫時無法回應，請稍後再試。")
            log.error("  💔 no reply for user=%s msg=%s", user_id, text[:100])

    except Exception as e:
        log.error("handle_message error: %s", e)
        await _set_reaction(update.message, "💔")
        await update.message.reply_text(f"⚠️ 處理失敗：{type(e).__name__}")
    finally:
        done.set()
        timer_task.cancel()


# ── Output 清理（對齊 ai-team-agent）─────────────────────

_ANSI_RE = re.compile(r"\x1b\[[0-9;]*m|\x1b\[\?[0-9]*[hl]|\x1b\[[0-9]*[A-Z]")

_TOOL_LINE_PREFIXES = (
    "Searching the web", "Reading content from", "Fetching URL",
    "Fetching ", "(using tool:", "✓ Found", "✓ Read",
    "- Completed in", "- Found", "- Read",
    "⏺ ", "┃ ", "│ ", "├ ", "└ ",
    "Running ", "Executed ", "Created ", "Updated ",
    "Tool call:", "Function:", "Calling tool",
)
_TOOL_LINE_RE = re.compile(
    r"^\s*[✓✗●◉⏺]\s+(Found|Read|Completed|Fetched|Searching|Writing|Created)"
    r"|^\s*\d+\s*(file|match)"
)


def _clean_output(raw: str) -> str:
    """從 Agent CLI 輸出提取最終結論，過濾工具過程 + ANSI codes。

    策略：
    1. 有 [DONE] 標記 → 用 summary
    2. 有 reply() 工具輸出 → 提取 reply 內容
    3. 否則從尾部反向掃描，找最後一段「非工具過程」的文字
    """
    # 清 ANSI
    text = _ANSI_RE.sub("", raw)
    # 清殘留 [0m 等
    text = re.sub(r"\[(?:\d+;)*\d*m", "", text)
    # 清 CLI '> ' 引用前綴
    text = re.sub(r"^>\s?", "", text, flags=re.MULTILINE)

    # 策略 1: [DONE] 標記
    done_match = re.search(r"\[DONE\]\s*summary=(.+)", text)
    if done_match:
        return done_match.group(1).strip()

    # 策略 2: reply() 工具呼叫
    reply_matches = re.findall(
        r'reply\s*\(\s*(?:text\s*=\s*)?["\'](.+?)["\']',
        text, re.DOTALL
    )
    if reply_matches:
        return reply_matches[-1].strip()

    # 策略 3: 從尾部提取結論段落
    lines = text.splitlines()
    conclusion_lines: list[str] = []
    found_content = False
    consecutive_tool_lines = 0

    for line in reversed(lines):
        stripped = line.strip()
        if not stripped and not found_content:
            continue
        is_tool_line = (
            any(stripped.startswith(p) for p in _TOOL_LINE_PREFIXES)
            or bool(_TOOL_LINE_RE.match(stripped))
        )
        if is_tool_line:
            consecutive_tool_lines += 1
            if found_content and consecutive_tool_lines >= 3:
                break  # 連續 3 行工具噪音才視為進入工具區段
            continue

        consecutive_tool_lines = 0  # 重置計數
        found_content = True
        # Strip '> ' prompt prefix
        if line.startswith("> "):
            line = line[2:]
        conclusion_lines.append(line)

    conclusion_lines.reverse()
    result = "\n".join(conclusion_lines).strip()

    # Fallback: 結果太短，做基礎清理取尾部
    if len(result) < 20 and len(text.strip()) > 20:
        cleaned_lines = []
        for l in lines:
            s = l.strip()
            if not s:
                cleaned_lines.append("")
                continue
            if any(s.startswith(p) for p in _TOOL_LINE_PREFIXES):
                continue
            if _TOOL_LINE_RE.match(s):
                continue
            if l.startswith("> "):
                l = l[2:]
            cleaned_lines.append(l)
        result = "\n".join(cleaned_lines).strip()
        if len(result) > 2000:
            result = result[-2000:]

    # 清理多餘空行
    result = re.sub(r"\n{3,}", "\n\n", result)
    return result


async def _execute_skill_by_id(skill_id: str, args: str = "") -> str | None:
    """根據 skill_id 直接執行對應 Skill。回傳結果字串或 None（不認識的 skill）。"""
    skill_id = skill_id.lower().strip()

    if skill_id == "news":
        return await _handle_news()

    if skill_id == "summarize":
        if not args:
            return "⚠️ 用法：/summarize <要摘要的文字>"
        try:
            from src.skills.internal.summarize import SummarizeSkill
            skill = SummarizeSkill()
            result = await skill.execute({"content": args, "max_length": 200})
            if result.success:
                return f"📝 摘要：\n{result.data['summary']}\n\n（原文 {result.data['original_length']} 字）"
            return f"⚠️ {result.error}"
        except Exception as e:
            return f"⚠️ 摘要失敗: {e}"

    if skill_id == "translate":
        if not args:
            return "⚠️ 用法：/translate <要翻譯的文字>"
        try:
            from src.skills.internal.translate import TranslateSkill
            skill = TranslateSkill()
            # 解析目標語言（預設 en）
            parts = args.rsplit(" to ", 1)
            text_to_translate = parts[0]
            target_lang = parts[1].strip() if len(parts) > 1 else "en"
            result = await skill.execute({"text": text_to_translate, "target_lang": target_lang})
            if result.success:
                return f"🌐 翻譯（→ {result.data['target_lang']}）：\n{result.data['translated']}"
            return f"⚠️ {result.error}"
        except Exception as e:
            return f"⚠️ 翻譯失敗: {e}"

    if skill_id == "wiki":
        if not args:
            return "⚠️ 用法：/wiki <查詢關鍵字>"
        try:
            from src.wiki.engine import WikiEngine
            engine = WikiEngine()
            result = await engine.query(args, use_rag=True)
            if result.get("answer"):
                return result["answer"]
            elif result.get("results"):
                lines = [f"📚 找到 {len(result['results'])} 筆："]
                for r in result["results"][:5]:
                    lines.append(f"• {r['title']}：{r['snippet'][:80]}")
                return "\n".join(lines)
            return "📚 知識庫中沒有找到相關內容。"
        except Exception as e:
            return f"⚠️ Wiki 查詢失敗: {e}"

    if skill_id == "ingest":
        try:
            from src.wiki.engine import WikiEngine
            engine = WikiEngine()
            ingested = engine.ingest()
            return f"✅ 匯入完成：{len(ingested)} 篇\n" + "\n".join(f"• {f}" for f in ingested)
        except Exception as e:
            return f"⚠️ Ingest 失敗: {e}"

    return None  # 不認識的 skill_id


# ── Memory Search ─────────────────────────────────────────


def _search_memory(agent_id: str, query: str, max_results: int = 3) -> str | None:
    """搜尋 Agent 的歷史記憶，回傳相關 context 或 None。"""
    from pathlib import Path
    memory_dir = Path(f"agents/{agent_id}-agent/knowledge/raw")
    if not memory_dir.exists():
        return None

    keywords = query.lower().split()
    matches: list[str] = []

    for md in sorted(memory_dir.glob("*.md"), reverse=True)[:20]:  # 最近 20 筆
        content = md.read_text(encoding="utf-8")
        if any(kw in content.lower() for kw in keywords):
            # 提取任務和結果
            lines = content.split("\n")
            task_line = ""
            result_lines: list[str] = []
            in_result = False
            for line in lines:
                if line.startswith("## 任務"):
                    in_result = False
                elif line.startswith("## 結果"):
                    in_result = True
                elif in_result and line.strip():
                    result_lines.append(line)
                elif not in_result and line.strip() and not line.startswith("---") and not line.startswith("user_id"):
                    task_line = line
            if result_lines:
                matches.append(f"[{md.stem}] {task_line}\n{''.join(result_lines[:3])}")

        if len(matches) >= max_results:
            break

    return "\n\n".join(matches) if matches else None


# ── Reaction Helper ───────────────────────────────────────


def _update_recent(session) -> None:
    """將 session 最近 5 輪對話寫入 memory/recent.md，供下次 system prompt 注入。"""
    from pathlib import Path

    recent_path = Path("memory/recent.md")
    recent_path.parent.mkdir(parents=True, exist_ok=True)

    # 取最近 5 輪
    turns = session.history[-10:]  # 5 輪 = 10 條（user + agent 各一）
    if not turns:
        return

    lines = ["# 最近對話\n"]
    for turn in turns:
        prefix = "👤 User" if turn.role == "user" else "🤖 Agent"
        content = turn.content[:300]
        lines.append(f"{prefix}: {content}\n")

    recent_path.write_text("\n".join(lines), encoding="utf-8")


# ── 自動 consolidate ─────────────────────────────────────

_consolidate_done_today: str = ""  # 記錄今天是否已跑過


async def _auto_consolidate_if_needed() -> None:
    """每天首次對話時，自動蒸餾前一天 daily log → memory.md。"""
    global _consolidate_done_today
    from datetime import datetime, timedelta

    today = datetime.now().strftime("%Y-%m-%d")
    if _consolidate_done_today == today:
        return  # 今天已經跑過

    # 檢查昨天有沒有 daily log
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    yesterday_log = Path(f"memory/daily/{yesterday}.md")
    if not yesterday_log.exists():
        _consolidate_done_today = today
        return  # 昨天沒 log，跳過

    # 非同步執行 consolidate（不阻塞對話）
    try:
        from src.memory.consolidate import consolidate
        result = await consolidate("_default")
        if result.get("status") == "updated":
            log.info("Auto-consolidate: memory.md updated from %s", yesterday)
        _consolidate_done_today = today
    except Exception as e:
        log.warning("Auto-consolidate failed: %s", e)
        _consolidate_done_today = today  # 避免重複嘗試


async def _set_reaction(message, emoji: str) -> None:
    """設定訊息 Reaction（靜默失敗）。"""
    try:
        from telegram import ReactionTypeEmoji
        await message.set_reaction([ReactionTypeEmoji(emoji=emoji)])
    except Exception:
        pass  # Reaction API 不可用時靜默跳過


async def _keep_action_alive(chat_id: int, action: str, done: asyncio.Event, bot) -> None:
    """持續送 chat action 直到 done 被 set（每 4 秒一次）。"""
    try:
        while not done.is_set():
            await bot.send_chat_action(chat_id=chat_id, action=action)
            try:
                await asyncio.wait_for(done.wait(), timeout=4.0)
            except asyncio.TimeoutError:
                pass
    except (asyncio.CancelledError, Exception):
        pass


# ── Skill 處理 ───────────────────────────────────────────


async def _handle_news() -> str | None:
    """新聞 Skill 快速路徑。"""
    try:
        from src.skills.internal.news import NewsSkill
        skill = NewsSkill()
        result = await skill.execute({"max_items": 5})
        if result.success:
            lines = [f"📰 *{result.data['source']}* — {result.data['count']} 則\n"]
            for i, art in enumerate(result.data["articles"], 1):
                lines.append(f"{i}. [{art['title']}]({art['url']}) (⬆️{art['score']})")
            return "\n".join(lines)
        return f"⚠️ {result.error}"
    except Exception as e:
        return f"⚠️ 新聞抓取失敗: {e}"


# ── Team Dispatch ────────────────────────────────────────


async def _handle_team_dispatch(text: str, update: Update, context: ContextTypes.DEFAULT_TYPE) -> str | None:
    """團隊派工處理 — 走 A2ARouter.dispatch()。

    只有 team.yaml 存在（_TEAM_MODE=1）時才啟用。
    """
    import os
    if os.getenv("_TEAM_MODE") != "1":
        return "⚠️ 團隊模式未啟用（需要 team.yaml）"

    # 清除關鍵字前綴
    clean_text = text
    for prefix in ("派工", "assign", "分配", "指派", "@pm"):
        clean_text = clean_text.replace(prefix, "").strip()

    if not clean_text:
        return "⚠️ 請描述要派工的任務，例如：`派工 分析老虎機競品數據`"

    try:
        from src.coordinator.a2a.router import A2ARouter
        from src.coordinator.a2a.graph import TaskGraph
        from src.coordinator.a2a.shared_memory import SharedMemory
        from src.coordinator.a2a.discovery import AgentDiscovery
        from src.coordinator.a2a.protocol import TaskHandoff
        from datetime import datetime, timezone

        # 組裝 Router（每次重建，讀最新的 profiles）
        graph = TaskGraph()
        memory = SharedMemory()
        discovery = AgentDiscovery(memory)

        # spawn_fn — 本地 Agent 用 agent_cli_chat
        async def _spawn_fn(agent_name: str, message: str) -> str | None:
            from src.agent.cli import agent_cli_chat
            return await agent_cli_chat(message, agent_id=agent_name.replace("-agent", ""))

        router = A2ARouter(graph, memory, discovery, spawn_fn=_spawn_fn)

        # 建立 TaskHandoff
        now = datetime.now(timezone.utc)
        task_id = now.strftime("%Y-%m-%d") + f"_{now.hour:02d}{now.minute:02d}_{clean_text[:20].replace(' ', '-')}"
        handoff = TaskHandoff(
            task_id=task_id,
            from_agent="user",
            to_agent="auto",
            title=clean_text,
            context="",
        )

        # Discovery 匹配
        target = discovery.match(handoff)
        handoff.to_agent = target

        # 通知使用者已派工
        await update.message.reply_text(f"📋 已派工給 **{target}**\n任務：{clean_text[:100]}", parse_mode="Markdown")

        # Dispatch（非同步執行）
        await router.dispatch(handoff)

        # 等結果（從 shared memory 讀）
        task_path = memory.base / "tasks" / f"{task_id}.md"
        if task_path.exists():
            content = task_path.read_text(encoding="utf-8")
            if "## Output" in content:
                output_section = content.split("## Output")[-1].strip()
                return f"✅ {target} 完成：\n\n{output_section[:2000]}"

        return f"⏳ 任務 {task_id} 已提交給 {target}，可用 /board 查看進度"

    except ImportError:
        return "⚠️ coordinator 模組未安裝"
    except Exception as e:
        log.error("Team dispatch error: %s", e)
        return f"⚠️ 派工失敗：{e}"


# ── /assign /board Commands ──────────────────────────────


async def cmd_assign(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/assign <描述> — 派工給團隊 Agent。"""
    text = update.message.text.strip()
    # 移除 /assign 前綴
    task_desc = text[len("/assign"):].strip() if text.startswith("/assign") else text

    if not task_desc:
        await update.message.reply_text(
            "📋 用法：`/assign <任務描述>`\n\n"
            "範例：\n"
            "• `/assign 分析老虎機競品數據`\n"
            "• `/assign review 主迴圈 performance`",
            parse_mode="Markdown",
        )
        return

    reply = await _handle_team_dispatch(f"派工 {task_desc}", update, context)
    if reply:
        # _handle_team_dispatch 已經回覆了中間訊息，這裡只處理最終結果
        if not reply.startswith("📋"):  # 避免重複
            await update.message.reply_text(reply)


async def cmd_board(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/board — 查看任務看板。"""
    from pathlib import Path

    tasks_dir = Path("knowledge/shared/tasks")
    if not tasks_dir.exists() or not list(tasks_dir.glob("*.md")):
        await update.message.reply_text("📋 任務看板為空\n\n使用 `/assign <描述>` 派工", parse_mode="Markdown")
        return

    lines = ["📋 **任務看板**\n"]
    status_emoji = {
        "pending": "⏳",
        "running": "🔄",
        "completed": "✅",
        "failed": "❌",
    }

    tasks = sorted(tasks_dir.glob("*.md"), reverse=True)[:10]  # 最近 10 筆
    for task_file in tasks:
        content = task_file.read_text(encoding="utf-8")
        # 解析 frontmatter
        status = "pending"
        assignee = ""
        title = task_file.stem
        for line in content.splitlines():
            if line.startswith("status:"):
                status = line.split(":", 1)[1].strip()
            elif line.startswith("assigned_to:"):
                assignee = line.split(":", 1)[1].strip()
            elif line.startswith("# "):
                title = line[2:].strip()

        emoji = status_emoji.get(status, "❓")
        assignee_str = f" → {assignee}" if assignee else ""
        lines.append(f"{emoji} {title[:40]}{assignee_str}")

    await update.message.reply_text("\n".join(lines), parse_mode="Markdown")
