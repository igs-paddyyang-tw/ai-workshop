"""Context Builder：統一組裝 system prompt。"""
from __future__ import annotations

import logging
from pathlib import Path

log = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parents[2]


async def build_default_system_prompt(query: str = "", session=None) -> str:
    """組裝 Default 模式（Ark Agent）的 system prompt。

    8 層：SOUL + BRAIN + USER + memory + recent + recall + wiki + skills + tool instructions
    """
    parts: list[str] = []

    # 1. SOUL.md
    soul_path = BASE_DIR / ".kiro" / "steering" / "SOUL.md"
    if soul_path.exists():
        parts.append(soul_path.read_text(encoding="utf-8"))

    # 2. BRAIN.md（去 frontmatter）
    brain_path = BASE_DIR / ".kiro" / "steering" / "BRAIN.md"
    if brain_path.exists():
        content = brain_path.read_text(encoding="utf-8")
        if content.startswith("---"):
            _, _, content = content.split("---", 2)
        parts.append(content.strip())

    # 3. USER.md
    user_path = BASE_DIR / ".kiro" / "steering" / "USER.md"
    if user_path.exists():
        parts.append(user_path.read_text(encoding="utf-8"))

    # 4. memory/memory.md
    memory_path = BASE_DIR / "memory" / "memory.md"
    if memory_path.exists():
        content = memory_path.read_text(encoding="utf-8")
        if content.strip() and "（尚無記錄）" not in content:
            parts.append(f"\n## 持久記憶\n{content[:1500]}")

    # 5. memory/recent.md
    recent_path = BASE_DIR / "memory" / "recent.md"
    if recent_path.exists():
        content = recent_path.read_text(encoding="utf-8")
        if content.strip() and "（尚無記錄）" not in content:
            parts.append(f"\n## 最近經驗\n{content[:1500]}")

    # 6. FTS5 recall（相關歷史）
    if query:
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

    # 7. Wiki + Web Search（搜尋流程指引）
    parts.append(
        "\n## 知識庫與搜尋\n"
        "查詢事實/比較/評價的流程（強制，不可跳過）：\n"
        "1. 先用 search_wiki tool 搜尋知識庫\n"
        "2. 知識庫查無 → 用 web_search tool 搜尋外部資訊\n"
        "3. web_search 有回傳內容 → 直接根據回傳內容整理回答，附上 🔗 來源\n"
        "4. 兩者都確實無結果（web_search 回傳含 'Error' 或 '無結果'）→ 回覆「📚 知識庫與外部搜尋皆無相關資料」\n"
        "重要：web_search 回傳的文字就是搜尋結果，直接使用它來回答使用者。\n"
        "需要寫入知識時使用 save_to_wiki tool（使用者明確要求時）。"
    )

    # 8. Skills 清單
    try:
        from src.llm.tool_registry import registry
        tool_desc = registry.list_descriptions()
        if tool_desc:
            parts.append(f"\n## 可用工具\n{tool_desc}")
    except Exception:
        pass

    # 9. Skill 清單（SKILL.md 名稱）
    try:
        from src.llm.tools.skill_executor import _list_skill_names
        skills = _list_skill_names()
        if skills:
            parts.append(f"\n## 可執行的 Skills\n使用 execute_skill tool 載入：\n- " + "\n- ".join(skills[:15]))
    except Exception:
        pass

    # 10. Session history
    if session:
        context_str = session.get_context()
        if context_str:
            parts.append(f"\n{context_str}")

    return "\n\n".join(parts)
