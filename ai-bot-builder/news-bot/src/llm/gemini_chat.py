"""Gemini API 即時對話（1-5 秒，選配）。"""
import logging
import os

logger = logging.getLogger(__name__)

_client = None


def _get_client():
    global _client
    if _client is None:
        from google import genai
        _client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    return _client


def is_available() -> bool:
    """檢查 Gemini API Key 是否有設定。"""
    return bool(os.getenv("GEMINI_API_KEY"))


async def chat(message: str, system_prompt: str = "") -> str:
    """單輪 Gemini API 對話（含重試）。無 Key 時回傳空字串。"""
    if not is_available():
        return ""

    import asyncio
    client = _get_client()
    config = {"system_instruction": system_prompt} if system_prompt else None

    for attempt in range(3):
        try:
            response = await client.aio.models.generate_content(
                model=os.getenv("GEMINI_MODEL", "gemini-2.5-flash"),
                contents=message,
                config=config,
            )
            return response.text or ""
        except Exception as e:
            err_str = str(e)
            if "503" in err_str or "UNAVAILABLE" in err_str or "overloaded" in err_str.lower():
                logger.warning("Gemini API 503 (attempt %d/3), 重試中...", attempt + 1)
                await asyncio.sleep(2 * (attempt + 1))
                continue
            logger.error("Gemini API 呼叫失敗: %s", e)
            return ""

    logger.error("Gemini API 重試 3 次後仍失敗")
    return ""
