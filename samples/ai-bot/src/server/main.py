"""FastAPI — 課程 A 簡易 API + Web UI。"""
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from src.skills.registry import SkillRegistry
from src.wiki.engine import WikiEngine
from pydantic import BaseModel

TEMPLATES_DIR = Path(__file__).resolve().parents[2] / "templates"

app = FastAPI(title="AI Bot — 個體 Agent API")
engine = WikiEngine()


# ─── Web UI ──────────────────────────────────────────

@app.get("/", response_class=HTMLResponse)
def chat_page():
    """聊天室首頁。"""
    html = (TEMPLATES_DIR / "index.html").read_text(encoding="utf-8")
    return HTMLResponse(content=html)


@app.get("/admin", response_class=HTMLResponse)
def admin_page():
    """管理介面。"""
    html = (TEMPLATES_DIR / "admin.html").read_text(encoding="utf-8")
    return HTMLResponse(content=html)


# ─── API ─────────────────────────────────────────────

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
