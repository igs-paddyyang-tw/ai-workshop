"""Telegram Bot handlers — 自然語言進 Agent CLI。"""
import json
import logging
from pathlib import Path

import yaml
from telegram import Update
from telegram.ext import ContextTypes

from src.skills.registry import SkillRegistry
from src.conversation.planner import ConversationPlanner, PlanAction
from src.llm import gemini_chat

logger = logging.getLogger(__name__)

# ── 載入系統提詞 ──────────────────────────────────────────────

_PROMPTS_PATH = Path(__file__).resolve().parents[2] / "config" / "llm_prompts.yaml"


def _load_prompts() -> dict[str, str]:
    defaults = {"default": "你是智能助理，用繁體中文回答。"}
    if not _PROMPTS_PATH.exists():
        return defaults
    try:
        data = yaml.safe_load(_PROMPTS_PATH.read_text(encoding="utf-8"))
        return {"default": data.get("default_system_prompt", defaults["default"]).strip()}
    except Exception:
        return defaults


_SYSTEM_PROMPTS = _load_prompts()

# ── 元件注入 ──────────────────────────────────────────────────

_registry: SkillRegistry | None = None
_planner: ConversationPlanner | None = None


def init_components(registry: SkillRegistry) -> None:
    """初始化共用元件（由 bot/main.py 呼叫）。"""
    global _registry, _planner
    _registry = registry
    _planner = ConversationPlanner(skill_ids=[s["id"] for s in registry.list_skills()])


# ── 指令 Handlers ─────────────────────────────────────────────


async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """歡迎訊息 + 自動訂閱每日日報。"""
    from src.bot.scheduler import register_chat
    chat_id = update.effective_chat.id
    register_chat(chat_id)
    logger.info("已註冊 chat_id=%s 接收每日日報", chat_id)

    await update.message.reply_text(
        "🤖 AI Agent Bot 就緒！\n\n"
        "直接打字跟我說話，我會用 Agent CLI 幫你做事。\n\n"
        "💡 試試看：\n"
        "• 「今天有什麼科技新聞」→ 自動抓取產日報\n"
        "• 「幫我寫一個計算機 Skill」→ 自動產出程式碼\n"
        "• 任何問題 → Agent CLI 深度回答\n\n"
        "📋 指令：\n"
        "  /daily — 手動觸發日報\n"
        "  /skills — 列出已載入 Skills\n\n"
        "⏰ 已訂閱每日 09:00 科技日報自動推送！"
    )


async def cmd_skills(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """列出 Skills。"""
    skills = _registry.list_skills() if _registry else []
    lines = [f"📦 {len(skills)} 個 Skills\n"]
    for s in skills:
        lines.append(f"  • {s['id']} — {s['description'][:40]}")
    await update.message.reply_text("\n".join(lines))


async def cmd_daily(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """手動觸發日報：產出科技日報 + 台灣遊戲情報日報（兩份獨立檔案）。"""
    if not _registry:
        await update.message.reply_text("❌ Skill 系統未就緒")
        return

    await update.message.reply_text("📡 抓取新聞中...")

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
        for cat, items in game_result.data.get("categories", {}).items():
            for item in items[:10]:
                desc = item.get("description", "")
                if desc == item["title"]:
                    desc = ""
                game_items.append({
                    "category": cat,
                    "title": item["title"],
                    "description": desc,
                    "url": item.get("url", ""),
                    "source": item.get("source", ""),
                })
    if not tech_items and not game_items:
        await update.message.reply_text("📭 今日無新聞")
        return

    # Step 3: 分別用 LLM 結構化兩份日報
    await update.message.reply_text("🎨 AI 編輯整理中...")

    # 科技日報
    tech_articles = await _structure_tech_report(tech_items[:12])
    if not tech_articles:
        tech_articles = _fallback_structure(tech_items[:5])

    # 台灣遊戲情報日報
    tw_keywords = _load_tw_game_keywords()
    game_items.sort(key=lambda x: _item_priority(x, tw_keywords))
    game_articles = await _structure_game_report(game_items[:20])
    if not game_articles:
        game_articles = _fallback_structure(game_items[:5])

    # 回填 URL
    if tech_articles:
        _backfill_urls(tech_articles, tech_items)
    if game_articles:
        _backfill_urls(game_articles, game_items)

    # Step 4: 分別渲染兩份 HTML
    sent_count = 0

    # 科技日報
    if tech_articles:
        r1 = await _registry.invoke("news_renderer", {
            "articles": tech_articles[:6],
            "report_title": "科技日報",
        })
        if r1.success:
            await update.message.reply_document(
                document=open(r1.data["path"], "rb"),
                filename=r1.data["filename"],
                caption=f"🔬 科技日報（{r1.data.get('count', 0)} 則）",
            )
            sent_count += 1

    # 台灣遊戲情報日報
    if game_articles:
        r2 = await _registry.invoke("news_renderer", {
            "articles": game_articles[:6],
            "report_title": "台灣遊戲情報",
        })
        if r2.success:
            await update.message.reply_document(
                document=open(r2.data["path"], "rb"),
                filename=r2.data["filename"],
                caption=f"🎮 台灣遊戲情報（{r2.data.get('count', 0)} 則）",
            )
            sent_count += 1

    if sent_count == 0:
        await update.message.reply_text("📭 今日無新聞可產出")


# ── 日報 LLM 結構化 ──────────────────────────────────────────

_CATEGORY_MAP = {
    "tech_general": "科技綜合",
    "ai_focus": "AI 焦點",
    "dev_tools": "開發工具",
    "hardware": "硬體趨勢",
    "general": "科技綜合",
    "tw_game": "台灣遊戲",
}


def _load_tw_game_keywords() -> list[str]:
    """從 config 載入台灣博弈遊戲關鍵字。"""
    config_path = Path("config/news_sources.yaml")
    if not config_path.exists():
        return []
    try:
        data = yaml.safe_load(config_path.read_text(encoding="utf-8"))
        return data.get("tw_game_keywords", [])
    except Exception:
        return []


def _item_priority(item: dict, tw_keywords: list[str]) -> int:
    """排序優先度：0=官網公告, 1=品牌關鍵字命中, 2=台灣遊戲分類, 3=有描述, 4=其他。"""
    title_lower = item.get("title", "").lower()
    desc_lower = item.get("description", "").lower()
    source_lower = item.get("source", "").lower()
    text = title_lower + " " + desc_lower

    # 官網來源 → 最高優先
    official_sources = ["官網", "星城online", "豪神", "包你發", "老子有錢", "天狐宴", "金爸爸", "滿貫大亨"]
    for os_name in official_sources:
        if os_name in source_lower:
            return 0

    # 台灣博弈品牌關鍵字命中 → 次高
    for kw in tw_keywords:
        if kw.lower() in text:
            return 1

    # 台灣遊戲分類 → 中高
    if item.get("category") == "tw_game":
        return 2

    # 有描述 → 中等
    if item.get("description"):
        return 3

    return 4

_TECH_PROMPT = """你是科技日報編輯。請根據以下國際科技新聞素材，撰寫結構化日報卡片。

重要規則：
1. 只使用素材中提供的真實資訊，禁止編造不存在的數據或細節
2. 如果素材只有標題沒有描述，就根據標題如實概述，不要臆測具體數字或細節
3. 挑選最有價值的 5 則新聞
4. 用繁體中文撰寫
5. "what" 欄位要基於素材中的 description 來寫，如果沒有 description 就簡述標題含義
6. "why" 欄位簡述該新聞的潛在影響
7. "url" 欄位必須保留素材中提供的原始網址，不可省略或修改

回傳純 JSON（不要 markdown code block），格式：
{
  "cards": [
    {
      "topic": "分類名稱（AI 焦點 / 資安 / 開發工具 / 科技綜合）",
      "title": "新聞標題（精煉中文，15 字內）",
      "what": "發生了什麼（2-3 句，可用 <span class=\\"hl\\">重點</span> 標記關鍵字）",
      "why": "為什麼重要（1-2 句話說明影響）",
      "summary": "一句話總結（10 字內）",
      "source": "來源名稱",
      "url": "原始新聞網址",
      "tags": [{"icon": "emoji", "text": "標籤文字（4字內）"}]
    }
  ]
}

以下是今日科技新聞素材：
"""

_GAME_PROMPT = """你是台灣遊戲市場情報編輯。請根據以下台灣遊戲新聞素材，撰寫結構化日報卡片。

特別關注品牌：金好運、包你發、老子有錢、星城Online、豪神、明星三缺一（明星3缺1）、鉅網、IGS、滿貫大亨、天狐宴、金爸爸，以及其他博弈/手遊相關新聞。

優先收錄規則（按重要性排序）：
1. 來自官網的公告（星城Online、豪神、包你發、老子有錢、天狐宴、金爸爸、滿貫大亨）必須優先收錄
2. 上述品牌在巴哈姆特或 4Gamers 的新聞報導次之
3. 其他台灣遊戲市場相關新聞補充

重要規則：
1. 只使用素材中提供的真實資訊，禁止編造不存在的數據或細節
2. 挑選最有價值的 5-6 則遊戲新聞
3. 用繁體中文撰寫
4. "what" 欄位要基於素材中的 description 來寫，如果沒有 description 就簡述標題含義
5. "why" 欄位從市場競爭、玩家影響或產業趨勢角度分析
6. "url" 欄位必須保留素材中提供的原始網址，不可省略或修改
7. "source" 欄位要標明來自哪個來源（如：星城Online 官網、巴哈姆特 GNN 等）

回傳純 JSON（不要 markdown code block），格式：
{
  "cards": [
    {
      "topic": "分類名稱（手遊動態 / 博弈遊戲 / 遊戲產業 / 活動情報 / 官方公告）",
      "title": "新聞標題（精煉中文，15 字內）",
      "what": "發生了什麼（2-3 句，可用 <span class=\\"hl\\">重點</span> 標記關鍵字）",
      "why": "為什麼重要（1-2 句話，市場/競品/玩家角度）",
      "summary": "一句話總結（10 字內）",
      "source": "來源名稱",
      "url": "原始新聞網址",
      "tags": [{"icon": "emoji", "text": "標籤文字（4字內）"}]
    }
  ]
}

以下是今日台灣遊戲新聞素材：
"""


async def _structure_tech_report(raw_items: list[dict]) -> list[dict]:
    """科技日報 LLM 結構化。"""
    return await _call_llm_structure(_TECH_PROMPT, raw_items)


async def _structure_game_report(raw_items: list[dict]) -> list[dict]:
    """台灣遊戲情報 LLM 結構化。"""
    return await _call_llm_structure(_GAME_PROMPT, raw_items)


async def _call_llm_structure(prompt_template: str, raw_items: list[dict]) -> list[dict]:
    """通用 LLM 結構化呼叫。"""
    if not gemini_chat.is_available() or not raw_items:
        return []

    # 組裝素材 — 包含 description 和 URL
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
            message=prompt_template + material,
            system_prompt="你是專業的新聞編輯，只回傳 JSON。",
        )
        if not response:
            logger.warning("LLM 結構化：Gemini 回傳空字串")
            return []

        # 清理回應
        text = response.strip()
        if text.startswith("```"):
            resp_lines = text.split("\n")
            text = "\n".join(resp_lines[1:])
        if text.endswith("```"):
            text = text[:-3]
        text = text.strip()

        data = json.loads(text)
        cards = data.get("cards", [])
        logger.info("LLM 結構化成功：%d 張卡片", len(cards))
        return cards if cards else []
    except json.JSONDecodeError as e:
        logger.error("LLM JSON 解析失敗: %s | 原始回應前200字: %s", e, response[:200] if response else "")
        return []
    except Exception as e:
        logger.error("LLM 結構化異常: %s", e, exc_info=True)
        return []


def _fallback_structure(raw_items: list[dict]) -> list[dict]:
    """LLM 不可用時的 fallback：基本格式化。"""
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


def _backfill_urls(articles: list[dict], raw_items: list[dict]) -> None:
    """將原始 URL 回填到 LLM 產出的卡片（LLM 不一定會保留 URL）。"""
    # 建立標題→URL 的對照表
    title_url_map = {}
    for item in raw_items:
        if item.get("url"):
            # 用原始標題的前 20 字當 key（因為 LLM 可能翻譯或精簡標題）
            title_url_map[item["title"].lower()[:30]] = item["url"]
            # 也用來源名做 fallback matching
            key = f"{item['source']}_{item['title'][:15]}".lower()
            title_url_map[key] = item["url"]

    for article in articles:
        if article.get("url"):
            continue  # 已經有 URL 了

        # 嘗試用 source 名稱匹配
        source = article.get("source", "")
        matched = False
        for item in raw_items:
            if item.get("url") and item["source"] == source:
                # 檢查標題是否相關（簡單比對）
                if (item["title"][:10].lower() in article.get("title", "").lower() or
                    article.get("title", "")[:5] in item["title"]):
                    article["url"] = item["url"]
                    matched = True
                    break

        # 如果沒匹配到，按順序分配
        if not matched:
            for item in raw_items:
                if item.get("url") and item["url"] not in [a.get("url") for a in articles]:
                    article["url"] = item["url"]
                    break


# ── 自然語言主流程 ────────────────────────────────────────────


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """自然語言 → Planner → 做事。核心入口。"""
    msg = update.effective_message
    if not msg or not msg.text:
        return
    text = msg.text.strip()

    # 意圖路由
    plan = await _planner.plan(text)

    if plan.action == PlanAction.RESET:
        await msg.reply_text("🔄 已重置")
        return

    if plan.action == PlanAction.EXECUTE:
        # 執行 Skill
        result = await _registry.invoke(plan.skill_id, plan.params)
        if result.success:
            output = result.data.get("output") or result.data.get("code") or str(result.data)
            if len(output) > 4000:
                output = output[:3900] + "\n\n📎 已截斷"
            await msg.reply_text(output)
        else:
            await msg.reply_text(f"❌ {plan.skill_id} 失敗：{result.error[:200]}")
        return

    # ANSWER — 直接走 Agent CLI 對話
    wait_msg = await msg.reply_text("🤖 思考中...")
    result = await _registry.invoke("llm_cli", {"prompt": text, "mode": "chat"})
    if result.success:
        reply = result.data.get("output", "")
        backend = result.data.get("backend", "unknown")
        if len(reply) > 4000:
            reply = reply[:3900] + "\n\n📎 已截斷"
        reply += f"\n\n— 🤖 {backend} CLI"
        await wait_msg.edit_text(reply or "🤔 沒有回應")
    else:
        await wait_msg.edit_text(f"❌ {result.error[:300]}")
