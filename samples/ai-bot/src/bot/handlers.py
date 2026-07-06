"""Bot 指令處理 — Inline Button Agent 切換 + Memory 管理。

對話流程：
  /agents → Inline Keyboard → 選 Agent → 對話 → 自動寫 memory
"""
from __future__ import annotations

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

    if plan.intent == IntentType.WIKI:
        # Wiki 查詢優先
        pass  # 繼續到下面的 Wiki RAG 段落

    # ── Reaction: 🔥 處理中 ──
    await _set_reaction(update.message, "🔥")
    await update.message.chat.send_action("typing")

    # ── L4: CLI → Wiki RAG → Gemini fallback ──
    reply: str | None = None
    memory_context: str | None = None

    # 4a. Agent CLI（優先 — 有裝 kiro-cli 時用完整 .kiro/ 配置）
    if is_cli_available():
        log.debug("  → trying Agent CLI...")
        try:
            reply = await agent_cli_chat(text, agent_id=current_agent)
            if reply:
                log.info("  ✅ CLI reply (%d chars)", len(reply))
        except Exception as e:
            log.error("  ❌ CLI error: %s", e)
            reply = None

    # 4b. Wiki RAG（CLI 沒回或沒裝時）
    if not reply:
        log.debug("  → trying Wiki RAG...")
        try:
            from src.wiki.engine import WikiEngine
            engine = WikiEngine(agent_id=current_agent)
            wiki_result = await engine.query(text, use_rag=True)
            if wiki_result.get("answer"):
                reply = wiki_result["answer"]
                log.info("  ✅ Wiki RAG reply (%d chars, sources=%s)", len(reply), wiki_result.get("sources", []))
        except Exception as e:
            log.error("  ❌ Wiki error: %s", e)

    # 4c. Memory Search（引用歷史記憶，注入 Gemini context）
    if not reply:
        try:
            memory_context = _search_memory(current_agent, text)
        except Exception:
            memory_context = None

    # 4d. Gemini API fallback
    if not reply:
        gemini_key = os.getenv("GEMINI_API_KEY", "")
        if gemini_key:
            log.debug("  → trying Gemini API...")
            try:
                from src.llm.gemini_chat import gemini_chat
                soul = _load_soul(current_agent)
                context_str = session.get_context()
                # 注入記憶（如果有）
                memory_str = f"\n\n## 相關歷史記憶\n{memory_context}" if memory_context else ""
                full_system = f"{soul}{memory_str}\n\n{context_str}" if context_str else f"{soul}{memory_str}"
                reply = await gemini_chat(text, system=full_system)
                if reply:
                    log.info("  ✅ Gemini reply (%d chars)", len(reply))
            except Exception as e:
                log.error("  ❌ Gemini error: %s", e)
                reply = f"⚠️ 錯誤: {e}"
        else:
            reply = (
                f"🔄 echo: {text}\n\n"
                "💡 開啟 AI：填入 GEMINI_API_KEY 或安裝 kiro-cli"
            )

    # ── 回覆 + 記憶 + Reaction ──
    if reply:
        reply = _clean_output(reply)
        session.add_turn("agent", reply)
        await save_memory(current_agent, user_id, text, reply)
        await _set_reaction(update.message, "👍")
        header = f"{agent_info['emoji']} [{current_agent}-agent]\n"
        await update.message.reply_text(header + reply)
        log.info("  📤 sent reply to user=%s (%d chars)", user_id, len(reply))
    else:
        await _set_reaction(update.message, "💔")
        header = f"{agent_info['emoji']} [{current_agent}-agent]\n"
        await update.message.reply_text(header + "⚠️ 抱歉，我暫時無法回應，請稍後再試。")
        log.error("  💔 no reply for user=%s msg=%s", user_id, text[:100])


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
    r"|^\s*━+\s*$"
    r"|^\s*─+\s*$"
    r"|^```"
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

    for line in reversed(lines):
        stripped = line.strip()
        if not stripped and not found_content:
            continue
        is_tool_line = (
            any(stripped.startswith(p) for p in _TOOL_LINE_PREFIXES)
            or bool(_TOOL_LINE_RE.match(stripped))
        )
        if is_tool_line:
            if found_content:
                break
            continue
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
