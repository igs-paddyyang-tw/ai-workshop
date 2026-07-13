"""Gemini ReAct Agent Loop — 帶 Function Calling 的對話迴圈。

架構：
  1. 組裝 contents（history + user message）
  2. 呼叫 Gemini API（帶 tools/function_declarations）
  3. 若回應包含 functionCall → 執行 tool → 結果回傳 → 重複
  4. 若回應為純文字 → 回傳最終回覆
  5. 最多 MAX_ITERATIONS 次（防止無限迴圈）
"""
from __future__ import annotations

import logging
import os
from typing import Any

import httpx

from src.tools.registry import TOOL_DECLARATIONS
from src.tools.handlers import dispatch_tool

log = logging.getLogger("llm.agent_loop")

MAX_ITERATIONS = 5


async def agent_loop(
    prompt: str,
    *,
    system: str = "",
    history: list[dict[str, Any]] | None = None,
) -> str | None:
    """執行 Gemini ReAct 迴圈。

    Args:
        prompt: 使用者訊息
        system: system prompt（注入為首輪 user+model 交換）
        history: 對話歷史（Gemini contents 格式）

    Returns:
        最終文字回覆，或 None（失敗）
    """
    api_key = os.getenv("GEMINI_API_KEY", "")
    if not api_key:
        log.warning("GEMINI_API_KEY not set")
        return None

    model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    url = (
        f"https://generativelanguage.googleapis.com/v1beta/models/{model}"
        f":generateContent?key={api_key}"
    )

    # ── 組裝 contents ──
    contents: list[dict] = []

    # System prompt 以首輪交換注入
    if system:
        contents.append({"role": "user", "parts": [{"text": f"[System]\n{system}"}]})
        contents.append({"role": "model", "parts": [{"text": "了解，我會遵循以上指示。"}]})

    # 歷史對話
    if history:
        contents.extend(history)

    # 當前使用者訊息
    contents.append({"role": "user", "parts": [{"text": prompt}]})

    # ── Tools 定義 ──
    tools_payload = [{"function_declarations": TOOL_DECLARATIONS}]

    # ── ReAct Loop ──
    for iteration in range(MAX_ITERATIONS):
        log.debug(
            "agent_loop iteration %d/%d, contents=%d messages",
            iteration + 1, MAX_ITERATIONS, len(contents),
        )

        async with httpx.AsyncClient(timeout=60) as client:
            try:
                response = await client.post(
                    url,
                    json={
                        "contents": contents,
                        "tools": tools_payload,
                    },
                )
            except Exception as e:
                log.error("Gemini API request failed: %s", e)
                return None

        if response.status_code != 200:
            log.error(
                "Gemini API error: status=%d body=%s",
                response.status_code, response.text[:300],
            )
            return None

        data = response.json()

        # 解析 candidate
        candidates = data.get("candidates", [])
        if not candidates:
            log.error("Gemini returned no candidates")
            return None

        candidate = candidates[0]
        content = candidate.get("content", {})
        parts = content.get("parts", [])

        if not parts:
            log.error("Gemini returned empty parts")
            return None

        # ── 檢查是否有 functionCall ──
        function_calls = [p for p in parts if "functionCall" in p]

        if function_calls:
            # 加入 model 的回應到 contents
            contents.append({"role": "model", "parts": parts})

            # 執行每個 function call
            function_responses: list[dict] = []
            for fc_part in function_calls:
                fc = fc_part["functionCall"]
                tool_name = fc["name"]
                tool_args = fc.get("args", {})

                log.info("  🔧 tool_call: %s(%s)", tool_name, str(tool_args)[:100])

                # Dispatch
                result = dispatch_tool(tool_name, tool_args)
                log.info("  📋 tool_result: %s", result[:100])

                function_responses.append({
                    "functionResponse": {
                        "name": tool_name,
                        "response": {"result": result},
                    }
                })

            # 回傳 function results 給 Gemini
            contents.append({"role": "user", "parts": function_responses})
            # 繼續迴圈
            continue

        # ── 純文字回覆 → 結束 ──
        text_parts = [p.get("text", "") for p in parts if "text" in p]
        final_text = "\n".join(text_parts).strip()

        if final_text:
            log.info("agent_loop completed in %d iteration(s), %d chars",
                     iteration + 1, len(final_text))
            return final_text
        else:
            log.warning("Gemini returned parts without text or functionCall")
            return None

    # 超過 max iterations
    log.warning("agent_loop reached MAX_ITERATIONS (%d)", MAX_ITERATIONS)
    return "⚠️ 處理步驟過多，已停止。請簡化需求後重試。"
