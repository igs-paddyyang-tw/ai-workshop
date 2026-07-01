"""AI Workshop — 一鍵啟動完整平台。

Tier 感知：
  Tier 0 — 零設定：Skills + Wiki + API + Dashboard
  Tier 1 — TG Token：Bot 對話 + /agents + /assign + /board
  Tier 2 — Gemini Key：AI 對話 + RAG 問答
"""
from __future__ import annotations

import os
import threading
from pathlib import Path


def main() -> None:
    os.chdir(Path(__file__).parent)

    from dotenv import load_dotenv
    load_dotenv()

    # ── Tier 偵測 ──
    tg_token = os.getenv("TELEGRAM_BOT_TOKEN", "")
    gemini_key = os.getenv("GEMINI_API_KEY", "")

    tier = 0
    if tg_token:
        tier = 1
    if gemini_key:
        tier = 2

    print("═" * 55)
    print("  🤖 AI Workshop — 完整平台")
    print("═" * 55)
    print(f"  Tier 0: ✅ Skills + Wiki + API + Dashboard（永遠可用）")
    print(f"  Tier 1: {'✅' if tg_token else '⬚'} Telegram Bot {'（已設定）' if tg_token else '（填入 TELEGRAM_BOT_TOKEN 開啟）'}")
    print(f"  Tier 2: {'✅' if gemini_key else '⬚'} Gemini AI {'（已設定）' if gemini_key else '（填入 GEMINI_API_KEY 開啟）'}")
    print("═" * 55)

    # ── 初始化 Skills ──
    from src.skills.registry import SkillRegistry
    registry = SkillRegistry()
    count = registry.auto_discover("src.skills.internal")
    print(f"\n  📦 Skills 載入: {count} 個")

    # ── 初始化 Wiki ──
    from src.wiki.engine import WikiEngine
    engine = WikiEngine()
    wiki_files = list(Path("knowledge/raw").glob("*.md"))
    print(f"  📚 知識庫: {len(wiki_files)} 篇原始文件")

    # ── 啟動 Bot（Tier 1+）──
    if tg_token:
        from src.gateway.bot import create_app
        bot_app = create_app()

        def run_bot():
            import asyncio
            asyncio.run(bot_app.run_polling(drop_pending_updates=True))

        t = threading.Thread(target=run_bot, daemon=True)
        t.start()
        print(f"  🤖 Bot: polling 啟動")
    else:
        print(f"  ⚠️  無 TG Token → 僅 API 模式")

    # ── 啟動 API Server ──
    print(f"\n  🚀 啟動中...")
    print(f"     ├── Web API: http://localhost:8000")
    print(f"     ├── Dashboard: http://localhost:8000/board")
    print(f"     ├── Health: http://localhost:8000/api/v1/health")
    print(f"     └── Wiki: http://localhost:8000/api/v1/wiki/query")
    print()

    import uvicorn
    uvicorn.run("src.server.main:app", host="0.0.0.0", port=8000, reload=True)


if __name__ == "__main__":
    main()
