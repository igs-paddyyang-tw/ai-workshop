"""Skills API endpoints。"""
from __future__ import annotations

from fastapi import APIRouter, Request
from pydantic import BaseModel

router = APIRouter(prefix="/api/v1/skills", tags=["skills"])


@router.get("")
async def list_skills(request: Request):
    """列出所有已載入 Skill。"""
    registry = getattr(request.app.state, "skill_registry", None)
    if not registry:
        return {"skills": [], "error": "Skills not initialized"}
    return {"skills": registry.list_skills()}


class InvokeRequest(BaseModel):
    skill_id: str
    params: dict = {}
    agent: str = "system"


@router.post("/invoke")
async def invoke_skill(req: InvokeRequest, request: Request):
    """呼叫 Skill。"""
    registry = getattr(request.app.state, "skill_registry", None)
    if not registry:
        return {"success": False, "error": "Skills not initialized"}

    result = await registry.invoke(req.skill_id, req.params, agent=req.agent)
    return result.to_dict()


@router.get("/stats")
async def skill_stats(request: Request):
    """取得 Skill 呼叫統計。"""
    registry = getattr(request.app.state, "skill_registry", None)
    if not registry or not registry.tracker:
        return {"stats": []}

    stats = await registry.tracker.get_stats()
    return {"stats": stats}


@router.get("/pending")
async def skills_pending(request: Request):
    """待審 Skill 提案。"""
    growth = getattr(request.app.state, "growth_detector", None)
    if not growth:
        return {"pending": []}

    pending = growth.get_pending()
    # 不回傳完整 skill_md 節省頻寬
    return {
        "pending": [
            {
                "id": p["id"],
                "agent": p["agent"],
                "skill_id": p["skill_id"],
                "title": p.get("title", ""),
                "proposed_at": p["proposed_at"],
            }
            for p in pending
        ]
    }


class ApproveRequest(BaseModel):
    proposal_id: str


@router.post("/approve")
async def approve_skill(req: ApproveRequest, request: Request):
    """核准 Skill 提案。"""
    growth = getattr(request.app.state, "growth_detector", None)
    if not growth:
        return {"success": False, "error": "Growth detector not available"}

    ok = await growth.approve(req.proposal_id)
    return {"success": ok}


@router.post("/reject")
async def reject_skill(req: ApproveRequest, request: Request):
    """駁回 Skill 提案。"""
    growth = getattr(request.app.state, "growth_detector", None)
    if not growth:
        return {"success": False, "error": "Growth detector not available"}

    ok = await growth.reject(req.proposal_id)
    return {"success": ok}
