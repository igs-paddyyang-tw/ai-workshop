"""Tool: web_search — 使用 Gemini Grounding (Google Search) 搜尋外部資訊。"""
from __future__ import annotations

import logging
import os

log = logging.getLogger(__name__)


async def handle_web_search(args: dict) -> str:
    """用 Gemini + Google Search Grounding 搜尋外部資訊。"""
    query = args.get("query", "").strip()
    if not query:
        return "Error: query 不能為空"

    try:
        import google.generativeai as genai

        api_key = os.getenv("GEMINI_API_KEY", "")
        if not api_key:
            return "Error: 未設定 GEMINI_API_KEY"

        genai.configure(api_key=api_key)

        model = genai.GenerativeModel("gemini-2.5-flash")

        # 使用 Google Search 作為 grounding tool
        response = await model.generate_content_async(
            f"請搜尋並整理以下問題的最新資訊（繁體中文回覆）：{query}",
            tools=[{"google_search": {}}],
        )

        # 擷取文字回覆
        text_parts = []
        sources = []

        if response.candidates:
            candidate = response.candidates[0]
            for part in candidate.content.parts:
                if hasattr(part, "text") and part.text:
                    text_parts.append(part.text)

            # 擷取 grounding metadata（來源連結）
            grounding = getattr(candidate, "grounding_metadata", None)
            if grounding:
                chunks = getattr(grounding, "grounding_chunks", [])
                for chunk in chunks[:5]:
                    web = getattr(chunk, "web", None)
                    if web:
                        title = getattr(web, "title", "")
                        uri = getattr(web, "uri", "")
                        if uri:
                            sources.append(f"- [{title}]({uri})")

        if not text_parts:
            return f"外部搜尋無結果：「{query}」"

        result = "\n".join(text_parts)
        if sources:
            result += "\n\n🔗 來源：\n" + "\n".join(sources)

        log.info("web_search success: query=%s, %d chars", query, len(result))
        return result

    except Exception as e:
        log.error("web_search failed: %s", e)
        return f"Error: 外部搜尋失敗 — {e}"


def register_tools():
    from src.llm.tool_registry import Tool, registry
    registry.register(Tool(
        name="web_search",
        description="搜尋外部網路資訊（Google Search）。當知識庫查無結果、需要最新資訊或即時資料時使用。",
        parameters={
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "搜尋關鍵詞（自然語言）"},
            },
            "required": ["query"],
        },
        handler=handle_web_search,
    ))
