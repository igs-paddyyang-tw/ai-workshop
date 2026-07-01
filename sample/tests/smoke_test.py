"""AI Workshop 冒煙測試 — Tier 分級自動跳過。

Tier 0: 零設定（結構 + Skills + Wiki + API）
Tier 1: 需 TELEGRAM_BOT_TOKEN
Tier 2: 需 GEMINI_API_KEY
"""
from __future__ import annotations

import asyncio
import os
from pathlib import Path

import pytest


# ── Tier 0：零設定 ───────────────────────────────────────


class TestTier0Structure:
    """專案結構驗證。"""

    def test_project_files_exist(self):
        base = Path(__file__).parent.parent
        assert (base / "start.py").exists()
        assert (base / "team.yaml").exists()
        assert (base / "requirements.txt").exists()
        assert (base / "src" / "gateway" / "bot.py").exists()
        assert (base / "src" / "skills" / "base.py").exists()
        assert (base / "src" / "wiki" / "engine.py").exists()
        assert (base / "src" / "coordinator" / "task_graph.py").exists()
        assert (base / "src" / "coordinator" / "discovery.py").exists()
        assert (base / "src" / "server" / "main.py").exists()
        assert (base / "src" / "llm" / "gemini_chat.py").exists()

    def test_knowledge_dir(self):
        base = Path(__file__).parent.parent
        assert (base / "knowledge" / "raw").is_dir()
        assert (base / "knowledge" / "schema.md").exists()
        raw_files = list((base / "knowledge" / "raw").glob("*.md"))
        assert len(raw_files) >= 3


class TestTier0Skills:
    """Skills 系統驗證。"""

    def test_registry_auto_discover(self):
        from src.skills.registry import SkillRegistry
        registry = SkillRegistry()
        count = registry.auto_discover("src.skills.internal")
        assert count >= 4
        ids = {s["skill_id"] for s in registry.list_skills()}
        assert "echo" in ids
        assert "news" in ids

    def test_echo_skill(self):
        from src.skills.internal.echo import EchoSkill
        skill = EchoSkill()
        result = asyncio.run(skill.execute({"message": "test"}))
        assert result.success
        assert result.data["echo"] == "test"

    def test_summarize_skill(self):
        from src.skills.internal.summarize import SummarizeSkill
        skill = SummarizeSkill()
        result = asyncio.run(skill.execute({"content": "短文"}))
        assert result.success

    def test_translate_skill(self):
        from src.skills.internal.translate import TranslateSkill
        skill = TranslateSkill()
        result = asyncio.run(skill.execute({"text": "hello", "target_lang": "ja"}))
        assert result.success
        assert result.data["translated"] == "[ja] hello"


class TestTier0Wiki:
    """Wiki 引擎驗證。"""

    def test_wiki_engine_importable(self):
        from src.wiki.engine import WikiEngine
        engine = WikiEngine()
        assert engine is not None

    def test_wiki_ingest(self):
        from src.wiki.engine import WikiEngine
        engine = WikiEngine()
        ingested = engine.ingest()
        assert len(ingested) >= 3

    def test_wiki_lint(self):
        from src.wiki.engine import WikiEngine
        engine = WikiEngine()
        engine.ingest()  # 先 ingest
        issues = engine.lint()
        # ingest 後應該沒有 missing frontmatter
        assert isinstance(issues, list)

    def test_wiki_query(self):
        from src.wiki.engine import WikiEngine
        engine = WikiEngine()
        engine.ingest()
        result = asyncio.run(engine.query("asyncio"))
        assert "results" in result
        assert len(result["results"]) >= 1


class TestTier0Coordinator:
    """團隊協調驗證。"""

    def test_task_graph(self):
        from src.coordinator.task_graph import TaskGraph, TaskNode
        graph = TaskGraph()
        graph.add_node(TaskNode(id="a", title="Task A"))
        graph.add_node(TaskNode(id="b", title="Task B", depends_on=["a"]))
        order = graph.topological_sort()
        assert order == ["a", "b"]

    def test_task_graph_parallel(self):
        from src.coordinator.task_graph import TaskGraph, TaskNode
        graph = TaskGraph()
        graph.add_node(TaskNode(id="a", title="A"))
        graph.add_node(TaskNode(id="b", title="B"))
        graph.add_node(TaskNode(id="c", title="C", depends_on=["a", "b"]))
        ready = graph.resolve_dependencies()
        assert set(ready) == {"a", "b"}

    def test_discovery(self):
        from src.coordinator.discovery import AgentDiscovery
        discovery = AgentDiscovery.from_yaml(
            Path(__file__).parent.parent / "team.yaml"
        )
        result = discovery.match_agent(["python", "fastapi"])
        assert result is not None
        assert result.agent_id == "backend"

    def test_task_manager(self):
        from src.coordinator.task_manager import TaskManager
        tm = TaskManager()
        task = tm.create_task("Test Task")
        assert task.id == "T-001"
        tm.assign(task.id, "backend")
        assert task.status == "assigned"


class TestTier0API:
    """API Server 驗證（import 層面）。"""

    def test_app_importable(self):
        from src.server.main import app
        assert app is not None


# ── Tier 1：需 TELEGRAM_BOT_TOKEN ────────────────────────


needs_tg = pytest.mark.skipif(
    not os.getenv("TELEGRAM_BOT_TOKEN"),
    reason="TELEGRAM_BOT_TOKEN 未設定 → 跳過 Tier 1",
)


class TestTier1:
    """需要 Telegram Bot Token。"""

    @needs_tg
    def test_bot_token_valid(self):
        import httpx
        token = os.getenv("TELEGRAM_BOT_TOKEN")
        r = httpx.get(f"https://api.telegram.org/bot{token}/getMe")
        data = r.json()
        assert data["ok"], f"Token 無效: {data}"

    @needs_tg
    def test_bot_create_app(self):
        from src.gateway.bot import create_app
        app = create_app()
        assert app is not None


# ── Tier 2：需 GEMINI_API_KEY ────────────────────────────


needs_gemini = pytest.mark.skipif(
    not os.getenv("GEMINI_API_KEY"),
    reason="GEMINI_API_KEY 未設定 → 跳過 Tier 2",
)


class TestTier2:
    """需要 Gemini API Key。"""

    @needs_gemini
    def test_gemini_chat(self):
        from src.llm.gemini_chat import ask_gemini
        result = asyncio.run(ask_gemini("說 hello"))
        assert len(result) > 0

    @needs_gemini
    def test_wiki_rag(self):
        from src.wiki.engine import WikiEngine
        engine = WikiEngine()
        engine.ingest()
        result = asyncio.run(engine.query("什麼是 asyncio", use_rag=True))
        assert result.get("answer") is not None
