"""ReAct Agent Loop：LLM ↔ Tool 迴圈。"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Callable

from src.llm.provider import FunctionCall, LLMResponse, get_default_provider
from src.llm.tool_registry import ToolRegistry, registry as default_registry

log = logging.getLogger(__name__)


@dataclass
class AgentResult:
    """Agent Loop 執行結果。"""
    text: str
    tool_calls_log: list[dict] = field(default_factory=list)
    iterations: int = 0
    token_usage: dict | None = None


async def agent_loop(
    user_message: str,
    system_prompt: str,
    session_history: list[dict] | None = None,
    tools_registry: ToolRegistry | None = None,
    max_iterations: int = 5,
    on_tool_call: Callable | None = None,
) -> AgentResult:
    """ReAct 迴圈：呼叫 LLM → dispatch tools → loop → 回傳文字。

    Args:
        user_message: 使用者訊息
        system_prompt: system prompt（SOUL + BRAIN + memory + ...）
        session_history: 之前的對話歷史（統一格式）
        tools_registry: Tool Registry 實例（None = 用全域 registry）
        max_iterations: 最大迭代次數
        on_tool_call: callback（tool 被呼叫時通知，用於 TG typing indicator）

    Returns:
        AgentResult 包含最終回覆文字 + tool 執行記錄
    """
    provider = get_default_provider()
    reg = tools_registry or default_registry

    # 組裝 messages
    messages: list[dict] = []
    if session_history:
        messages.extend(session_history)
    messages.append({"role": "user", "content": user_message})

    # Tool schemas
    tool_schemas = reg.all_schemas() if reg.all_names() else None
    tool_calls_log: list[dict] = []
    total_usage = {"input_tokens": 0, "output_tokens": 0}

    for iteration in range(max_iterations):
        log.debug("agent_loop iteration %d/%d", iteration + 1, max_iterations)

        # Context 壓縮（超限保護）
        from src.llm.compression import compress_messages
        messages = compress_messages(messages)

        # 呼叫 LLM
        response: LLMResponse = await provider.chat(
            messages=messages,
            system=system_prompt,
            tools=tool_schemas,
        )

        # 累計 token
        if response.usage:
            total_usage["input_tokens"] += response.usage.get("input_tokens", 0)
            total_usage["output_tokens"] += response.usage.get("output_tokens", 0)

        # 無 function call → 純文字回覆，結束
        if not response.function_calls:
            return AgentResult(
                text=response.text or "",
                tool_calls_log=tool_calls_log,
                iterations=iteration + 1,
                token_usage=total_usage,
            )

        # 有 function call → dispatch 每個 tool
        for fc in response.function_calls:
            log.info("Tool call: %s(%s)", fc.name, list(fc.args.keys()))

            if on_tool_call:
                await on_tool_call(fc.name)

            # Dispatch
            result_str = await reg.dispatch(fc.name, fc.args)

            # 記錄
            tool_calls_log.append({
                "iteration": iteration + 1,
                "tool": fc.name,
                "args": fc.args,
                "result_preview": result_str[:200],
            })

            # Append to messages（Gemini 格式：model 的 function_call + user 的 function_response）
            messages.append({
                "role": "model",
                "parts": [{"function_call": {"name": fc.name, "args": fc.args, "id": fc.id}}],
            })
            messages.append({
                "role": "user",
                "parts": [{"function_response": {"name": fc.name, "response": {"result": result_str}}}],
            })

    # Max iterations 耗盡
    log.warning("agent_loop max_iterations reached (%d)", max_iterations)
    # 嘗試取最後一次有文字的 response
    last_text = "⚠️ 任務太複雜（超過迭代上限），已完成的部分如上。"
    if tool_calls_log:
        last_text = f"⚠️ 已執行 {len(tool_calls_log)} 個工具呼叫，但未能完成最終回覆。請嘗試簡化問題。"

    return AgentResult(
        text=last_text,
        tool_calls_log=tool_calls_log,
        iterations=max_iterations,
        token_usage=total_usage,
    )
