"""情節記憶：任務結束後自動追加 daily log。"""
from __future__ import annotations

import logging
from datetime import datetime
from pathlib import Path

log = logging.getLogger(__name__)

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

# Fallback 模板（LLM 不可用時）
_FALLBACK_TEMPLATE = "## {time} [{agent}] task:{task_id}\n- **做了**：完成任務（摘要生成失敗）\n"


async def write_daily_log(
    agent_name: str,
    task_id: str,
    conversation: str,
    agents_dir: Path | None = None,
) -> Path:
    """寫入 daily log，回傳寫入的檔案路徑。

    Args:
        agent_name: Agent 名稱（如 coder-agent）
        task_id: 任務識別碼
        conversation: 任務對話摘要（輸入 + 輸出的關鍵部分）
        agents_dir: agents 根目錄，預設為專案內的 agents/
    """
    if agents_dir is None:
        agents_dir = Path(__file__).resolve().parents[2] / "agents"

    memory_dir = agents_dir / agent_name / "memory" / "daily"
    memory_dir.mkdir(parents=True, exist_ok=True)

    today = datetime.now().strftime("%Y-%m-%d")
    daily_file = memory_dir / f"{today}.md"
    now_time = datetime.now().strftime("%H:%M")

    # 嘗試 LLM 摘要
    entry = await _generate_summary(agent_name, task_id, conversation, now_time)

    # Append 到 daily 檔案
    with open(daily_file, "a", encoding="utf-8") as f:
        if daily_file.stat().st_size == 0:
            f.write(f"# {today} Daily Log\n\n")
        f.write(entry + "\n\n")

    log.info("Daily log written: %s (%d chars)", daily_file.name, len(entry))
    return daily_file


async def _generate_summary(
    agent_name: str,
    task_id: str,
    conversation: str,
    now_time: str,
) -> str:
    """使用 LLM 生成摘要，失敗時 fallback。"""
    try:
        from src.llm.gemini_chat import gemini_chat

        prompt = _SUMMARY_PROMPT.format(
            agent=agent_name,
            task_id=task_id,
            conversation=conversation[:3000],  # 截斷避免過長
        )
        result = await gemini_chat(
            prompt=prompt,
            system="你是記錄員，只輸出 markdown 條目，不加其他說明。",
        )
        if result and len(result.strip()) > 20:
            return result.strip()
    except Exception as e:
        log.warning("LLM summary failed for %s: %s", agent_name, e)

    # Fallback
    return _FALLBACK_TEMPLATE.format(
        time=now_time,
        agent=agent_name,
        task_id=task_id,
    )
