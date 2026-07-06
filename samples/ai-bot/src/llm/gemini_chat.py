"""Gemini API 即時對話（最快路徑，不經 CLI）。"""
from __future__ import annotations

import logging
import os

import httpx

log = logging.getLogger("llm.gemini")


async def gemini_chat(prompt: str, system: str = "") -> str | None:
    """直接呼叫 Gemini API（跳過 CLI，2-3 秒回覆）。"""
    api_key = os.getenv("GEMINI_API_KEY", "")
    if not api_key:
        log.warning("GEMINI_API_KEY not set")
        return None

    model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"

    contents = []
    if system:
        contents.append({"role": "user", "parts": [{"text": f"[System] {system}"}]})
        contents.append({"role": "model", "parts": [{"text": "了解。"}]})
    contents.append({"role": "user", "parts": [{"text": prompt}]})

    log.debug("Gemini request: model=%s prompt=%s", model, prompt[:80])

    async with httpx.AsyncClient(timeout=30) as client:
        try:
            r = await client.post(url, json={"contents": contents})
            log.debug("Gemini response: status=%d", r.status_code)
            if r.status_code != 200:
                log.error("Gemini API error: status=%d body=%s", r.status_code, r.text[:200])
                return None
            data = r.json()
            text = data["candidates"][0]["content"]["parts"][0]["text"]
            log.debug("Gemini reply: %d chars", len(text))
            return text
        except Exception as e:
            log.error("Gemini exception: %s", e)
            return None
