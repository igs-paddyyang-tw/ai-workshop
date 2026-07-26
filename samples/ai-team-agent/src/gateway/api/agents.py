"""Agent 管理 API。"""
from __future__ import annotations

import uuid
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from coordinator.db.models import get_async_db, insert, fetch_all, fetch_one, now_iso
from coordinator.events.types import EventType, Event

router = APIRouter()


class AgentCreate(BaseModel):
    name: str
    role: str = "worker"
    provider: str = "kiro-cli"
    working_dir: str = "."
    model: str = "auto"


class AgentUpdate(BaseModel):
    status: str | None = None
    model: str | None = None


class AgentResponse(BaseModel):
    """Agent 完整回應格式（含運行時資訊）。"""
    id: str
    name: str
    role: str
    provider: str
    working_dir: str
    model: str
    status: str
    # 運行時欄位（由 daemon 注入，無 daemon 時為預設值）
    mode: str = "spawn"              # persistent | spawn
    uptime_seconds: float = 0.0
    memory_mb: float = 0.0
    tasks_completed: int = 0
    created_at: str
    updated_at: str


class AgentHealthResponse(BaseModel):
    """單一 Agent 健康詳情。"""
    agent_id: str
    status: str
    mode: str
    pid: int | None = None
    uptime_seconds: float = 0.0
    memory_mb: float = 0.0
    consecutive_failures: int = 0
    last_heartbeat: str | None = None

@router.get("/sessions")
async def agent_sessions_list():
    conn = await get_async_db()
    try:
        return await fetch_all(conn, "SELECT * FROM agent_sessions ORDER BY started_at DESC LIMIT 50")
    finally:
        await conn.close()


@router.get("")
async def list_agents(request: Request):
    conn = await get_async_db()
    try:
        rows = await fetch_all(conn, "SELECT * FROM agents ORDER BY created_at")
        daemon = getattr(request.app.state, "persistent_daemon", None)
        if daemon:
            status_map = {s["name"]: s for s in daemon.get_status()}
            enriched = []
            for r in rows:
                s = status_map.get(r["id"], {})
                enriched.append({
                    **r,
                    "mode": "persistent" if s.get("status") in ("running", "idle") else "spawn",
                    "uptime_seconds": s.get("uptime_seconds", 0.0),
                    "memory_mb": s.get("memory_mb", 0.0),
                    "tasks_completed": s.get("tasks_total", 0),
                })
            return enriched
        return rows
    finally:
        await conn.close()


@router.get("/{agent_id}/health")
async def get_agent_health(agent_id: str, request: Request) -> AgentHealthResponse:
    """取得單一 Agent 健康詳情（pid / uptime / memory / failures）。"""
    conn = await get_async_db()
    try:
        agent = await fetch_one(conn, "SELECT * FROM agents WHERE id=?", (agent_id,))
        if not agent:
            raise HTTPException(404, "Agent not found")
    finally:
        await conn.close()

    daemon = getattr(request.app.state, "persistent_daemon", None)
    if daemon:
        status_list = daemon.get_status()
        s = next((x for x in status_list if x["name"] == agent_id), {})
        return AgentHealthResponse(
            agent_id=agent_id,
            status=s.get("status", agent["status"]),
            mode="persistent",
            pid=s.get("pid"),
            uptime_seconds=s.get("uptime_seconds", 0.0),
            memory_mb=s.get("memory_mb", 0.0),
            consecutive_failures=s.get("consecutive_failures", 0),
            last_heartbeat=s.get("last_heartbeat"),
        )
    return AgentHealthResponse(
        agent_id=agent_id,
        status=agent["status"],
        mode="spawn",
    )

@router.post("", status_code=201)
async def create_agent(body: AgentCreate, request: Request):
    conn = await get_async_db()
    try:
        agent_id = str(uuid.uuid4())[:8]
        now = now_iso()
        data = {"id": agent_id, "name": body.name, "role": body.role, "provider": body.provider,
                "working_dir": body.working_dir, "model": body.model, "status": "idle",
                "created_at": now, "updated_at": now}
        await insert(conn, "agents", data)
        bus = request.app.state.bus
        await bus.emit(Event(type=EventType.AGENT_STARTED, data=data, source="api"))
        return data
    finally:
        await conn.close()

@router.get("/{agent_id}")
async def get_agent(agent_id: str):
    conn = await get_async_db()
    try:
        agent = await fetch_one(conn, "SELECT * FROM agents WHERE id=?", (agent_id,))
        if not agent:
            raise HTTPException(404, "Agent not found")
        return agent
    finally:
        await conn.close()

@router.patch("/{agent_id}")
async def update_agent(agent_id: str, body: AgentUpdate):
    conn = await get_async_db()
    try:
        updates = {k: v for k, v in body.model_dump().items() if v is not None}
        if not updates:
            raise HTTPException(400, "No fields to update")
        updates["updated_at"] = now_iso()
        set_clause = ", ".join(f"{k}=?" for k in updates)
        await conn.execute(f"UPDATE agents SET {set_clause} WHERE id=?", [*updates.values(), agent_id])
        await conn.commit()
        return await fetch_one(conn, "SELECT * FROM agents WHERE id=?", (agent_id,))
    finally:
        await conn.close()

@router.delete("/{agent_id}", status_code=204)
async def delete_agent(agent_id: str, request: Request):
    conn = await get_async_db()
    try:
        await conn.execute("DELETE FROM agents WHERE id=?", (agent_id,))
        await conn.commit()
        bus = request.app.state.bus
        await bus.emit(Event(type=EventType.AGENT_STOPPED, data={"agent_id": agent_id}, source="api"))
    finally:
        await conn.close()


@router.post("/spawn")
async def spawn_agent(body: dict, request: Request):
    """動態啟動一個 agent（觸發 daemon）。"""
    name = body.get("name", "")
    bus = request.app.state.bus
    from coordinator.events.types import Event, EventType
    await bus.emit(Event(type=EventType.AGENT_STARTED, data={"agent_id": name, "action": "spawn"}, source="api"))
    return {"status": "spawning", "agent": name}


@router.get("/runtime/status")
async def runtime_status(request: Request):
    """常駐 Daemon 運行狀態（pid / status / crash_count）。"""
    daemon = getattr(request.app.state, "persistent_daemon", None)
    if daemon:
        return {"mode": "persistent", "instances": daemon.get_status()}
    return {"mode": "spawn", "instances": []}
