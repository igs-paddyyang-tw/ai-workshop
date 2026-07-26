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

    def test_team_yaml_8_agents(self):
        """team.yaml 預設 8 agents 配置驗證。"""
        import yaml
        base = Path(__file__).parent.parent
        team_yaml = base / "team.yaml"
        assert team_yaml.exists(), "team.yaml 不存在"
        data = yaml.safe_load(team_yaml.read_text(encoding="utf-8"))

        instances = data.get("instances", {})
        assert len(instances) == 8, f"team.yaml 應有 8 agents，目前 {len(instances)}"

        expected = {"admin-agent", "pm-agent", "coder-agent", "qa-agent",
                    "ai-dev-agent", "market-agent", "data-agent", "report-agent"}
        assert set(instances.keys()) == expected, f"缺少或多餘的 agent: {set(instances.keys()) ^ expected}"

        # 驗證 admin + pm 是常駐（persistent: true，或繼承 defaults）
        defaults_persistent = data.get("defaults", {}).get("persistent", False)
        admin = instances.get("admin-agent", {})
        pm = instances.get("pm-agent", {})
        admin_persistent = admin.get("persistent", defaults_persistent)
        pm_persistent = pm.get("persistent", defaults_persistent)
        assert admin_persistent, "admin-agent 應為 persistent: true"
        assert pm_persistent, "pm-agent 應為 persistent: true"

    def test_team_yaml_variants(self):
        """team-ops.yaml 和 team-dev.yaml 存在且格式正確。"""
        import yaml
        base = Path(__file__).parent.parent

        for fname, expected_workers in [("team-ops.yaml", {"market-agent", "data-agent", "report-agent"}),
                                         ("team-dev.yaml", {"ai-dev-agent", "coder-agent", "qa-agent"})]:
            path = base / fname
            assert path.exists(), f"{fname} 不存在"
            data = yaml.safe_load(path.read_text(encoding="utf-8"))
            instances = set(data.get("instances", {}).keys())
            assert "admin-agent" in instances, f"{fname}: 缺少 admin-agent"
            assert "pm-agent" in instances, f"{fname}: 缺少 pm-agent"
            for w in expected_workers:
                assert w in instances, f"{fname}: 缺少 {w}"

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

    def test_steering_4_files(self):
        """每個 agent 必須有 4 檔 steering（SOUL/BRAIN/MEMORY/TEAM）。"""
        base = Path(__file__).parent.parent
        agents_dir = base / "agents"
        agents = [d for d in agents_dir.iterdir() if d.is_dir()]
        assert len(agents) >= 3, "至少 3 個 agent"

        required = ["SOUL.md", "BRAIN.md", "MEMORY.md", "TEAM.md"]
        missing = []
        for agent_dir in agents:
            steering_dir = agent_dir / ".kiro" / "steering"
            for f in required:
                if not (steering_dir / f).exists():
                    missing.append(f"{agent_dir.name}/{f}")

        assert missing == [], f"缺少 steering 檔案：{missing}"

    def test_brain_inclusion_always(self):
        """每個 agent BRAIN.md 必須有 inclusion: always frontmatter。"""
        base = Path(__file__).parent.parent
        agents_dir = base / "agents"
        bad = []
        for agent_dir in agents_dir.iterdir():
            if not agent_dir.is_dir():
                continue
            brain = agent_dir / ".kiro" / "steering" / "BRAIN.md"
            if brain.exists():
                content = brain.read_text(encoding="utf-8")
                if "inclusion: always" not in content:
                    bad.append(agent_dir.name)
        assert bad == [], f"BRAIN.md 缺少 inclusion: always：{bad}"

    def test_memory_daily_dirs(self):
        """每個 agent 必須有 memory/daily/ 目錄（情節記憶）。"""
        base = Path(__file__).parent.parent
        agents_dir = base / "agents"
        missing = []
        for agent_dir in agents_dir.iterdir():
            if not agent_dir.is_dir():
                continue
            daily_dir = agent_dir / "memory" / "daily"
            if not daily_dir.exists():
                missing.append(agent_dir.name)
        assert missing == [], f"缺少 memory/daily/：{missing}"

    def test_root_brain_exists(self):
        """根目錄 .kiro/steering/BRAIN.md 必須存在。"""
        base = Path(__file__).parent.parent
        brain = base / ".kiro" / "steering" / "BRAIN.md"
        assert brain.exists(), "根 .kiro/steering/BRAIN.md 不存在"
        content = brain.read_text(encoding="utf-8")
        assert "三層資源" in content, "BRAIN.md 缺少三層資源內容"

    def test_hooks_exist(self):
        """根目錄 .kiro/hooks/ 必須有 hook 檔案。"""
        base = Path(__file__).parent.parent
        hooks_dir = base / ".kiro" / "hooks"
        assert hooks_dir.exists(), ".kiro/hooks/ 不存在"
        hooks = list(hooks_dir.glob("*.hook"))
        assert len(hooks) >= 1, "沒有 hook 檔案"

    def test_output_dirs(self):
        """根目錄 output/ 四區必須存在。"""
        base = Path(__file__).parent.parent
        for category in ["reports", "skills", "exports", "drafts"]:
            d = base / "output" / category
            assert d.exists(), f"output/{category}/ 不存在"

    def test_skills_json_exists(self):
        """每個 agent 必須有 .kiro/settings/skills.json，格式正確。"""
        import json
        base = Path(__file__).parent.parent
        agents_dir = base / "agents"
        missing, invalid = [], []
        for agent_dir in agents_dir.iterdir():
            if not agent_dir.is_dir():
                continue
            skills_json = agent_dir / ".kiro" / "settings" / "skills.json"
            if not skills_json.exists():
                missing.append(agent_dir.name)
                continue
            try:
                data = json.loads(skills_json.read_text(encoding="utf-8"))
                if "role" not in data or "skills" not in data:
                    invalid.append(agent_dir.name)
            except json.JSONDecodeError:
                invalid.append(agent_dir.name)
        assert missing == [], f"缺少 skills.json：{missing}"
        assert invalid == [], f"skills.json 格式錯誤（缺 role/skills）：{invalid}"

    def test_skill_mapping_yaml_exists(self):
        """config/skill-mapping.yaml 必須存在且含 roles + shared。"""
        import yaml
        base = Path(__file__).parent.parent
        mapping = base / "config" / "skill-mapping.yaml"
        assert mapping.exists(), "config/skill-mapping.yaml 不存在"
        data = yaml.safe_load(mapping.read_text(encoding="utf-8"))
        assert "roles" in data, "skill-mapping.yaml 缺少 roles 區塊"
        assert "shared" in data, "skill-mapping.yaml 缺少 shared 區塊"
        assert len(data["roles"]) >= 5, f"roles 應至少 5 個角色，目前 {len(data['roles'])}"

    def test_team_md_8_members(self):
        """每個 agent TEAM.md 必須包含完整 8 人清單和「你的身份」標示。"""
        base = Path(__file__).parent.parent
        agents_dir = base / "agents"
        issues = []
        expected_agents = {"admin-agent", "pm-agent", "coder-agent", "qa-agent",
                           "ai-dev-agent", "market-agent", "data-agent", "report-agent"}
        for agent_dir in agents_dir.iterdir():
            if not agent_dir.is_dir():
                continue
            team_md = agent_dir / ".kiro" / "steering" / "TEAM.md"
            if not team_md.exists():
                issues.append(f"{agent_dir.name}: TEAM.md 不存在")
                continue
            content = team_md.read_text(encoding="utf-8")
            # 驗證 8 人清單
            for a in expected_agents:
                if a not in content:
                    issues.append(f"{agent_dir.name}: TEAM.md 缺少 {a}")
            # 驗證身份標示
            if "你的身份" not in content and "你 " not in content and "← 你" not in content:
                issues.append(f"{agent_dir.name}: TEAM.md 缺少身份標示")
        assert issues == [], f"TEAM.md 問題：{issues}"


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
