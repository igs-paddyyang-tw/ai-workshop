"""Layer 3：LLM Rerank（可選，有 GEMINI_API_KEY 才啟用）。"""
from __future__ import annotations

import json
import logging
import os

import httpx

log = logging.getLogger("wiki.search.rerank")


def is_available() -> bool:
    """檢查 Gemini API 是否可用。"""
    key = os.environ.get("GEMINI_API_KEY", "")
    return bool(key) and key != "your_gemini_api_key_here"


async def rerank(query: str, results: list[dict], top_k: int = 5) -> list[dict]:
    """使用 LLM 對搜尋結果重新排序。

    Args:
        query: 原始查詢
        results: 前幾層的搜尋結果
        top_k: 回傳筆數

    Returns:
        重排後的結果
    """
    if not is_available() or not results:
        return results[:top_k]

    api_key = os.environ["GEMINI_API_KEY"]
    model = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"

    # 準備 prompt
    candidates = "\n".join(
        f"{i+1}. [{r['title']}] {r.get('body_preview', r.get('snippet', ''))[:100]}"
        for i, r in enumerate(results[:10])
    )

    prompt = (
        f"根據查詢「{query}」，請將以下文件按相關性從高到低排序。\n"
        f"只回傳排序後的編號列表（如：3,1,5,2,4），不要其他文字。\n\n"
        f"文件列表：\n{candidates}"
    )

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.post(url, json={
                "contents": [{"parts": [{"text": prompt}]}],
            })
            if resp.status_code != 200:
                return results[:top_k]
            data = resp.json()
            text = data["candidates"][0]["content"]["parts"][0]["text"]

        # 解析排序
        indices = _parse_ranking(text, len(results))
        reranked = [results[i] for i in indices if i < len(results)]

        # 更新分數
        for rank, entry in enumerate(reranked):
            entry["score"] = round(1.0 - rank * 0.1, 2)
            entry["match_type"] = "reranked"

        return reranked[:top_k]
    except Exception as e:
        log.warning("LLM rerank failed: %s", e)
        return results[:top_k]


def _parse_ranking(text: str, max_idx: int) -> list[int]:
    """解析 LLM 回傳的排序編號。"""
    import re
    numbers = re.findall(r"\d+", text)
    indices: list[int] = []
    seen: set[int] = set()
    for n in numbers:
        idx = int(n) - 1  # 1-based → 0-based
        if 0 <= idx < max_idx and idx not in seen:
            indices.append(idx)
            seen.add(idx)
    return indices
