"""Memory Consolidate — 蒸餾 daily log → memory.md 持久事實。"""
from __future__ import annotations

import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Callable, Awaitable

from coordinator.db.models import get_async_db, fetch_all

log = logging.getLogger("memory.consolidate")

_CONSOLIDATE_PROMPT = """\
你是一位記憶管理員。根據以下 Agent 的近期 daily log，蒸餾出持久性事實。

規則：
1. 只保留 **反覆出現的模式、重要決策、關鍵經驗**
2. 刪除一次性事件、瑣碎細節
3. 輸出格式為 Markdown 列表（每項 ≤ 30 字）
4. 總長 ≤ 2000 字元
5. 如果沒有值得蒸餾的內容，回覆「（無新增持久事實）」

Agent: {agent}
現有 memory.md 內容：
{existing_memory}

---
近期 daily log（最近 14 天）：
{daily_logs}
"""

MAX_MEMORY_CHARS = 2000


async def consolidate(
    agent_name: str,
    agents_dir: Path | None = None,
    gemini_fn: Callable[[str, str], Awaitable[str | None]] | None = None,
    days: int = 14,
) -> str:
    """蒸餾 daily → memory.md。

    Args:
        agent_name: Agent 名稱
        agents_dir: agents 根目錄
        gemini_fn: LLM 函式 (prompt, system) → str
        days: 蒸餾最近幾天

    Returns:
        蒸餾結果（新 memory.md 內容）
    """
    if agents_dir is None:
        agents_dir = Path("agents")

    memory_dir = agents_dir / agent_name / "memory"
    memory_file = memory_dir / "memory.md"
    memory_dir.mkdir(parents=True, exist_ok=True)

    # 讀取現有 memory.md
    existing = ""
    if memory_file.exists():
        existing = memory_file.read_text(encoding="utf-8")

    # 從 DB 取得近期 daily log
    cutoff = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
    conn = await get_async_db()
    try:
        rows = await fetch_all(
            conn,
            "SELECT date, title, body FROM memory_entries WHERE agent=? AND date>=? ORDER BY date",
            (agent_name, cutoff),
        )
    finally:
        await conn.close()

    if not rows:
        log.info("No recent entries for %s, skip consolidate", agent_name)
        return existing

    daily_logs = "\n\n".join(
        f"[{r['date']}] {r['title']}\n{r['body']}" for r in rows
    )

    # LLM 蒸餾
    if gemini_fn:
        try:
            prompt = _CONSOLIDATE_PROMPT.format(
                agent=agent_name,
                existing_memory=existing[:1000],
                daily_logs=daily_logs[:4000],
            )
            result = await gemini_fn(
                prompt,
                "你是記憶管理員，只輸出蒸餾後的 memory.md 內容。",
            )
            if result and "（無新增持久事實）" not in result:
                new_memory = _merge_memory(existing, result)
                memory_file.write_text(new_memory, encoding="utf-8")
                log.info("Consolidated %s: %d chars", agent_name, len(new_memory))
                return new_memory
        except Exception as e:
            log.warning("LLM consolidate failed: %s", e)

    # Fallback：附加最近摘要
    summary_lines = [f"- [{r['date']}] {r['title'][:50]}" for r in rows[-5:]]
    fallback = "\n".join(summary_lines)
    new_memory = _merge_memory(existing, fallback)
    memory_file.write_text(new_memory, encoding="utf-8")
    log.info("Consolidated %s (fallback): %d chars", agent_name, len(new_memory))
    return new_memory


def _merge_memory(existing: str, new_content: str) -> str:
    """合併既有 memory 與新蒸餾內容，保持在上限內。"""
    if not existing.strip():
        header = "# 持久事實\n\n> 上限 2000 tokens。蒸餾自 daily log。\n\n"
        return (header + new_content.strip())[:MAX_MEMORY_CHARS]

    # 如果新內容是完整替換（LLM 已合併）
    if new_content.startswith("# ") or new_content.startswith("- "):
        merged = existing.rstrip() + "\n\n## 最新蒸餾\n\n" + new_content.strip()
    else:
        merged = existing.rstrip() + "\n\n" + new_content.strip()

    # 超過上限時截斷舊內容
    if len(merged) > MAX_MEMORY_CHARS:
        merged = merged[-MAX_MEMORY_CHARS:]
        # 找到第一個完整行
        first_newline = merged.find("\n")
        if first_newline > 0:
            merged = merged[first_newline + 1:]

    return merged
