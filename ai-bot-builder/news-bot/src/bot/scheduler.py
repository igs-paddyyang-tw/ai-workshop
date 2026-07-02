"""排程模組 — 每日自動發送科技日報 + 台灣遊戲情報日報。"""
import json
import logging
from pathlib import Path

import yaml
from telegram.ext import ContextTypes

from src.skills.registry import SkillRegistry
from src.llm import gemini_chat
from src.bot.handlers import (
    _item_priority, _load_tw_game_keywords,
    _TECH_PROMPT, _GAME_PROMPT, _CATEGORY_MAP,
)

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
    """每日排程：抓新聞 → 分類 → LLM 結構化 → 渲染兩份日報 → 推送。"""
    if not _subscribed_chats:
        logger.warning("排程觸發但無訂閱者，跳過")
        return

    logger.info("⏰ 每日排程觸發，推送給 %d 位訂閱者", len(_subscribed_chats))

    from src.bot.handlers import _registry
    if not _registry:
        logger.error("排程：Skill 系統未就緒")
        return

    # Step 1: 分別抓取科技來源和遊戲來源
    tech_result = await _registry.invoke("news_scraper", {
        "config_path": "config/news_sources.yaml",
        "source_key": "sources",
    })
    game_result = await _registry.invoke("news_scraper", {
        "config_path": "config/news_sources.yaml",
        "source_key": "game_sources",
    })

    # Step 2: 收集素材
    tech_items = []
    game_items = []

    if tech_result.success:
        for cat, items in tech_result.data.get("categories", {}).items():
            for item in items[:10]:
                desc = item.get("description", "")
                if desc == item["title"]:
                    desc = ""
                tech_items.append({
                    "category": cat,
                    "title": item["title"],
                    "description": desc,
                    "url": item.get("url", ""),
                    "source": item.get("source", ""),
                })

    if game_result.success:
        tw_keywords = _load_tw_game_keywords()
        for cat, items in game_result.data.get("categories", {}).items():
            for item in items:
                desc = item.get("description", "")
                if desc == item["title"]:
                    desc = ""
                source_name = item.get("source", "")
                entry = {
                    "category": cat,
                    "title": item["title"],
                    "description": desc,
                    "url": item.get("url", ""),
                    "source": source_name,
                }
                # 官網來源：全部收錄
                if "官網" in source_name or "官方" in source_name:
                    game_items.append(entry)
                    continue
                # RSS 來源：只收錄命中關鍵字的
                text_to_match = (item["title"] + " " + desc).lower()
                if any(kw.lower() in text_to_match for kw in tw_keywords):
                    game_items.append(entry)

    if not tech_items and not game_items:
        logger.warning("排程：今日無新聞")
        return

    # Step 3: 分別 LLM 結構化
    # 科技日報
    tech_articles = await _call_llm(_TECH_PROMPT, tech_items[:12])
    if not tech_articles:
        tech_articles = _fallback(tech_items[:5])

    # 台灣遊戲情報
    game_items.sort(key=lambda x: _item_priority(x, tw_keywords))
    game_articles = await _call_llm(_GAME_PROMPT, game_items[:20])
    if not game_articles:
        game_articles = _fallback(game_items[:5])

    # Step 4: 渲染兩份 HTML + 推送
    reports = []

    if tech_articles:
        r = await _registry.invoke("news_renderer", {
            "articles": tech_articles[:6],
            "report_title": "科技日報",
        })
        if r.success:
            reports.append(("🔬 每日科技日報", r.data["path"], r.data["filename"], r.data.get("count", 0)))

    if game_articles:
        r = await _registry.invoke("news_renderer", {
            "articles": game_articles[:6],
            "report_title": "台灣遊戲情報",
        })
        if r.success:
            reports.append(("🎮 台灣遊戲情報", r.data["path"], r.data["filename"], r.data.get("count", 0)))

    # Step 5: 推送給所有訂閱者
    for chat_id in _subscribed_chats:
        for caption_prefix, path, filename, count in reports:
            try:
                await context.bot.send_document(
                    chat_id=chat_id,
                    document=open(path, "rb"),
                    filename=filename,
                    caption=f"{caption_prefix}（{count} 則）— 自動排程推送",
                )
            except Exception as e:
                logger.error("排程推送失敗 chat_id=%s, file=%s: %s", chat_id, filename, e)
        logger.info("排程：已推送 %d 份日報到 chat_id=%s", len(reports), chat_id)


# ── LLM 結構化 ───────────────────────────────────────────────


async def _call_llm(prompt_template: str, raw_items: list[dict]) -> list[dict]:
    """通用 LLM 結構化。用 index 綁定真實 URL。"""
    if not gemini_chat.is_available() or not raw_items:
        return []

    lines = []
    for i, item in enumerate(raw_items):
        line = f"[{i}] [{item['category']}] {item['title']} (來源: {item['source']})"
        if item.get("description"):
            line += f"\n    描述: {item['description']}"
        lines.append(line)
    material = "\n".join(lines)

    try:
        response = await gemini_chat.chat(
            message=prompt_template + material,
            system_prompt="你是專業的新聞編輯，只回傳 JSON。",
        )
        if not response:
            return []

        text = response.strip()
        if text.startswith("```"):
            resp_lines = text.split("\n")
            text = "\n".join(resp_lines[1:])
        if text.endswith("```"):
            text = text[:-3]
        text = text.strip()

        data = json.loads(text)
        cards = data.get("cards", [])

        # 用 index 綁定真實 URL
        for card in cards:
            idx = card.pop("index", None)
            if idx is not None and isinstance(idx, int) and 0 <= idx < len(raw_items):
                card["url"] = raw_items[idx].get("url", "")
                if not card.get("source"):
                    card["source"] = raw_items[idx].get("source", "")

        return cards
    except Exception as e:
        logger.error("排程 LLM 結構化失敗: %s", e)
        return []


def _fallback(raw_items: list[dict]) -> list[dict]:
    """Fallback 格式化。"""
    articles = []
    for item in raw_items:
        cat_name = _CATEGORY_MAP.get(item["category"], "科技綜合")
        articles.append({
            "topic": cat_name,
            "title": item["title"],
            "what": f"「{item['title']}」— 來自 {item['source']} 的最新報導。",
            "why": "值得關注的動態。",
            "summary": item["title"][:15],
            "tags": [{"icon": "📰", "text": cat_name}],
            "source": item.get("source", ""),
            "url": item.get("url", ""),
        })
    return articles
