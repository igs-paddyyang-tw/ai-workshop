"""Gemini API 即時對話。"""
from __future__ import annotations

import os
import httpx


async def ask_gemini(prompt: str) -> str:
    """呼叫 Gemini API 產生回答。"""
    key = os.getenv("GEMINI_API_KEY", "")
    if not key:
        return "⚠️ GEMINI_API_KEY 未設定"
    async with httpx.AsyncClient(timeout=30) as client:
        r = await client.post(
            f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={key}",
            json={"contents": [{"parts": [{"text": prompt}]}]},
        )
        r.raise_for_status()
        data = r.json()
        return data["candidates"][0]["content"]["parts"][0]["text"]
