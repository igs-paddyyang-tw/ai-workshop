"""情節記憶：任務結束後自動追加 daily log。"""
from __future__ import annotations

import logging
from datetime import datetime
from pathlib import Path
from typing import Callable, Awaitable

from .indexer import index_entry

log = logging.getLogger("memory.daily_log")

# LLM 摘要 prompt
_SUMMARY_PROMPT = """\
你是一個簡潔的記錄員。根據以下任務對話，產出一筆 daily log 條目。

格式：
## HH:MM [{agent}] task:{task_id}
- **做了**：（一句話）
- **決定**：（如有）
- **踩坑**：（如有）
- **後續**：（如有）
- tags: tag1, tag2

規則：
- 總長 ≤ 150 字（不含標題行）
- 沒有的欄位直接省略
- tags 用英文逗號分隔，2-5 個關鍵詞

任務對話：
{conversation}
"""

# Fallback 模板
_FALLBACK_TEMPLATE = (
    "## {time} [{agent}] task:{task_id}\n"
    "- **做了**：完成任務（摘要生成失敗）\n"
    "- tags: task\n"
)


async def write_daily_log(
    agent_name: str,
    task_id: str,
    conversation: str,
    agents_dir: Path | None = None,
    gemini_fn: Callable[[str, str], Awaitable[str | None]] | None = None,
) -> str:
    """寫入 daily log（檔案 + DB FTS5）。

    Args:
        agent_name: Agent 名稱（如 coder-agent）
        task_id: 任務識別碼
        conversation: 任務對話摘要
        agents_dir: agents 根目錄
        gemini_fn: LLM 摘要函式 (prompt, system) → str

    Returns:
        寫入的 entry 文字
    """
    if agents_dir is None:
        agents_dir = Path("agents")

    memory_dir = agents_dir / agent_name / "memory" / "daily"
    memory_dir.mkdir(parents=True, exist_ok=True)

    today = datetime.now().strftime("%Y-%m-%d")
    daily_file = memory_dir / f"{today}.md"
    now_time = datetime.now().strftime("%H:%M")

    # LLM 摘要
    entry = await _generate_summary(agent_name, task_id, conversation, now_time, gemini_fn)

    # Append 到 daily 檔案
    with open(daily_file, "a", encoding="utf-8") as f:
        if not daily_file.exists() or daily_file.stat().st_size == 0:
            f.write(f"# {today} Daily Log\n\n")
        f.write(entry + "\n\n")

    # 寫入 DB（FTS5 自動索引）
    title_line = entry.splitlines()[0] if entry else f"{now_time} [{agent_name}]"
    tags = _extract_tags_from_entry(entry)
    await index_entry(
        agent=agent_name,
        source="daily",
        date=today,
        title=title_line,
        body=entry,
        tags=tags,
    )

    log.info("Daily log: %s (%d chars)", agent_name, len(entry))
    return entry


async def _generate_summary(
    agent_name: str,
    task_id: str,
    conversation: str,
    now_time: str,
    gemini_fn: Callable[[str, str], Awaitable[str | None]] | None = None,
) -> str:
    """使用 LLM 生成摘要，失敗時 fallback。"""
    if gemini_fn:
        try:
            prompt = _SUMMARY_PROMPT.format(
                agent=agent_name,
                task_id=task_id,
                conversation=conversation[:3000],
            )
            result = await gemini_fn(
                prompt,
                "你是記錄員，只輸出 markdown 條目，不加其他說明。",
            )
            if result and len(result.strip()) > 20:
                return result.strip()
        except Exception as e:
            log.warning("LLM summary failed: %s", e)

    # Fallback
    return _FALLBACK_TEMPLATE.format(
        time=now_time,
        agent=agent_name,
        task_id=task_id,
    )


def _extract_tags_from_entry(entry: str) -> str:
    """從 entry 中提取 tags。"""
    for line in entry.splitlines():
        stripped = line.strip()
        if stripped.startswith("- tags:") or stripped.startswith("tags:"):
            return stripped.split(":", 1)[1].strip()
    return ""
