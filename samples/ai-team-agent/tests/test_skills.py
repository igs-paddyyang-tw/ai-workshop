"""Skills 框架測試。"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))


@pytest.fixture(autouse=True)
def setup_test_db(tmp_path, monkeypatch):
    """每個測試使用獨立的臨時 DB。"""
    db_path = tmp_path / "test.db"
    monkeypatch.setattr("coordinator.db.models.DB_PATH", db_path)

    import sqlite3
    conn = sqlite3.connect(str(db_path))
    migrations_dir = Path(__file__).parent.parent / "src" / "coordinator" / "db" / "migrations"
    for sql_file in sorted(migrations_dir.glob("*.sql")):
        conn.executescript(sql_file.read_text(encoding="utf-8"))
    conn.commit()
    conn.close()


# ── BaseSkill 測試 ──


def test_base_skill_abstract():
    """BaseSkill 不能直接實例化。"""
    from business.skills.base import BaseSkill
    with pytest.raises(TypeError):
        BaseSkill()


def test_skill_result():
    """SkillResult 序列化。"""
    from business.skills.base import SkillResult
    r = SkillResult(success=True, data={"key": "val"})
    assert r.to_dict() == {"success": True, "data": {"key": "val"}, "error": ""}


# ── SkillRegistry 測試 ──


def test_registry_register():
    """手動註冊 Skill。"""
    from business.skills.registry import SkillRegistry
    from business.skills.internal.echo import EchoSkill

    reg = SkillRegistry()
    reg.register(EchoSkill())
    assert reg.get("echo") is not None
    assert len(reg.list_skills()) == 1


def test_registry_auto_discover():
    """auto_discover 掃描 internal/。"""
    from business.skills.registry import SkillRegistry

    reg = SkillRegistry()
    count = reg.auto_discover("business.skills.internal")
    assert count >= 5  # echo, wiki_query, news_scraper, news_renderer, web_search


@pytest.mark.asyncio
async def test_registry_invoke_echo():
    """呼叫 echo Skill。"""
    from business.skills.registry import SkillRegistry

    reg = SkillRegistry()
    reg.auto_discover("business.skills.internal")
    result = await reg.invoke("echo", {"text": "hello"})
    assert result.success
    assert result.data["echo"] == "hello"


@pytest.mark.asyncio
async def test_registry_invoke_not_found():
    """呼叫不存在的 Skill。"""
    from business.skills.registry import SkillRegistry

    reg = SkillRegistry()
    result = await reg.invoke("nonexistent", {})
    assert not result.success
    assert "not found" in result.error


# ── SkillTracker 測試 ──


@pytest.mark.asyncio
async def test_tracker_record_and_stats():
    """記錄呼叫 + 取得統計。"""
    from business.skills.tracker import SkillTracker

    tracker = SkillTracker()
    await tracker.record("echo", "test-agent", success=True, duration_ms=50)
    await tracker.record("echo", "test-agent", success=True, duration_ms=30)
    await tracker.record("echo", "test-agent", success=False, duration_ms=100)

    stats = await tracker.get_stats("echo")
    assert len(stats) == 1
    assert stats[0]["call_count"] == 3
    assert stats[0]["success_count"] == 2
    assert stats[0]["success_rate"] == 0.67


@pytest.mark.asyncio
async def test_tracker_needs_evolution():
    """演化判斷。"""
    from business.skills.tracker import SkillTracker

    tracker = SkillTracker()
    # 呼叫不夠多，不需演化
    assert not await tracker.needs_evolution("echo")


@pytest.mark.asyncio
async def test_registry_with_tracker():
    """Registry + Tracker 整合。"""
    from business.skills.registry import SkillRegistry
    from business.skills.tracker import SkillTracker

    tracker = SkillTracker()
    reg = SkillRegistry(tracker=tracker)
    reg.auto_discover("business.skills.internal")

    await reg.invoke("echo", {"text": "test"}, agent="coder-agent")
    stats = await tracker.get_stats("echo")
    assert len(stats) == 1
    assert stats[0]["call_count"] == 1
