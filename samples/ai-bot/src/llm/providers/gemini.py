"""Gemini Provider — google-generativeai SDK。"""
from __future__ import annotations

import json
import logging
from dataclasses import dataclass

from src.llm.provider import FunctionCall, LLMResponse

log = logging.getLogger(__name__)


@dataclass
class GeminiProvider:
    """Gemini API Provider with Function Calling support."""

    name: str = "gemini"
    api_key: str = ""
    model: str = "gemini-2.0-flash"
    temperature: float = 0.7

    def __post_init__(self):
        import google.generativeai as genai
        genai.configure(api_key=self.api_key)
        self._genai = genai

    async def chat(
        self,
        messages: list[dict],
        system: str = "",
        tools: list[dict] | None = None,
        temperature: float | None = None,
    ) -> LLMResponse:
        """呼叫 Gemini API。"""
        temp = temperature if temperature is not None else self.temperature

        # 建立 model
        model_kwargs = {}
        if system:
            model_kwargs["system_instruction"] = system

        # Tools 轉換
        gemini_tools = None
        if tools:
            gemini_tools = [{"function_declarations": tools}]

        model = self._genai.GenerativeModel(
            model_name=self.model,
            generation_config={"temperature": temp},
            tools=gemini_tools,
            **model_kwargs,
        )

        # Messages 轉換：統一格式 → Gemini Content 格式
        contents = self._convert_messages(messages)

        try:
            response = await model.generate_content_async(contents)
        except Exception as e:
            log.error("Gemini API error: %s", e)
            return LLMResponse(text=f"⚠️ Gemini API 錯誤: {e}")

        # 解析回應
        return self._parse_response(response)

    def _convert_messages(self, messages: list[dict]) -> list:
        """統一格式 → Gemini Content 格式。"""
        from google.generativeai.types import content_types

        contents = []
        for msg in messages:
            role = msg.get("role", "user")
            # Gemini 只有 "user" 和 "model" 兩種角色
            gemini_role = "model" if role in ("assistant", "model") else "user"

            parts = msg.get("parts")
            if parts:
                # 已經是 Gemini 格式（function_call / function_response）
                contents.append({"role": gemini_role, "parts": parts})
            else:
                # 純文字
                text = msg.get("content", "")
                if text:
                    contents.append({"role": gemini_role, "parts": [{"text": text}]})

        return contents

    def _parse_response(self, response) -> LLMResponse:
        """解析 Gemini response → 統一 LLMResponse。"""
        try:
            candidate = response.candidates[0]
            parts = candidate.content.parts
        except (IndexError, AttributeError):
            return LLMResponse(text="⚠️ Gemini 回傳無內容")

        function_calls = []
        text_parts = []

        for part in parts:
            if hasattr(part, "function_call") and part.function_call.name:
                fc = part.function_call
                # args 可能是 MapComposite，轉成 dict
                args = dict(fc.args) if fc.args else {}
                function_calls.append(FunctionCall(
                    name=fc.name,
                    args=args,
                ))
            elif hasattr(part, "text") and part.text:
                text_parts.append(part.text)

        # 解析 usage
        usage = None
        if hasattr(response, "usage_metadata") and response.usage_metadata:
            um = response.usage_metadata
            usage = {
                "input_tokens": getattr(um, "prompt_token_count", 0),
                "output_tokens": getattr(um, "candidates_token_count", 0),
            }

        if function_calls:
            return LLMResponse(function_calls=function_calls, usage=usage)
        else:
            return LLMResponse(text="\n".join(text_parts) or None, usage=usage)
