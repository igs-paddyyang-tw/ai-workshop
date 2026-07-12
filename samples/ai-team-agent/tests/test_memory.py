"""Memory 子系統測試。"""
from __future__ import annotations

import asyncio
import sys
from pathlib import Path

import pytest

# 確保 src 在 path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))


@pytest.fixture(autouse=True)
def setup_test_db(tmp_path, monkeypatch):
    """每個測試使用獨立的臨時 DB。"""
    db_path = tmp_path / "test.db"
    monkeypatch.setattr("coordinator.db.models.DB_PATH", db_path)

    # 初始化 DB schema
    import sqlite3
    conn = sqlite3.connect(str(db_path))
    migrations_dir = Path(__file__).parent.parent / "src" / "coordinator" / "db" / "migrations"
    for sql_file in sorted(migrations_dir.glob("*.sql")):
        conn.executescript(sql_file.read_text(encoding="utf-8"))
    conn.commit()
    conn.close()


@pytest.fixture
def agents_dir(tmp_path):
    """建立測試用 agents 目錄。"""
    agent_dir = tmp_path / "agents" / "test-agent" / "memory" / "daily"
    agent_dir.mkdir(parents=True)
    return tmp_path / "agents"


# ── indexer 測試 ──


@pytest.mark.asyncio
async def test_index_entry():
    """測試單筆索引寫入。"""
    from coordinator.memory.indexer import index_entry

    row_id = await index_entry(
        agent="test-agent",
        source="daily",
        date="2026-07-12",
        title="## 10:00 [test-agent] task:t1",
        body="- 做了：部署新版本",
        tags="deploy, production",
    )
    assert row_id > 0


@pytest.mark.asyncio
async def test_rebuild_memory_index(agents_dir):
    """測試從檔案重建索引。"""
    from coordinator.memory.indexer import rebuild_memory_index

    # 寫入測試 daily log
    daily_file = agents_dir / "test-agent" / "memory" / "daily" / "2026-07-12.md"
    daily_file.write_text(
        "# 2026-07-12 Daily Log\n\n"
        "## 10:00 [test-agent] task:t1\n"
        "- **做了**：修復登入 bug\n"
        "- tags: bugfix, auth\n\n"
        "## 14:00 [test-agent] task:t2\n"
        "- **做了**：部署 v2.0\n"
        "- tags: deploy\n",
        encoding="utf-8",
    )

    count = await rebuild_memory_index(agents_dir)
    assert count == 2


# ── daily_log 測試 ──


@pytest.mark.asyncio
async def test_write_daily_log(agents_dir):
    """測試 daily log 寫入。"""
    from coordinator.memory.daily_log import write_daily_log

    entry = await write_daily_log(
        agent_name="test-agent",
        task_id="task-001",
        conversation="我修好了登入頁面的 CSS 問題",
        agents_dir=agents_dir,
    )
    assert "test-agent" in entry
    assert "task-001" in entry

    # 確認檔案已建立
    from datetime import datetime
    today = datetime.now().strftime("%Y-%m-%d")
    daily_file = agents_dir / "test-agent" / "memory" / "daily" / f"{today}.md"
    assert daily_file.exists()
    content = daily_file.read_text(encoding="utf-8")
    assert "task-001" in content


# ── recall 測試 ──


@pytest.mark.asyncio
async def test_recall_basic():
    """測試 FTS5 查詢。"""
    from coordinator.memory.indexer import index_entry
    from coordinator.memory.recall import recall

    # 先寫入幾筆
    await index_entry("test-agent", "daily", "2026-07-12", "修復部署", "修復了 nginx 配置的部署問題", "deploy, nginx")
    await index_entry("test-agent", "daily", "2026-07-11", "前端重構", "React 元件拆分重構完成", "react, refactor")
    await index_entry("test-agent", "daily", "2026-07-10", "DB 遷移", "PostgreSQL 升級到 16 版", "database, postgres")

    # 查詢
    results = await recall("test-agent", "部署")
    assert len(results) >= 1
    assert any("部署" in r.body or "部署" in r.title for r in results)


@pytest.mark.asyncio
async def test_recall_empty_query():
    """空查詢回傳空列表。"""
    from coordinator.memory.recall import recall

    results = await recall("test-agent", "")
    assert results == []


@pytest.mark.asyncio
async def test_recall_time_decay():
    """測試時間衰減：較新的記憶分數較高。"""
    from coordinator.memory.indexer import index_entry
    from coordinator.memory.recall import recall

    await index_entry("test-agent", "daily", "2026-07-12", "今天部署", "今天部署了新版本", "deploy")
    await index_entry("test-agent", "daily", "2026-06-01", "上月部署", "上個月部署了舊版本", "deploy")

    results = await recall("test-agent", "部署", k=2)
    assert len(results) >= 1
    # 較新的應該排在前面（分數較高）
    if len(results) >= 2:
        assert results[0].date >= results[1].date


# ── consolidate 測試 ──


@pytest.mark.asyncio
async def test_consolidate_fallback(agents_dir):
    """測試無 LLM 時的 fallback 蒸餾。"""
    from coordinator.memory.indexer import index_entry
    from coordinator.memory.consolidate import consolidate

    # 先寫入資料
    await index_entry("test-agent", "daily", "2026-07-12", "部署", "完成部署", "deploy")
    await index_entry("test-agent", "daily", "2026-07-11", "測試", "完成測試", "test")

    result = await consolidate("test-agent", agents_dir=agents_dir)
    assert len(result) > 0

    # 確認 memory.md 已建立
    memory_file = agents_dir / "test-agent" / "memory" / "memory.md"
    assert memory_file.exists()


# ── recommend 測試 ──


@pytest.mark.asyncio
async def test_recommend_skills_empty():
    """無歷史時回傳空。"""
    from coordinator.memory.recommend import recommend_skills

    results = await recommend_skills("test-agent", "部署")
    assert results == []
