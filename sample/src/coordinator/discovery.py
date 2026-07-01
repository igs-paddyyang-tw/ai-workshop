"""Agent Discovery — 根據任務需求自動匹配最適 Agent。

Workshop 03 程式碼閱讀重點：
  - match_agent(): 根據 capabilities 標籤匹配最適 Agent
  - score_match(): 計算任務需求與 Agent 能力的匹配分數
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import yaml


@dataclass
class AgentProfile:
    """Agent 能力描述。"""

    id: str
    name: str
    role: str
    skills: list[str] = field(default_factory=list)
    available: bool = True


@dataclass
class MatchResult:
    """匹配結果。"""

    agent_id: str
    score: float  # 0.0 ~ 1.0
    matched_skills: list[str] = field(default_factory=list)
    reason: str = ""


class AgentDiscovery:
    """Agent 自動發現與匹配系統。

    使用方式:
        discovery = AgentDiscovery.from_yaml("team.yaml")
        result = discovery.match_agent(required_skills=["python", "data-analysis"])
        # → MatchResult(agent_id="backend", score=0.67, matched_skills=["python"])
    """

    def __init__(self, agents: list[AgentProfile] | None = None) -> None:
        self._agents: list[AgentProfile] = agents or []

    @classmethod
    def from_yaml(cls, path: str | Path) -> "AgentDiscovery":
        """從 team.yaml 載入 Agent 清單。"""
        path = Path(path)
        if not path.exists():
            return cls([])
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        agents = [
            AgentProfile(
                id=a["id"],
                name=a.get("name", a["id"]),
                role=a.get("role", ""),
                skills=a.get("skills", []),
            )
            for a in data.get("agents", [])
        ]
        return cls(agents)

    # ─── 核心方法 ────────────────────────────────────────

    def match_agent(
        self,
        required_skills: list[str],
        *,
        prefer_role: str = "",
        exclude: list[str] | None = None,
    ) -> MatchResult | None:
        """匹配最適 Agent。

        根據 required_skills 計算每個 Agent 的匹配分數，
        回傳分數最高且可用的 Agent。

        Args:
            required_skills: 任務需要的能力標籤列表
            prefer_role: 偏好角色（加分項）
            exclude: 排除的 agent_id（已在忙的）

        Returns:
            最佳匹配結果，若無匹配則回傳 None。
        """
        exclude = exclude or []
        best: MatchResult | None = None

        for agent in self._agents:
            if not agent.available:
                continue
            if agent.id in exclude:
                continue

            result = self.score_match(agent, required_skills, prefer_role)

            if result.score > 0 and (best is None or result.score > best.score):
                best = result

        return best

    def score_match(
        self,
        agent: AgentProfile,
        required_skills: list[str],
        prefer_role: str = "",
    ) -> MatchResult:
        """計算任務需求與 Agent 能力的匹配分數。

        計算邏輯：
        1. 基礎分 = 交集技能數 / 需求技能數（0.0 ~ 1.0）
        2. 角色加分 = 偏好角色匹配時 +0.1（上限 1.0）

        Args:
            agent: Agent 能力描述
            required_skills: 任務需要的技能
            prefer_role: 偏好角色

        Returns:
            匹配結果（含分數與原因）
        """
        if not required_skills:
            return MatchResult(
                agent_id=agent.id,
                score=0.5,
                reason="無明確需求，預設中等分數",
            )

        # 計算交集
        agent_skill_set = set(s.lower() for s in agent.skills)
        required_set = set(s.lower() for s in required_skills)
        matched = agent_skill_set & required_set

        # 基礎分數 = 覆蓋率
        base_score = len(matched) / len(required_set)

        # 角色加分
        role_bonus = 0.1 if prefer_role and prefer_role.lower() in agent.role.lower() else 0.0

        final_score = min(base_score + role_bonus, 1.0)

        # 組裝理由
        reason_parts = []
        if matched:
            reason_parts.append(f"匹配技能: {', '.join(sorted(matched))}")
        if role_bonus > 0:
            reason_parts.append(f"角色匹配: {agent.role}")
        if not matched and not role_bonus:
            reason_parts.append("無匹配技能")

        return MatchResult(
            agent_id=agent.id,
            score=round(final_score, 2),
            matched_skills=sorted(matched),
            reason="; ".join(reason_parts),
        )

    # ─── 輔助方法 ────────────────────────────────────────

    def list_agents(self) -> list[dict]:
        """列出所有 Agent 及其能力。"""
        return [
            {
                "id": a.id,
                "name": a.name,
                "role": a.role,
                "skills": a.skills,
                "available": a.available,
            }
            for a in self._agents
        ]

    def set_available(self, agent_id: str, available: bool) -> None:
        """設定 Agent 可用狀態。"""
        for agent in self._agents:
            if agent.id == agent_id:
                agent.available = available
                break

    def find_all_matches(
        self,
        required_skills: list[str],
        *,
        min_score: float = 0.1,
    ) -> list[MatchResult]:
        """找出所有匹配的 Agent（按分數降序）。"""
        results: list[MatchResult] = []
        for agent in self._agents:
            if not agent.available:
                continue
            result = self.score_match(agent, required_skills)
            if result.score >= min_score:
                results.append(result)
        return sorted(results, key=lambda r: r.score, reverse=True)
