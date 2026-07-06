"""FastAPI — 課程 A 簡易 API。"""
from fastapi import FastAPI
from src.skills.registry import SkillRegistry
from src.wiki.engine import WikiEngine
from pydantic import BaseModel

app = FastAPI(title="AI Bot — 個體 Agent API")
engine = WikiEngine()


@app.get("/")
def root():
    """首頁 — 確認服務正常 + 端點導航。"""
    return {
        "name": "🤖 個體 Agent",
        "status": "running",
        "docs": "/docs",
        "endpoints": {
            "health": "/health",
            "skills": "/api/v1/skills",
            "wiki_query": "POST /api/v1/wiki/query",
            "wiki_ingest": "POST /api/v1/wiki/ingest",
            "wiki_lint": "/api/v1/wiki/lint",
        },
    }


@app.get("/health")
def health_root():
    """健康檢查（短路徑）。"""
    return {"status": "ok"}


@app.get("/api/v1/health")
async def health():
    return {"status": "ok", "service": "a-agent"}


@app.get("/api/v1/skills")
async def list_skills():
    registry = SkillRegistry()
    registry.auto_discover("src.skills.internal")
    return {"skills": registry.list_skills()}


class QueryRequest(BaseModel):
    q: str


@app.post("/api/v1/wiki/query")
async def wiki_query(req: QueryRequest):
    result = await engine.query(req.q)
    return result


@app.post("/api/v1/wiki/ingest")
async def wiki_ingest():
    ingested = engine.ingest()
    return {"ingested": ingested, "count": len(ingested)}


@app.get("/api/v1/wiki/lint")
async def wiki_lint():
    issues = engine.lint()
    return {"issues": issues, "healthy": len(issues) == 0}
