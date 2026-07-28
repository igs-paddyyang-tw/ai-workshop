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
    wiki_files = list(Path("knowledge/shared/wiki").rglob("*.md"))
    for agent_wiki in Path("agents").glob("*/knowledge/wiki"):
        wiki_files.extend(agent_wiki.rglob("*.md"))
    print(f"  📚 知識庫: {len(wiki_files)} 篇")

    # SOUL
    soul_path = Path(".kiro/steering/SOUL.md")
    print(f"  🧠 SOUL: {'✅ 已載入' if soul_path.exists() else '⚠️ 未找到'}")

    # ── 自我成長系統自檢 ──
    _self_growth_check()

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

    print(f"\n  📌 個體模式")

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


def _self_growth_check() -> None:
    """啟動自檢：驗證 steering 4 檔制 + memory/ 目錄。"""
    agents_dir = Path("agents")
    if not agents_dir.exists():
        return

    warnings: list[str] = []
    agents = [d.name for d in agents_dir.iterdir() if d.is_dir() and d.name.endswith("-agent")]

    for agent in agents:
        agent_path = agents_dir / agent

        # Steering 必備檔
        steering_dir = agent_path / ".kiro" / "steering"
        required_steering = ["SOUL.md", "BRAIN.md", "GUARDRAILS.md", "USER.md"]
        for f in required_steering:
            if not (steering_dir / f).exists():
                warnings.append(f"  ⚠️  {agent}: 缺少 steering/{f}")

        # Memory 目錄
        memory_dir = agent_path / "memory"
        if not memory_dir.exists():
            memory_dir.mkdir(parents=True, exist_ok=True)
            (memory_dir / "daily").mkdir(exist_ok=True)
            (memory_dir / "memory.md").write_text(
                f"# {agent} 持久事實\n\n> 上限 2000 tokens。\n", encoding="utf-8"
            )
            (memory_dir / "recent.md").write_text(
                "# 最近經驗\n\n（尚無記錄）\n", encoding="utf-8"
            )
            warnings.append(f"  📁 {agent}: memory/ 已自動初始化")
        else:
            if not (memory_dir / "daily").exists():
                (memory_dir / "daily").mkdir(exist_ok=True)

    if warnings:
        print(f"  🔍 自檢:")
        for w in warnings:
            print(w)
    else:
        print(f"  🔍 自檢: ✅ 8 Agent steering + memory 完整")


if __name__ == "__main__":
    main()
