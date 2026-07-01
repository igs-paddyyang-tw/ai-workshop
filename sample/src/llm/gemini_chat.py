"""Gemini API 即時對話。

Workshop 01 的核心：LLM 對話 + SOUL.md system prompt 注入。
"""
from __future__ import annotations

import os
import httpx


async def ask_gemini(prompt: str, system_prompt: str = "") -> str:
    """呼叫 Gemini API 產生回答。

    Args:
        prompt: 使用者訊息
        system_prompt: 系統提詞（來自 soul.md）
    """
    key = os.getenv("GEMINI_API_KEY", "")
    if not key:
        return "⚠️ GEMINI_API_KEY 未設定"

    # 組裝 request body
    body: dict = {"contents": [{"parts": [{"text": prompt}]}]}
    if system_prompt:
        body["system_instruction"] = {"parts": [{"text": system_prompt}]}

    async with httpx.AsyncClient(timeout=30) as client:
        r = await client.post(
            f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={key}",
            json=body,
        )
        r.raise_for_status()
        data = r.json()
        return data["candidates"][0]["content"]["parts"][0]["text"]
