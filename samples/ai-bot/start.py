"""AI Agent 專家開發平台 — 一鍵啟動。"""
from __future__ import annotations

import os
import sys
import subprocess
from pathlib import Path


def main() -> None:
    import time
    _start_time = time.time()

    os.chdir(Path(__file__).parent)

    from dotenv import load_dotenv
    load_dotenv()

    # ── 依賴檢查（啟動前攔截）──
    _check_dependencies()

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

    # Tier 3: kiro-cli
    from src.agent.cli import is_cli_available
    cli_available = is_cli_available()
    print(f"  Tier 3: {'✅' if cli_available else '⬚'} kiro-cli Agent 常駐")
    print("═" * 50)

    # Skills（拆分類型）
    from src.skills.registry import SkillRegistry
    registry = SkillRegistry()
    internal_count = registry.auto_discover("src.skills.internal")
    ide_skills = list(Path(".kiro/skills").glob("ark-*")) if Path(".kiro/skills").exists() else []
    print(f"\n  📦 Skills: IDE {len(ide_skills)} | Internal {internal_count}")

    # Wiki（拆分知識庫數字）
    shared_wiki = list(Path("knowledge/shared/wiki").rglob("*.md")) if Path("knowledge/shared/wiki").exists() else []
    shared_raw = list(Path("knowledge/shared/raw").rglob("*.md")) if Path("knowledge/shared/raw").exists() else []
    agent_wiki_count = 0
    for agent_wiki in Path("agents").glob("*/knowledge/wiki"):
        agent_wiki_count += len(list(agent_wiki.rglob("*.md")))
    print(f"  📚 Wiki:   shared {len(shared_wiki)} | raw {len(shared_raw)} | agents {agent_wiki_count}")

    # Wiki lint
    try:
        from src.wiki.engine import WikiEngine
        engine = WikiEngine()
        lint_issues = engine.lint()
        if lint_issues:
            print(f"  🔍 Lint:   ⚠️ {len(lint_issues)} issues")
        else:
            print(f"  🔍 Lint:   ✅ 0 issues")
    except Exception:
        print(f"  🔍 Lint:   ⚠️ 無法執行")

    # SOUL
    soul_path = Path(".kiro/steering/SOUL.md")
    print(f"  🧠 SOUL: {'✅ 已載入' if soul_path.exists() else '⚠️ 未找到'}")

    # ── 自我成長系統自檢 ──
    _self_growth_check()

    # ── Output 清理（僅提醒，不主動刪除）──
    try:
        from src.tools.cleanup import cleanup_output
        deleted = cleanup_output(max_age_days=30)
        if deleted:
            print(f"  🧹 Output:  ⚠️ {len(deleted)} 個檔案超過 30 天，建議清理")
        else:
            print(f"  🧹 Output:  ✅ 無過期檔案")
    except Exception as e:
        print(f"  🧹 Output:  ⚠️ {e}")

    # Memory 統計
    daily_dir = Path("memory/daily") if Path("memory/daily").exists() else None
    daily_count = len(list(daily_dir.glob("*.md"))) if daily_dir else 0
    memory_md = Path("memory/memory.md")
    memory_size = f"{len(memory_md.read_text(encoding='utf-8').split())}" if memory_md.exists() else "0"
    print(f"  🧠 Memory: daily {daily_count}d | memory.md ~{memory_size} words")

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
    if cli_available:
        print(f"  🧠 Agent:  8 active (kiro-cli) | 由 Bot 子進程管理")
    else:
        print(f"  🧠 Agent:  8 active (gemini fallback)")

    # ── Team 模式偵測 ──
    team_yaml_path = Path("team.yaml")
    team_mode = team_yaml_path.exists()
    if team_mode:
        import yaml
        team_data = yaml.safe_load(team_yaml_path.read_text(encoding="utf-8"))
        team_name = team_data.get("name", "unnamed")
        instances = team_data.get("instances", {})
        local_count = sum(1 for v in instances.values() if v.get("transport", "local") == "local")
        http_count = sum(1 for v in instances.values() if v.get("transport", "local") == "http")

        print(f"\n  🤝 團隊模式: {team_name}")
        print(f"     本地 Agent: {local_count} 個")
        if http_count:
            print(f"     遠端 Agent: {http_count} 個（跨機協作）")

        # 組裝 A2A Router
        from src.coordinator.a2a.router import A2ARouter
        from src.coordinator.a2a.graph import TaskGraph
        from src.coordinator.a2a.shared_memory import SharedMemory
        from src.coordinator.a2a.discovery import AgentDiscovery
        from src.coordinator.a2a.transport import AgentConfig, fetch_agent_card

        graph = TaskGraph()
        memory = SharedMemory()
        discovery = AgentDiscovery(memory)

        # 建立 AgentConfig 列表
        agent_configs: dict[str, AgentConfig] = {}
        for name, cfg in instances.items():
            agent_configs[name] = AgentConfig(
                name=name,
                role=cfg.get("role", "worker"),
                working_directory=cfg.get("working_directory", "."),
                transport=cfg.get("transport", "local"),
                endpoint=cfg.get("endpoint", ""),
                auth_token_env=cfg.get("auth_token_env", ""),
                description=cfg.get("description", ""),
            )

        # 存入環境供 handlers.py 使用
        os.environ["_TEAM_MODE"] = "1"
        os.environ["_TEAM_NAME"] = team_name

        # 寫入 agent_profiles（供 discovery 用）
        profiles_dir = Path("knowledge/shared/agent_profiles")
        profiles_dir.mkdir(parents=True, exist_ok=True)
        for name, cfg in agent_configs.items():
            profile = {
                "agent_id": name,
                "role": cfg.role,
                "skills": cfg.skills,
                "description": cfg.description,
                "transport": cfg.transport,
                "current_load": 0,
                "capacity": 3,
            }
            (profiles_dir / f"{name}.yaml").write_text(
                yaml.dump(profile, allow_unicode=True), encoding="utf-8"
            )

        # 配置 A2A Server
        from src.coordinator.a2a.server import configure as configure_a2a_server
        configure_a2a_server(agent_card={
            "name": os.getenv("AGENT_NAME", "ai-bot"),
            "description": "",
            "skills": [],
            "status": "idle",
        })

        print(f"     A2A Router: ✅ 已組裝")
    else:
        print(f"\n  📌 個體模式（無 team.yaml）")

    print(f"\n  ── Web UI ──────────────────────────────────────")
    print(f"  💬 Chat:      http://localhost:8000")
    print(f"  ⚙️  Dashboard: http://localhost:8000/admin")
    print(f"  📖 Wiki:      http://localhost:8000/wiki")
    print(f"  🕸️  Graph:     http://localhost:8000/graph")
    print(f"  🏗️  Builder:   http://localhost:8000/builder")
    print(f"\n  ── API ─────────────────────────────────────────")
    print(f"  📡 API Docs:  http://localhost:8000/api-docs")
    print(f"  ❤️  Health:    http://localhost:8000/health")
    if team_mode:
        print(f"  🔗 A2A:      http://localhost:8000/api/v1/a2a/card")
    print()
    print(f"  ⏱️  Ready in {time.time() - _start_time:.1f}s")
    print()

    # API Server
    import uvicorn
    try:
        uvicorn.run("src.server.main:app", host="0.0.0.0", port=8000, reload=True)
    finally:
        if bot_proc:
            bot_proc.terminate()
            bot_proc.wait(timeout=5)


def _check_dependencies() -> None:
    """啟動前檢查必要依賴，缺少時直接報錯退出。"""
    required = {
        "google.generativeai": "google-generativeai",
        "telegram": "python-telegram-bot",
        "fastapi": "fastapi",
        "uvicorn": "uvicorn",
        "httpx": "httpx",
        "dotenv": "python-dotenv",
        "yaml": "pyyaml",
    }
    missing: list[str] = []
    for module, package in required.items():
        try:
            __import__(module)
        except ImportError:
            missing.append(package)
    if missing:
        print("❌ 缺少必要依賴：")
        for pkg in missing:
            print(f"   pip install {pkg}")
        print(f"\n   或執行：pip install -r requirements.txt")
        sys.exit(1)


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
