"""課程 A 產出 — 個體 Agent 一鍵啟動。"""
from __future__ import annotations

import os
import threading
from pathlib import Path


def main() -> None:
    os.chdir(Path(__file__).parent)

    from dotenv import load_dotenv
    load_dotenv()

    tg_token = os.getenv("TELEGRAM_BOT_TOKEN", "")
    gemini_key = os.getenv("GEMINI_API_KEY", "")

    print("═" * 50)
    print("  🤖 課程 A — 個體 Agent")
    print("═" * 50)
    print(f"  Tier 0: ✅ Skills + Wiki + API（永遠可用）")
    print(f"  Tier 1: {'✅' if tg_token else '⬚'} Telegram Bot")
    print(f"  Tier 2: {'✅' if gemini_key else '⬚'} Gemini AI + RAG")
    print("═" * 50)

    # Skills
    from src.skills.registry import SkillRegistry
    registry = SkillRegistry()
    count = registry.auto_discover("src.skills.internal")
    print(f"\n  📦 Skills: {count} 個")

    # Wiki
    wiki_files = list(Path("knowledge/raw").glob("*.md"))
    print(f"  📚 知識庫: {len(wiki_files)} 篇")

    # SOUL
    soul_path = Path("soul.md")
    print(f"  🧠 SOUL: {'✅ 已載入' if soul_path.exists() else '⚠️ 未找到'}")

    # Bot
    if tg_token:
        # 先驗證 Token 有效
        import httpx
        try:
            resp = httpx.get(f"https://api.telegram.org/bot{tg_token}/getMe", timeout=10)
            bot_info = resp.json()
            if bot_info.get("ok"):
                bot_name = bot_info["result"]["username"]
                print(f"  🤖 Bot: @{bot_name} 已連線")
            else:
                print(f"  ❌ Bot Token 無效: {bot_info.get('description', '未知錯誤')}")
                tg_token = ""  # 跳過啟動
        except Exception as e:
            print(f"  ❌ Bot 連線失敗: {e}")
            tg_token = ""

    if tg_token:
        from src.bot.main import create_app
        bot_app = create_app()

        def run_bot():
            import asyncio
            asyncio.run(bot_app.run_polling(drop_pending_updates=True))

        t = threading.Thread(target=run_bot, daemon=True)
        t.start()
        print(f"  🤖 Bot: polling 啟動")
    else:
        if not os.getenv("TELEGRAM_BOT_TOKEN", ""):
            print(f"  ⚠️  無 TG Token → 僅 API 模式")

    print(f"\n  🚀 http://localhost:8000")
    print()

    import uvicorn
    uvicorn.run("src.server.main:app", host="0.0.0.0", port=8000, reload=True)


if __name__ == "__main__":
    main()
