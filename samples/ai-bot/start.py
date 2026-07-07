"""AI Agent 專家開發平台 — 一鍵啟動。"""
from __future__ import annotations

import os
import sys
import subprocess
from pathlib import Path


def main() -> None:
    os.chdir(Path(__file__).parent)

    from dotenv import load_dotenv
    load_dotenv()

    from src.logging_config import setup_logging
    setup_logging()

    tg_token = os.getenv("TELEGRAM_BOT_TOKEN", "")
    gemini_key = os.getenv("GEMINI_API_KEY", "")

    print("═" * 50)
    print("  🤖 AI Agent 專家開發平台")
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
    wiki_files = list(Path("knowledge/wiki").rglob("*.md"))
    print(f"  📚 知識庫: {len(wiki_files)} 篇")

    # SOUL
    soul_path = Path(".kiro/steering/SOUL.md")
    print(f"  🧠 SOUL: {'✅ 已載入' if soul_path.exists() else '⚠️ 未找到'}")

    # Bot 子進程
    bot_proc = None
    if tg_token:
        import httpx
        try:
            resp = httpx.get(f"https://api.telegram.org/bot{tg_token}/getMe", timeout=10)
            bot_info = resp.json()
            if bot_info.get("ok"):
                bot_name = bot_info["result"]["username"]
                print(f"  🤖 Bot: @{bot_name} 已連線")
            else:
                print(f"  ❌ Bot Token 無效: {bot_info.get('description', '')}")
                tg_token = ""
        except Exception as e:
            print(f"  ❌ Bot 連線失敗: {e}")
            tg_token = ""

    if tg_token:
        bot_proc = subprocess.Popen(
            [sys.executable, "-m", "src.bot.run"],
            env={**os.environ, "PYTHONIOENCODING": "utf-8"},
        )
        print(f"  🤖 Bot: 子進程已啟動 (PID={bot_proc.pid})")
    else:
        if not os.getenv("TELEGRAM_BOT_TOKEN", ""):
            print(f"  ⚠️  無 TG Token → 僅 API 模式")

    # Agent 服務
    from src.agent.cli import is_cli_available
    if is_cli_available():
        print(f"  🧠 Agent 服務: 由 Bot 子進程管理")
    else:
        print(f"  🧠 Agent 服務: ⬚（kiro-cli 未安裝，使用 Gemini fallback）")

    print(f"\n  🚀 API:  http://localhost:8000")
    print(f"  📖 Docs: http://localhost:8000/api-docs")
    print()

    # API Server
    import uvicorn
    try:
        uvicorn.run("src.server.main:app", host="0.0.0.0", port=8000, reload=True)
    finally:
        if bot_proc:
            bot_proc.terminate()
            bot_proc.wait(timeout=5)


if __name__ == "__main__":
    main()
