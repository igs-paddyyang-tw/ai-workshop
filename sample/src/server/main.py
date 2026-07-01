"""FastAPI 入口 — 21 端點 + Dashboard + Wiki。"""
from __future__ import annotations

import os
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path
from pydantic import BaseModel

from src.server.api.admin import router as admin_router
from src.wiki.engine import WikiEngine

load_dotenv()

templates = Jinja2Templates(directory=str(Path(__file__).parent / "templates"))

engine = WikiEngine()


def _has_gemini_key() -> bool:
    key = os.getenv("GEMINI_API_KEY", "")
    return bool(key and key != "your_gemini_api_key_here")


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield

app = FastAPI(title="03-platform", lifespan=lifespan)
app.include_router(admin_router, prefix="/api/admin")


@app.get("/api/v1/health")
async def health():
    tier = 2 if _has_gemini_key() else 0
    return {"status": "ok", "service": "03-platform", "tier": tier}

# ── In-memory stores ──
_agents: dict[str, dict] = {}
_tasks: dict[str, dict] = {}
_schedules: dict[str, dict] = {}
_skills = ["echo", "news_fetcher", "report_gen"]
_next_id = {"agent": 1, "task": 1, "schedule": 1}


def _gen_id(prefix: str) -> str:
    _id = f"{prefix}-{_next_id[prefix]:03d}"
    _next_id[prefix] += 1
    return _id


# ── Agents CRUD (4 endpoints) ──

@app.get("/api/v1/agents")
async def list_agents():
    return list(_agents.values())


@app.post("/api/v1/agents", status_code=201)
async def create_agent(body: dict):
    aid = _gen_id("agent")
    agent = {"id": aid, **body}
    _agents[aid] = agent
    return agent


@app.get("/api/v1/agents/{agent_id}")
async def get_agent(agent_id: str):
    return _agents.get(agent_id, {"error": "not found"})


@app.patch("/api/v1/agents/{agent_id}")
async def update_agent(agent_id: str, body: dict):
    if agent_id in _agents:
        _agents[agent_id].update(body)
    return _agents.get(agent_id, {"error": "not found"})


@app.delete("/api/v1/agents/{agent_id}")
async def delete_agent(agent_id: str):
    return _agents.pop(agent_id, {"error": "not found"})


# ── Tasks CRUD + assign (5 endpoints) ──

@app.get("/api/v1/tasks")
async def list_tasks():
    return list(_tasks.values())


@app.post("/api/v1/tasks", status_code=201)
async def create_task(body: dict):
    tid = _gen_id("task")
    task = {"id": tid, "status": "todo", **body}
    _tasks[tid] = task
    return task


@app.get("/api/v1/tasks/{task_id}")
async def get_task(task_id: str):
    return _tasks.get(task_id, {"error": "not found"})


@app.patch("/api/v1/tasks/{task_id}")
async def update_task(task_id: str, body: dict):
    if task_id in _tasks:
        _tasks[task_id].update(body)
    return _tasks.get(task_id, {"error": "not found"})


@app.post("/api/v1/tasks/{task_id}/assign")
async def assign_task(task_id: str, body: dict):
    if task_id in _tasks:
        _tasks[task_id]["assignee"] = body.get("agent_id")
        _tasks[task_id]["status"] = "assigned"
    return _tasks.get(task_id, {"error": "not found"})


# ── Skills (2 endpoints) ──

@app.get("/api/v1/skills")
async def list_skills():
    return [{"id": s, "type": "python"} for s in _skills]


@app.post("/api/v1/skills/invoke")
async def invoke_skill(body: dict):
    skill_id = body.get("skill_id", "echo")
    params = body.get("params", {})
    return {"skill_id": skill_id, "result": {"echo": params.get("message", "ok")}}


# ── Schedules (3 endpoints) ──

@app.get("/api/v1/schedules")
async def list_schedules():
    return list(_schedules.values())


@app.post("/api/v1/schedules", status_code=201)
async def create_schedule(body: dict):
    sid = _gen_id("schedule")
    schedule = {"id": sid, **body}
    _schedules[sid] = schedule
    return schedule


@app.delete("/api/v1/schedules/{schedule_id}")
async def delete_schedule(schedule_id: str):
    return _schedules.pop(schedule_id, {"error": "not found"})


# ── Wiki (3 endpoints) ──

class QueryRequest(BaseModel):
    q: str


class IngestRequest(BaseModel):
    filename: str | None = None


@app.post("/api/v1/wiki/query")
async def wiki_query(req: QueryRequest):
    use_rag = _has_gemini_key()
    result = await engine.query(req.q, use_rag=use_rag)
    return result


@app.post("/api/v1/wiki/ingest")
async def wiki_ingest(req: IngestRequest | None = None):
    filename = req.filename if req else None
    ingested = engine.ingest(filename)
    return {"ingested": ingested, "count": len(ingested)}


@app.get("/api/v1/wiki/lint")
async def wiki_lint():
    issues = engine.lint()
    return {"issues": issues, "total": len(issues), "healthy": len(issues) == 0}


# ── Dashboard (board.html) ──

@app.get("/board", response_class=HTMLResponse)
async def board(request: Request):
    return templates.TemplateResponse(request, "board.html")
