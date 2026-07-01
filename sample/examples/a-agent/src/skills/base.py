"""BaseSkill 插件系統核心。"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from pydantic import BaseModel


class SkillType(str, Enum):
    PYTHON = "python"
    LLM = "llm"
    EXTERNAL = "external"


class SkillParam(BaseModel):
    """Skill 輸入參數基底類別。"""


@dataclass
class SkillResult:
    """Skill 執行結果。"""
    success: bool
    data: dict[str, Any] = field(default_factory=dict)
    error: str = ""


class BaseSkill(ABC):
    """Skill 基底類別。"""
    skill_id: str = ""
    skill_type: SkillType = SkillType.PYTHON
    description: str = ""
    version: str = "1.0.0"
    input_schema: type[SkillParam] | None = None

    def validate_params(self, params: dict) -> bool:
        """驗證參數。"""
        if not self.input_schema:
            return True
        try:
            self.input_schema(**params)
            return True
        except Exception:
            return False

    def to_tool_definition(self) -> dict:
        """產生 tool definition。"""
        schema = self.input_schema.model_json_schema() if self.input_schema else {}
        return {
            "skill_id": self.skill_id,
            "description": self.description,
            "parameters": schema,
        }

    @abstractmethod
    async def execute(self, params: dict) -> SkillResult:
        """執行 Skill。"""
        ...


__all__ = ["BaseSkill", "SkillParam", "SkillResult", "SkillType"]
