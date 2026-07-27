"""LLM Router — 統一多模型呼叫，走 Provider 層自動 fallback。"""
from __future__ import annotations

import os
from src.skills.base import BaseSkill, SkillResult


class RouterSkill(BaseSkill):
    skill_id = "router"
    description = "統一多模型呼叫，自動 fallback（gemini → openai）"
    version = "1.0.0"

    async def execute(self, params: dict) -> SkillResult:
        message = params.get("message", "")
        system_prompt = params.get("system_prompt", "")
        if not message:
            return SkillResult(success=False, error="message is required")
        result = await chat(message, system_prompt)
        return SkillResult(success=True, data={"reply": result})


def available_backends() -> list[str]:
    """列出可用的 LLM 後端。"""
    backends = []
    if os.getenv("GEMINI_API_KEY"):
        backends.append("gemini")
    if os.getenv("OPENAI_API_KEY"):
        backends.append("openai")
    return backends


async def chat(
    message: str,
    system_prompt: str = "",
    backend: str = "",
    model: str = "",
) -> str:
    """統一對話介面，走 Provider 層。"""
    try:
        from src.llm.chat import simple_chat
        result = await simple_chat(message, system=system_prompt)
        return result or ""
    except Exception:
        return ""
