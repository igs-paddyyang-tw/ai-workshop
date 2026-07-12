"""GrowthDetector — 偵測重複模式，自動提案 Skill。"""
from __future__ import annotations

import hashlib
import json
import logging
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Awaitable

from coordinator.events.types import Event, EventType

log = logging.getLogger("services.growth")

PROPOSALS_FILE = Path("data/proposals.json")
SIMILARITY_THRESHOLD = 0.7   # Jaccard 相似度
TRIGGER_COUNT = 3            # 相似 output ≥ 3 次觸發


class GrowthDetector:
    """偵測 Agent 重複行為模式，自動提案 Skill。

    流程：
    1. 每次 AGENT_OUTPUT 計算 shingle hash
    2. 累積相似 output ≥ TRIGGER_COUNT 觸發提案
    3. LLM 產生 SKILL.md 草稿 → proposals.json
    4. TG 推送 InlineKeyboard 審批
    """

    def __init__(
        self,
        gemini_fn: Callable[[str, str], Awaitable[str | None]] | None = None,
        notify_fn: Callable[[str, dict], Awaitable[None]] | None = None,
        event_bus=None,
    ) -> None:
        self._gemini_fn = gemini_fn
        self._notify_fn = notify_fn  # (agent, proposal) → TG 推送
        self._event_bus = event_bus
        # agent → [shingle_set, ...]（最近 20 筆）
        self._history: dict[str, list[set[str]]] = {}
        self._proposals = _load_proposals()

    async def on_agent_output(self, event: Event) -> None:
        """EventBus handler：分析 output，偵測重複。"""
        data = event.data
        agent = data.get("agent_id") or data.get("agent", "")
        output = data.get("output", "")

        if not agent or not output or len(output) < 50:
            return

        # 計算 shingle set
        shingles = _compute_shingles(output)
        history = self._history.setdefault(agent, [])

        # 計算與歷史的相似度
        similar_count = sum(
            1 for prev in history
            if _jaccard(shingles, prev) >= SIMILARITY_THRESHOLD
        )

        # 保留最近 20 筆
        history.append(shingles)
        if len(history) > 20:
            history.pop(0)

        # 達到閾值 → 提案
        if similar_count >= TRIGGER_COUNT - 1:  # 加上自己 = TRIGGER_COUNT
            # 避免重複提案同一模式
            pattern_hash = _hash_shingle_set(shingles)
            if self._has_recent_proposal(agent, pattern_hash):
                return

            log.info("Growth triggered for %s (similar=%d)", agent, similar_count + 1)
            await self._propose_skill(agent, output, pattern_hash)

    async def _propose_skill(self, agent: str, sample_output: str, pattern_hash: str) -> None:
        """產生 Skill 草稿 → 存入 proposals.json。"""
        skill_md = await self._generate_skill_draft(agent, sample_output)
        if not skill_md:
            return

        proposal = {
            "id": str(uuid.uuid4())[:8],
            "agent": agent,
            "skill_id": _extract_skill_id(skill_md),
            "title": _extract_title(skill_md),
            "status": "pending",
            "pattern_hash": pattern_hash,
            "proposed_at": datetime.now(timezone.utc).isoformat(),
            "resolved_at": None,
            "skill_md": skill_md,
        }

        self._proposals.append(proposal)
        _save_proposals(self._proposals)

        # 發事件
        if self._event_bus:
            await self._event_bus.emit(Event(
                type=EventType.SKILL_PROPOSED,
                data={"proposal_id": proposal["id"], "agent": agent, "skill_id": proposal["skill_id"]},
            ))

        # TG 通知
        if self._notify_fn:
            await self._notify_fn(agent, proposal)

        log.info("Skill proposed: %s (agent=%s)", proposal["skill_id"], agent)

    async def _generate_skill_draft(self, agent: str, sample_output: str) -> str | None:
        """用 LLM 產生 SKILL.md。"""
        if not self._gemini_fn:
            # Fallback: 簡單模板
            return _fallback_skill_md(agent, sample_output)

        prompt = (
            f"根據以下 Agent 的重複輸出模式，產出一份 SKILL.md 描述。\n\n"
            f"Agent: {agent}\n"
            f"重複輸出範本（節錄）：\n{sample_output[:1500]}\n\n"
            f"產出格式：\n"
            f"```markdown\n"
            f"## skill_id\n"
            f"description: ...\n"
            f"inputs:\n  - name: param1\n    type: str\n"
            f"steps:\n  1. ...\n  2. ...\n"
            f"```\n"
            f"只輸出 markdown，不要其他說明。"
        )

        try:
            result = await self._gemini_fn(prompt, "你是 Skill 設計師。")
            if result and len(result.strip()) > 30:
                return result.strip()
        except Exception as e:
            log.warning("LLM skill draft failed: %s", e)

        return _fallback_skill_md(agent, sample_output)

    def _has_recent_proposal(self, agent: str, pattern_hash: str) -> bool:
        """避免重複提案同一模式。"""
        for p in self._proposals:
            if (
                p["agent"] == agent
                and p.get("pattern_hash") == pattern_hash
                and p["status"] in ("pending", "approved")
            ):
                return True
        return False

    # ─── 審批操作 ───

    def get_pending(self, agent: str | None = None) -> list[dict]:
        """取得待審提案。"""
        pending = [p for p in self._proposals if p["status"] == "pending"]
        if agent:
            pending = [p for p in pending if p["agent"] == agent]
        return pending

    async def approve(self, proposal_id: str) -> bool:
        """核准提案 → 寫入 .kiro/skills/。"""
        proposal = self._find_proposal(proposal_id)
        if not proposal:
            return False

        proposal["status"] = "approved"
        proposal["resolved_at"] = datetime.now(timezone.utc).isoformat()
        _save_proposals(self._proposals)

        # 寫入 agents/{name}/.kiro/skills/{skill_id}/SKILL.md
        agent = proposal["agent"]
        skill_id = proposal["skill_id"]
        skill_dir = Path("agents") / agent / ".kiro" / "skills" / skill_id
        skill_dir.mkdir(parents=True, exist_ok=True)
        (skill_dir / "SKILL.md").write_text(proposal["skill_md"], encoding="utf-8")

        # 發事件
        if self._event_bus:
            await self._event_bus.emit(Event(
                type=EventType.SKILL_APPROVED,
                data={"proposal_id": proposal_id, "skill_id": skill_id, "agent": agent},
            ))

        log.info("Skill approved: %s → %s", skill_id, skill_dir)
        return True

    async def reject(self, proposal_id: str) -> bool:
        """駁回提案。"""
        proposal = self._find_proposal(proposal_id)
        if not proposal:
            return False

        proposal["status"] = "rejected"
        proposal["resolved_at"] = datetime.now(timezone.utc).isoformat()
        _save_proposals(self._proposals)
        log.info("Skill rejected: %s", proposal_id)
        return True

    def _find_proposal(self, proposal_id: str) -> dict | None:
        for p in self._proposals:
            if p["id"] == proposal_id:
                return p
        return None


# ─── 工具函式 ───


def _compute_shingles(text: str, n: int = 3) -> set[str]:
    """計算文字的 n-gram shingle set。"""
    words = text.lower().split()[:200]  # 限制長度
    if len(words) < n:
        return set(words)
    return {" ".join(words[i:i+n]) for i in range(len(words) - n + 1)}


def _jaccard(set_a: set, set_b: set) -> float:
    """Jaccard 相似度。"""
    if not set_a or not set_b:
        return 0.0
    intersection = len(set_a & set_b)
    union = len(set_a | set_b)
    return intersection / union if union > 0 else 0.0


def _hash_shingle_set(shingles: set[str]) -> str:
    """產生 shingle set 的 hash。"""
    sorted_shingles = sorted(shingles)[:50]
    text = "|".join(sorted_shingles)
    return hashlib.sha256(text.encode()).hexdigest()[:16]


def _extract_skill_id(skill_md: str) -> str:
    """從 SKILL.md 提取 skill_id。"""
    for line in skill_md.splitlines():
        if line.startswith("## "):
            return line[3:].strip().replace(" ", "_").lower()[:30]
    return f"auto_{uuid.uuid4().hex[:6]}"


def _extract_title(skill_md: str) -> str:
    """從 SKILL.md 提取標題。"""
    for line in skill_md.splitlines():
        if line.startswith("## "):
            return line[3:].strip()
        if "description:" in line:
            return line.split(":", 1)[1].strip()[:60]
    return "Auto-generated Skill"


def _fallback_skill_md(agent: str, sample_output: str) -> str:
    """無 LLM 時的 fallback 模板。"""
    snippet = sample_output[:200].replace("\n", " ")
    skill_id = f"auto_{hashlib.md5(snippet.encode()).hexdigest()[:6]}"
    return (
        f"## {skill_id}\n"
        f"description: 自動偵測的重複模式（{agent}）\n"
        f"inputs:\n  - name: input\n    type: str\n"
        f"steps:\n  1. 執行偵測到的重複操作\n"
        f"sample_output: |\n  {snippet}\n"
    )


def _load_proposals() -> list[dict]:
    """載入 proposals.json。"""
    if PROPOSALS_FILE.exists():
        try:
            return json.loads(PROPOSALS_FILE.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, IOError):
            return []
    return []


def _save_proposals(proposals: list[dict]) -> None:
    """儲存 proposals.json。"""
    PROPOSALS_FILE.parent.mkdir(parents=True, exist_ok=True)
    PROPOSALS_FILE.write_text(
        json.dumps(proposals, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
