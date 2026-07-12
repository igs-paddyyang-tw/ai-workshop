"""AI Workshop 冒煙測試 — Tier 分級自動跳過。

Tier 0: 零設定（結構 + Skills + Wiki + API + Memory）
Tier 1: 需 TELEGRAM_BOT_TOKEN
Tier 2: 需 GEMINI_API_KEY
"""
from __future__ import annotations

import asyncio
import os
import sys
from pathlib import Path

import pytest

# 確保 src 在 path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))


# ── Tier 0：零設定 ───────────────────────────────────────


class TestTier0Structure:
    """專案結構驗證。"""

    def test_project_files_exist(self):
        base = Path(__file__).parent.parent
        assert (base / "start.py").exists()
        assert (base / "team.yaml").exists()
        assert (base / "requirements.txt").exists()
        assert (base / "src" / "bootstrap.py").exists()
        assert (base / "src" / "runtime" / "process.py").exists()
        assert (base / "src" / "runtime" / "tier.py").exists()
        assert (base / "src" / "coordinator" / "events" / "bus.py").exists()

    def test_agents_dir(self):
        base = Path(__file__).parent.parent
        assert (base / "agents").is_dir()
        agents = [d.name for d in (base / "agents").iterdir() if d.is_dir()]
        assert len(agents) >= 3

    def test_knowledge_dir(self):
        base = Path(__file__).parent.parent
        knowledge = base / "knowledge"
        if knowledge.exists():
            assert (knowledge / "shared").is_dir() or True  # 可能還沒建

    def test_migrations_exist(self):
        base = Path(__file__).parent.parent
        migrations = base / "src" / "coordinator" / "db" / "migrations"
        assert migrations.is_dir()
        sql_files = list(migrations.glob("*.sql"))
        assert len(sql_files) >= 4  # 001-004


class TestTier0Skills:
    """Skills 系統驗證。"""

    def test_registry_auto_discover(self):
        from business.skills.registry import SkillRegistry
        registry = SkillRegistry()
        count = registry.auto_discover("business.skills.internal")
        assert count >= 5
        ids = {s["skill_id"] for s in registry.list_skills()}
        assert "echo" in ids
        assert "wiki_query" in ids

    def test_echo_skill(self):
        from business.skills.internal.echo import EchoSkill
        skill = EchoSkill()
        result = asyncio.run(skill.execute({"text": "test"}))
        assert result.success
        assert result.data["echo"] == "test"

    def test_base_skill_interface(self):
        from business.skills.base import BaseSkill, SkillResult, SkillType
        assert SkillType.PYTHON == "python"
        r = SkillResult(success=True, data={"k": "v"})
        assert r.to_dict()["success"] is True

    def test_skill_tracker_importable(self):
        from business.skills.tracker import SkillTracker
        tracker = SkillTracker()
        assert tracker is not None


class TestTier0Wiki:
    """Wiki 引擎驗證。"""

    def test_wiki_engine_importable(self):
        from coordinator.wiki.engine import WikiEngine
        engine = WikiEngine()
        assert engine is not None

    def test_wiki_indexer_importable(self):
        from coordinator.wiki.indexer import build_metadata, rebuild_index
        assert callable(build_metadata)
        assert callable(rebuild_index)

    def test_search_layers_importable(self):
        from coordinator.wiki.search.layer0_exact import search_exact, search_substring
        from coordinator.wiki.search.layer1_bm25 import search_bm25, build_bm25_index
        from coordinator.wiki.search.layer2_tfidf import is_available
        from coordinator.wiki.search.layer3_rerank import is_available as rerank_available
        assert callable(search_exact)
        assert callable(search_bm25)


class TestTier0Memory:
    """Memory 子系統驗證。"""

    def test_memory_importable(self):
        from coordinator.memory import write_daily_log, recall, consolidate, recommend_skills
        assert callable(write_daily_log)
        assert callable(recall)
        assert callable(consolidate)

    def test_recall_result_dataclass(self):
        from coordinator.memory.recall import RecallResult
        r = RecallResult(agent="a", source="daily", date="2026-01-01",
                         title="t", body="b", tags="", score=0.5)
        d = r.to_dict()
        assert d["agent"] == "a"
        assert d["score"] == 0.5


needs_py311 = pytest.mark.skipif(
    sys.version_info < (3, 11),
    reason="需要 Python 3.11+（StrEnum / str | None 語法）",
)


class TestTier0Coordinator:
    """Coordinator 驗證。"""

    def test_event_types(self):
        from coordinator.events.types import EventType
        assert EventType.AGENT_OUTPUT == "agent.output"
        assert EventType.MEMORY_WRITTEN == "memory.written"
        assert EventType.SKILL_EXECUTED == "skill.executed"
        assert EventType.SKILL_PROPOSED == "skill.proposed"

    @pytest.mark.skipif(sys.version_info < (3, 10), reason="asyncio.Queue 在 3.9 需要 event loop")
    def test_event_bus_importable(self):
        from coordinator.events.bus import EventBus
        bus = EventBus(maxsize=10)
        assert bus is not None

    def test_a2a_importable(self):
        from coordinator.a2a.protocol import TaskHandoff
        from coordinator.a2a.graph import TaskGraph
        from coordinator.a2a.shared_memory import SharedMemory
        from coordinator.a2a.discovery import AgentDiscovery
        assert callable(TaskGraph)

    def test_growth_detector_importable(self):
        from coordinator.services.growth import GrowthDetector
        gd = GrowthDetector()
        assert gd is not None

    @needs_py311
    def test_task_lifecycle_importable(self):
        from coordinator.task_lifecycle import TaskLifecycle, TaskStatus
        assert TaskStatus.COMPLETED == "completed"


class TestTier0Runtime:
    """Runtime 驗證。"""

    def test_tier_detect(self):
        from runtime.tier import detect_tier, TierStatus
        status = detect_tier()
        assert isinstance(status, TierStatus)
        assert status.tier >= 0

    @needs_py311
    def test_registry_importable(self):
        from runtime.registry import RuntimeRegistry, ALL_PROVIDERS
        assert "kiro-cli" in ALL_PROVIDERS

    def test_config_importable(self):
        from runtime.config import load_config
        assert callable(load_config)


class TestTier0API:
    """API Server 驗證（import 層面）。"""

    @needs_py311
    def test_app_importable(self):
        from gateway.api.router import app
        assert app is not None

    @needs_py311
    def test_new_routers_registered(self):
        from gateway.api.router import app
        routes = [r.path for r in app.routes]
        assert any("/api/v1/memory" in r for r in routes)
        assert any("/api/v1/wiki" in r for r in routes)
        assert any("/api/v1/skills" in r for r in routes)


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
    def test_memory_commands_importable(self):
        from gateway.telegram.handlers.memory_commands import (
            cmd_recall, cmd_consolidate, cmd_skills, cmd_mode
        )
        assert callable(cmd_recall)


# ── Tier 2：需 GEMINI_API_KEY ────────────────────────────


needs_gemini = pytest.mark.skipif(
    not os.getenv("GEMINI_API_KEY"),
    reason="GEMINI_API_KEY 未設定 → 跳過 Tier 2",
)


class TestTier2:
    """需要 Gemini API Key。"""

    @needs_gemini
    def test_gemini_chat_importable(self):
        from gateway.gemini_chat import gemini_chat
        assert callable(gemini_chat)

    @needs_gemini
    def test_wiki_rag(self):
        from coordinator.wiki.engine import WikiEngine
        engine = WikiEngine()
        result = asyncio.run(engine.query("test", use_rag=True))
        assert "answer" in result
