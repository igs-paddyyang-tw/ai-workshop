"""Web Search Skill — 網路搜尋（Gemini grounding）。"""
from business.skills.base import BaseSkill, SkillResult, SkillType


class WebSearchSkill(BaseSkill):
    skill_id = "web_search"
    skill_type = SkillType.LLM
    description = "透過 Gemini API 進行網路搜尋"
    version = "1.0.0"

    async def execute(self, params: dict) -> SkillResult:
        query = params.get("q", params.get("query", ""))
        if not query:
            return SkillResult(success=False, error="Missing query parameter")

        limit = params.get("limit", 5)

        try:
            from business.web_search import web_search
            results = await web_search(query, limit=limit)
            return SkillResult(success=True, data={"results": results, "count": len(results)})
        except Exception as e:
            return SkillResult(success=False, error=str(e))
