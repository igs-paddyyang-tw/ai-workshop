"""SkillRegistry — 自動發現與管理 Skills。"""
from __future__ import annotations

import importlib
import pkgutil
from typing import Any

from .base import BaseSkill, SkillResult


class SkillRegistry:
    """Skill 註冊表。"""

    def __init__(self) -> None:
        self._skills: dict[str, BaseSkill] = {}

    def register(self, skill: BaseSkill) -> None:
        """註冊 Skill。"""
        self._skills[skill.skill_id] = skill

    def get(self, skill_id: str) -> BaseSkill | None:
        """取得 Skill。"""
        return self._skills.get(skill_id)

    def list_skills(self) -> list[dict[str, Any]]:
        """列出所有已註冊 Skills。"""
        return [
            {"skill_id": s.skill_id, "description": s.description, "version": s.version}
            for s in self._skills.values()
        ]

    async def invoke(self, skill_id: str, params: dict) -> SkillResult:
        """呼叫 Skill。"""
        skill = self._skills.get(skill_id)
        if not skill:
            return SkillResult(success=False, error=f"Skill not found: {skill_id}")
        if not skill.validate_params(params):
            return SkillResult(success=False, error=f"Invalid params for skill: {skill_id}")
        try:
            return await skill.execute(params)
        except Exception as e:
            return SkillResult(success=False, error=str(e))

    def auto_discover(self, package_name: str) -> int:
        """自動發現並註冊 package 下的所有 Skills。"""
        count = 0
        package = importlib.import_module(package_name)
        for _, module_name, _ in pkgutil.iter_modules(package.__path__):
            module = importlib.import_module(f"{package_name}.{module_name}")
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if (
                    isinstance(attr, type)
                    and issubclass(attr, BaseSkill)
                    and attr is not BaseSkill
                    and attr.skill_id
                ):
                    self.register(attr())
                    count += 1
        return count
