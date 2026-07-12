"""Memory API endpoints。"""
from __future__ import annotations

from fastapi import APIRouter, Query
from pydantic import BaseModel

router = APIRouter(prefix="/api/v1/memory", tags=["memory"])


class RecallRequest(BaseModel):
    agent: str
    query: str
    k: int = 5


class ConsolidateRequest(BaseModel):
    agent: str


@router.post("/recall")
async def recall_endpoint(req: RecallRequest):
    """FTS5 查詢 Agent 記憶。"""
    from coordinator.memory.recall import recall

    results = await recall(req.agent, req.query, k=req.k)
    return {"results": [r.to_dict() for r in results], "count": len(results)}


@router.get("/daily/{agent}")
async def daily_log_endpoint(agent: str, date: str = Query(None)):
    """取得 Agent 的 daily log。"""
    from pathlib import Path

    daily_dir = Path("agents") / agent / "memory" / "daily"
    if not daily_dir.exists():
        return {"entries": [], "error": "Agent daily dir not found"}

    if date:
        files = [daily_dir / f"{date}.md"]
    else:
        files = sorted(daily_dir.glob("*.md"), reverse=True)[:7]

    entries = []
    for f in files:
        if f.exists():
            entries.append({
                "date": f.stem,
                "content": f.read_text(encoding="utf-8")[:5000],
            })

    return {"entries": entries}


@router.post("/consolidate")
async def consolidate_endpoint(req: ConsolidateRequest):
    """手動蒸餾 daily → memory.md。"""
    from coordinator.memory.consolidate import consolidate

    result = await consolidate(req.agent)
    return {"agent": req.agent, "result": result[:2000]}
