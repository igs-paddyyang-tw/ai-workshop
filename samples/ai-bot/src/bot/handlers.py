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
from src.agent.memory import save_memory
from src.agent.cli import AVAILABLE_AGENTS, is_cli_available, agent_cli_chat

log = __import__("logging").getLogger("bot.handlers")

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
    session.clear_history()  # 重新開始，清空舊對話
    agent = AVAILABLE_AGENTS[session.current_agent]
    mode = "🧠 Agent CLI" if is_cli_available() else "⚡ Gemini API"
    await update.message.reply_text(
        f"🤖 AI Agent 已就緒！\n\n"
        f"• 模式：{mode}\n"
        f"• Agent：{agent['emoji']} {agent['name']}\n\n"
        "📌 /agents → 選擇 Agent\n"
        "💬 直接打字 → 對話\n"
        "📋 /help → 指令清單"
    )


async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "📋 指令清單：\n\n"
        "/start — 歡迎訊息\n"
        "/agents — 🔘 選擇 Agent（按鈕）\n"
        "/mode — 查看執行模式\n"
        "/history — 查看對話歷史\n"
        "/help — 本清單\n\n"
        "💬 直接輸入文字即可對話"
    )


async def cmd_agents(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """顯示 Inline Keyboard 選擇 Agent。"""
    user_id = update.effective_user.id
    session = session_manager.get_or_create(user_id)
    current = session.current_agent

    def btn(agent_id):
        info = AVAILABLE_AGENTS[agent_id]
        prefix = "→ " if current == agent_id else ""
        return InlineKeyboardButton(
            f"{prefix}{info['emoji']} {agent_id.capitalize()}",
            callback_data=f"switch_agent:{agent_id}",
        )

    keyboard = [
        [btn("admin"), btn("pm")],
        [btn("ai-dev"), btn("coder")],
        [btn("qa"), btn("data")],
        [btn("market"), btn("report")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    agent = AVAILABLE_AGENTS[current]
    await update.message.reply_text(
        f"當前：{agent['emoji']} {agent['name']}\n\n選擇要對話的 Agent：",
        reply_markup=reply_markup,
    )


async def callback_switch_agent(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Inline Button 回調 — 切換 Agent。"""
    query = update.callback_query
    await query.answer()

    agent_id = query.data.split(":")[1]  # "switch_agent:news" → "news"
    user_id = query.from_user.id

    if agent_id not in AVAILABLE_AGENTS:
        await query.edit_message_text("❌ 無效的 Agent")
        return

    session = session_manager.switch_agent(user_id, agent_id)
    info = AVAILABLE_AGENTS[agent_id]
    await query.edit_message_text(
        f"✅ 已切換到 {info['emoji']} **{info['name']}**\n\n"
        f"{info['desc']}\n\n"
        f"現在開始對話吧！",
        parse_mode="Markdown",
    )


async def cmd_mode(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """顯示當前執行模式。"""
    if is_cli_available():
        await update.message.reply_text(
            "🧠 **Agent CLI 模式**\n\n"
            "• kiro-cli 已安裝 ✅\n"
            "• .kiro/ 配置全部生效\n"
            "• 對話由 kiro-cli 驅動",
            parse_mode="Markdown",
        )
    else:
        has_key = "✅" if os.getenv("GEMINI_API_KEY") else "❌"
        await update.message.reply_text(
            f"⚡ **Gemini API 模式**\n\n"
            f"• Gemini Key: {has_key}\n"
            f"• SOUL.md 作為 system prompt\n\n"
            "升級：`npm i -g kiro-cli && kiro-cli login`",
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

    # ── 呼叫 Gemini ──
    try:
        from src.llm.gemini_chat import gemini_chat
        reply = await gemini_chat(text, system=system_prompt)
    except Exception as e:
        log.error("Gemini chat error: %s", e)
        reply = f"⚠️ Gemini 錯誤：{e}"

    if reply:
        if len(reply) > 3000:
            reply = reply[-3000:]
        session.add_turn("agent", reply)
        await save_memory(current_agent, user_id, text, reply)
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
            wiki_lines = ["\n## 知識庫參考"]
            for r in wiki_result["results"][:3]:
                wiki_lines.append(f"### {r['title']}\n{r['snippet'][:200]}")
            parts.append("\n".join(wiki_lines))
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
    session = session_manager.get_or_create(user_id)
    current_agent = session.current_agent
    agent_info = AVAILABLE_AGENTS[current_agent]

    # 記錄 user 這輪
    session.add_turn("user", text)
    log.info("📨 user=%s agent=%s msg=%s", user_id, current_agent, text[:100])

    # ── Reaction: 👀 收到 ──
    await _set_reaction(update.message, "👀")

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
            await save_memory(current_agent, user_id, text, result)
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
            await save_memory(current_agent, user_id, text, reply)
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
            await save_memory(current_agent, user_id, text, reply)
            await _set_reaction(update.message, "👍")
            header = f"🤝 [team]\n"
            await update.message.reply_text(header + reply, disable_web_page_preview=True)
            return

    if plan.intent == IntentType.WIKI:
        # Wiki 查詢優先
        pass  # 繼續到下面的 Wiki RAG 段落

    # ── Reaction: 🔥 處理中 + 持續 typing ──
    await _set_reaction(update.message, "🔥")
    done = asyncio.Event()
    timer_task = asyncio.create_task(
        _keep_action_alive(update.message.chat_id, "typing", done, context.bot)
    )

    try:
        # ── L4: 自然對話 = Agent CLI（不 fallback Gemini）──
        # 強制 Gemini 請用 /chat 指令
        reply: str | None = None

        # 4a. Agent CLI（唯一自然對話路徑）
        if is_cli_available():
            log.debug("  → Agent CLI...")
            try:
                reply = await agent_cli_chat(text, agent_id=current_agent)
                if reply:
                    log.info("  ✅ CLI reply (%d chars)", len(reply))
            except Exception as e:
                log.error("  ❌ CLI error: %s", e)
                reply = None

        # 4b. CLI 不可用 → 提示使用 /chat
        if not reply and not is_cli_available():
            gemini_key = os.getenv("GEMINI_API_KEY", "")
            if gemini_key:
                reply = (
                    "💡 Agent CLI 未安裝，自然對話不可用。\n\n"
                    "替代方案：\n"
                    "• `/chat 你的問題` — 強制使用 Gemini API\n"
                    "• 安裝 kiro-cli：`npm i -g kiro-cli && kiro-cli login`"
                )
            else:
                reply = (
                    f"🔄 echo: {text}\n\n"
                    "💡 開啟 AI：填入 GEMINI_API_KEY 或安裝 kiro-cli"
                )

        # 4c. CLI 有回但為空（timeout 等）→ 簡短提示
        if not reply and is_cli_available():
            reply = "⚠️ Agent CLI 無回應（可能超時），請重試或用 `/chat` 走 Gemini。"

        # ── 回覆 + 記憶 + Reaction ──
        if reply:
            reply = _clean_output(reply)
            # 長度截斷（避免 TG 洗版）
            if len(reply) > 3000:
                reply = reply[-3000:]
            session.add_turn("agent", reply)
            await save_memory(current_agent, user_id, text, reply)
            await _set_reaction(update.message, "👍")
            header = f"{agent_info['emoji']} [{current_agent}-agent]\n"
            # 分段發送（TG 單則上限 4096）
            full_text = header + reply
            for i in range(0, len(full_text), 4000):
                await update.message.reply_text(full_text[i:i+4000])
            log.info("  📤 sent reply to user=%s (%d chars)", user_id, len(reply))
        else:
            await _set_reaction(update.message, "💔")
            header = f"{agent_info['emoji']} [{current_agent}-agent]\n"
            await update.message.reply_text(header + "⚠️ 抱歉，我暫時無法回應，請稍後再試。")
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
    """從 kiro-cli 輸出提取最終結論，過濾工具過程 + ANSI codes。

    策略：
    1. 有 [DONE] 標記 → 用 summary
    2. 有 reply() 工具輸出 → 提取 reply 內容
    3. 否則從尾部反向掃描，找最後一段「非工具過程」的文字
    """
    # 清 ANSI
    text = _ANSI_RE.sub("", raw)
    # 清殘留 [0m 等
    text = re.sub(r"\[(?:\d+;)*\d*m", "", text)
    # 清 kiro-cli '> ' 引用前綴
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
