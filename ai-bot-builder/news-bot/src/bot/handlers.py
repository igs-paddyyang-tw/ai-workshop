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
    """歡迎訊息。"""
    await update.message.reply_text(
        "🤖 AI Agent Bot 就緒！\n\n"
        "直接打字跟我說話，我會用 Agent CLI 幫你做事。\n\n"
        "💡 試試看：\n"
        "• 「今天有什麼科技新聞」→ 自動抓取產日報\n"
        "• 「幫我寫一個計算機 Skill」→ 自動產出程式碼\n"
        "• 任何問題 → Agent CLI 深度回答\n\n"
        "📋 指令：\n"
        "  /daily — 手動觸發日報\n"
        "  /skills — 列出已載入 Skills"
    )


async def cmd_skills(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """列出 Skills。"""
    skills = _registry.list_skills() if _registry else []
    lines = [f"📦 {len(skills)} 個 Skills\n"]
    for s in skills:
        lines.append(f"  • {s['id']} — {s['description'][:40]}")
    await update.message.reply_text("\n".join(lines))


async def cmd_daily(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """手動觸發科技日報：scrape → LLM 結構化 → render → 發送 HTML。"""
    if not _registry:
        await update.message.reply_text("❌ Skill 系統未就緒")
        return

    await update.message.reply_text("📡 抓取新聞中...")

    # Step 1: 抓取
    result = await _registry.invoke("news_scraper", {"config_path": "config/news_sources.yaml"})
    if not result.success:
        await update.message.reply_text(f"❌ 抓取失敗：{result.error[:200]}")
        return

    # Step 2: 收集原始素材（帶描述）
    raw_items = []
    for cat, items in result.data.get("categories", {}).items():
        for item in items[:5]:
            desc = item.get("description", "")
            # 如果 description 只是重複標題，標記為空
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
        await update.message.reply_text("📭 今日無新聞")
        return

    # Step 3: 用 Gemini API 結構化為日報卡片（優先使用有描述的素材）
    # 排序：有 description 的放前面
    raw_items.sort(key=lambda x: (0 if x.get("description") else 1))
    articles = await _structure_news_with_llm(raw_items[:10])

    # 如果 LLM 失敗，fallback 到基本格式
    if not articles:
        articles = _fallback_structure(raw_items[:5])

    # Step 4: 渲染 HTML
    await update.message.reply_text("🎨 渲染日報中...")
    render_result = await _registry.invoke("news_renderer", {"articles": articles[:5]})
    if render_result.success:
        path = render_result.data["path"]
        await update.message.reply_document(
            document=open(path, "rb"),
            filename=Path(path).name,
            caption=f"📰 科技日報（{render_result.data.get('count', 0)} 則）",
        )
    else:
        await update.message.reply_text(f"❌ 渲染失敗：{render_result.error[:200]}")


# ── 日報 LLM 結構化 ──────────────────────────────────────────

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
      "tags": [
        {"icon": "emoji", "text": "標籤文字（4字內）"}
      ]
    }
  ]
}

以下是今日新聞素材：
"""


async def _structure_news_with_llm(raw_items: list[dict]) -> list[dict]:
    """用 Gemini API 將原始新聞結構化為日報卡片。"""
    if not gemini_chat.is_available():
        return []

    # 組裝素材 — 包含 description
    lines = []
    for item in raw_items:
        line = f"- [{item['category']}] {item['title']} (來源: {item['source']})"
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
            logger.warning("LLM 結構化：Gemini 回傳空字串")
            return []

        # 清理回應（移除可能的 markdown code block 標記）
        text = response.strip()
        if text.startswith("```"):
            # 移除第一行 (```json 或 ```)
            lines = text.split("\n")
            text = "\n".join(lines[1:])
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
        })
    return articles


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
