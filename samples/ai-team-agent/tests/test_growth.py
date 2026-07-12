"""GrowthDetector 自我成長測試。"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))


@pytest.fixture(autouse=True)
def setup_env(tmp_path, monkeypatch):
    """隔離 proposals.json。"""
    proposals_file = tmp_path / "data" / "proposals.json"
    monkeypatch.setattr("coordinator.services.growth.PROPOSALS_FILE", proposals_file)
    # agents dir
    agents_dir = tmp_path / "agents" / "test-agent" / ".kiro" / "skills"
    agents_dir.mkdir(parents=True)
    monkeypatch.chdir(tmp_path)
    return tmp_path


# ── 工具函式測試 ──


def test_compute_shingles():
    """Shingle 計算。"""
    from coordinator.services.growth import _compute_shingles

    shingles = _compute_shingles("hello world this is a test")
    assert len(shingles) > 0
    assert "hello world this" in shingles


def test_jaccard_identical():
    """相同集合 Jaccard = 1.0。"""
    from coordinator.services.growth import _jaccard

    s = {"a", "b", "c"}
    assert _jaccard(s, s) == 1.0


def test_jaccard_disjoint():
    """無交集 Jaccard = 0.0。"""
    from coordinator.services.growth import _jaccard

    assert _jaccard({"a", "b"}, {"c", "d"}) == 0.0


def test_jaccard_partial():
    """部分交集。"""
    from coordinator.services.growth import _jaccard

    score = _jaccard({"a", "b", "c"}, {"b", "c", "d"})
    assert 0.4 < score < 0.6  # 2/4 = 0.5


# ── GrowthDetector 核心邏輯測試 ──


@pytest.mark.asyncio
async def test_no_trigger_below_threshold():
    """不到 3 次不觸發。"""
    from coordinator.services.growth import GrowthDetector
    from coordinator.events.types import Event, EventType

    growth = GrowthDetector()

    # 送 2 次相同 output（不應觸發）
    for _ in range(2):
        await growth.on_agent_output(Event(
            type=EventType.AGENT_OUTPUT,
            data={"agent": "test-agent", "output": "這是一段很長的重複輸出 " * 20},
        ))

    assert len(growth.get_pending()) == 0


@pytest.mark.asyncio
async def test_trigger_at_threshold():
    """達到 3 次觸發提案。"""
    from coordinator.services.growth import GrowthDetector
    from coordinator.events.types import Event, EventType

    growth = GrowthDetector()
    output = "部署新版本到 production 環境，執行 docker pull && docker-compose up -d " * 10

    # 送 3 次相同 output
    for _ in range(3):
        await growth.on_agent_output(Event(
            type=EventType.AGENT_OUTPUT,
            data={"agent": "test-agent", "output": output},
        ))

    pending = growth.get_pending()
    assert len(pending) >= 1
    assert pending[0]["agent"] == "test-agent"
    assert pending[0]["status"] == "pending"


@pytest.mark.asyncio
async def test_no_duplicate_proposal():
    """同一模式不重複提案。"""
    from coordinator.services.growth import GrowthDetector
    from coordinator.events.types import Event, EventType

    growth = GrowthDetector()
    output = "執行資料備份流程，壓縮並上傳到 S3 bucket 完成歸檔 " * 10

    # 送 6 次（觸發 2 次，但只產生 1 個提案）
    for _ in range(6):
        await growth.on_agent_output(Event(
            type=EventType.AGENT_OUTPUT,
            data={"agent": "test-agent", "output": output},
        ))

    pending = growth.get_pending()
    assert len(pending) == 1  # 不重複


@pytest.mark.asyncio
async def test_different_agents_independent():
    """不同 Agent 獨立計算。"""
    from coordinator.services.growth import GrowthDetector
    from coordinator.events.types import Event, EventType

    growth = GrowthDetector()
    output = "分析用戶數據並產生報表，包含 DAU MAU ARPU 等指標 " * 10

    # Agent A 送 2 次
    for _ in range(2):
        await growth.on_agent_output(Event(
            type=EventType.AGENT_OUTPUT,
            data={"agent": "agent-a", "output": output},
        ))
    # Agent B 送 2 次
    for _ in range(2):
        await growth.on_agent_output(Event(
            type=EventType.AGENT_OUTPUT,
            data={"agent": "agent-b", "output": output},
        ))

    # 都不到 3 次，不觸發
    assert len(growth.get_pending()) == 0


# ── 審批流程測試 ──


@pytest.mark.asyncio
async def test_approve_flow(setup_env):
    """核准流程：pending → approved → 寫入 .kiro/skills/。"""
    from coordinator.services.growth import GrowthDetector
    from coordinator.events.types import Event, EventType

    growth = GrowthDetector()
    output = "每天清理 tmp 目錄下超過 7 天的暫存檔案，釋放磁碟空間 " * 10

    for _ in range(3):
        await growth.on_agent_output(Event(
            type=EventType.AGENT_OUTPUT,
            data={"agent": "test-agent", "output": output},
        ))

    pending = growth.get_pending()
    assert len(pending) >= 1

    proposal_id = pending[0]["id"]
    ok = await growth.approve(proposal_id)
    assert ok

    # 確認狀態
    assert pending[0]["status"] == "approved"

    # 確認檔案寫入
    skill_id = pending[0]["skill_id"]
    skill_file = Path("agents/test-agent/.kiro/skills") / skill_id / "SKILL.md"
    assert skill_file.exists()


@pytest.mark.asyncio
async def test_reject_flow():
    """駁回流程。"""
    from coordinator.services.growth import GrowthDetector
    from coordinator.events.types import Event, EventType

    growth = GrowthDetector()
    output = "批次發送 Email 通知給所有訂閱用戶，使用 SES 服務 " * 10

    for _ in range(3):
        await growth.on_agent_output(Event(
            type=EventType.AGENT_OUTPUT,
            data={"agent": "test-agent", "output": output},
        ))

    pending = growth.get_pending()
    proposal_id = pending[0]["id"]
    ok = await growth.reject(proposal_id)
    assert ok
    assert growth.get_pending() == []  # 不再是 pending
