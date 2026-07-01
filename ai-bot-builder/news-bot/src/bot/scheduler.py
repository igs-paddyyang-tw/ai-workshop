"""排程模組 — 每日自動發送科技日報。"""
import json
import logging
from pathlib import Path

from telegram.ext import ContextTypes

from src.skills.registry import SkillRegistry
from src.llm import gemini_chat
from src.bot.handlers import _backfill_urls

logger = logging.getLogger(__name__)

# ── 記錄要推送的 Chat IDs ─────────────────────────────────────

_subscribed_chats: set[int] = set()


def register_chat(chat_id: int) -> None:
    """註冊一個 chat_id 接收排程推送。"""
    _subscribed_chats.add(chat_id)


def get_subscribed_chats() -> set[int]:
    """取得所有已註冊的 chat_ids。"""
    return _subscribed_chats.copy()


# ── 排程 Job ──────────────────────────────────────────────────


async def scheduled_daily(context: ContextTypes.DEFAULT_TYPE) -> None:
    """每日排程：抓新聞 → LLM 結構化 → 渲染 → 推送到所有訂閱者。"""
    if not _subscribed_chats:
        logger.warning("排程觸發但無訂閱者，跳過")
        return

    logger.info("⏰ 每日排程觸發，推送給 %d 位訂閱者", len(_subscribed_chats))

    # 取得 handlers 裡的 registry
    from src.bot.handlers import _registry
    if not _registry:
        logger.error("排程：Skill 系統未就緒")
        return

    # Step 1: 抓取新聞
    result = await _registry.invoke("news_scraper", {"config_path": "config/news_sources.yaml"})
    if not result.success:
        logger.error("排程：抓取失敗 %s", result.error)
        return

    # Step 2: 收集素材
    raw_items = []
    for cat, items in result.data.get("categories", {}).items():
        for item in items[:5]:
            desc = item.get("description", "")
            if desc == item["title"]:
                desc = ""
            raw_items.append({
                "category": cat,
                "title": item["title"],
                "description": desc,
                "url": item.get("url", ""),
                "source": item.get("source", ""),
            })

    if not raw_items:
        logger.warning("排程：今日無新聞")
        return

    # Step 3: LLM 結構化
    raw_items.sort(key=lambda x: (0 if x.get("description") else 1))
    articles = await _structure_for_schedule(raw_items[:10])

    # 回填 URL
    if articles:
        _backfill_urls(articles, raw_items)

    if not articles:
        articles = _fallback_for_schedule(raw_items[:5])

    # Step 4: 渲染 HTML
    render_result = await _registry.invoke("news_renderer", {"articles": articles[:5]})
    if not render_result.success:
        logger.error("排程：渲染失敗 %s", render_result.error)
        return

    # Step 5: 推送給所有訂閱者
    path = render_result.data["path"]
    count = render_result.data.get("count", 0)

    for chat_id in _subscribed_chats:
        try:
            await context.bot.send_document(
                chat_id=chat_id,
                document=open(path, "rb"),
                filename=Path(path).name,
                caption=f"📰 每日科技日報（{count} 則）— 自動排程推送",
            )
            logger.info("排程：已推送到 chat_id=%s", chat_id)
        except Exception as e:
            logger.error("排程：推送失敗 chat_id=%s: %s", chat_id, e)


# ── LLM 結構化（排程用，同 handlers 邏輯）────────────────────

_CATEGORY_MAP = {
    "tech_general": "科技綜合",
    "ai_focus": "AI 焦點",
    "dev_tools": "開發工具",
    "hardware": "硬體趨勢",
    "general": "科技綜合",
}

_STRUCTURE_PROMPT = """你是科技日報編輯。請根據以下新聞素材，撰寫結構化日報卡片。

重要規則：
1. 只使用素材中提供的真實資訊，禁止編造不存在的數據或細節
2. 如果素材只有標題沒有描述，就根據標題如實概述，不要臆測具體數字或細節
3. 從提供的新聞中挑選最有價值的 5 則
4. 用繁體中文撰寫
5. "what" 欄位要基於素材中的 description 來寫，如果沒有 description 就簡述標題含義
6. "why" 欄位簡述該新聞的潛在影響
7. "url" 欄位必須保留素材中提供的原始網址，不可省略或修改

回傳純 JSON（不要 markdown code block），格式：
{
  "cards": [
    {
      "topic": "分類名稱（如：AI 焦點、開發工具、科技綜合、硬體趨勢、資安）",
      "title": "新聞標題（精煉中文，15 字內）",
      "what": "發生了什麼（2-3 句，基於素材的 description，可用 <span class=\\"hl\\">重點</span> 標記關鍵字）",
      "why": "為什麼重要（1-2 句話說明影響）",
      "summary": "一句話總結（10 字內）",
      "source": "來源名稱",
      "url": "原始新聞網址（直接複製素材中的網址）",
      "tags": [
        {"icon": "emoji", "text": "標籤文字（4字內）"}
      ]
    }
  ]
}

以下是今日新聞素材：
"""


async def _structure_for_schedule(raw_items: list[dict]) -> list[dict]:
    """LLM 結構化（排程版）。"""
    if not gemini_chat.is_available():
        return []

    lines = []
    for item in raw_items:
        line = f"- [{item['category']}] {item['title']} (來源: {item['source']})"
        if item.get("url"):
            line += f"\n  網址: {item['url']}"
        if item.get("description"):
            line += f"\n  描述: {item['description']}"
        lines.append(line)
    material = "\n".join(lines)

    try:
        response = await gemini_chat.chat(
            message=_STRUCTURE_PROMPT + material,
            system_prompt="你是專業的科技日報編輯，擅長將新聞素材轉化為精煉的中文日報卡片。只回傳 JSON。",
        )
        if not response:
            return []

        text = response.strip()
        if text.startswith("```"):
            lines_resp = text.split("\n")
            text = "\n".join(lines_resp[1:])
        if text.endswith("```"):
            text = text[:-3]
        text = text.strip()

        data = json.loads(text)
        return data.get("cards", [])
    except Exception as e:
        logger.error("排程 LLM 結構化失敗: %s", e)
        return []


def _fallback_for_schedule(raw_items: list[dict]) -> list[dict]:
    """Fallback 格式化。"""
    articles = []
    for item in raw_items:
        cat_name = _CATEGORY_MAP.get(item["category"], "科技綜合")
        articles.append({
            "topic": cat_name,
            "title": item["title"],
            "what": f"「{item['title']}」— 來自 {item['source']} 的最新報導。",
            "why": "值得關注的科技動態。",
            "summary": item["title"][:15],
            "tags": [{"icon": "📰", "text": cat_name}],
            "source": item.get("source", ""),
            "url": item.get("url", ""),
        })
    return articles
