"""A2A Server — HTTP endpoints for cross-machine task dispatch.

Routes:
  POST /api/v1/a2a/task          接收派工
  POST /api/v1/a2a/callback      接收遠端回報結果
  GET  /api/v1/a2a/card          回傳 Agent Card（能力宣告）
  PATCH /api/v1/a2a/task/{id}    心跳/進度更新
"""
from __future__ import annotations

import logging
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from fastapi import APIRouter, Depends, Header, HTTPException, Request
from pydantic import BaseModel, Field

from .transport import resolve_callback

log = logging.getLogger("a2a.server")

router = APIRouter(prefix="/api/v1/a2a", tags=["A2A"])


# ─── Token Auth Dependency ───────────────────────────

def _get_a2a_token() -> str:
    """從環境變數取得 A2A 認證 token。"""
    return os.getenv("A2A_SECRET", "")


async def verify_token(x_a2a_token: str = Header(default="")) -> str:
    """FastAPI dependency — 驗證 X-A2A-Token header。

    如果 A2A_SECRET 未設定，跳過驗證（開發模式）。
    """
    secret = _get_a2a_token()
    if not secret:
        # 未設定 token = 開發模式，不驗證
        return "dev"
    if x_a2a_token != secret:
        raise HTTPException(status_code=401, detail="Invalid A2A token")
    return x_a2a_token


# ─── Request/Response Models ─────────────────────────

class TaskRequest(BaseModel):
    task_id: str
    goal: str
    context: str = ""
    callback_url: str = ""
    priority: int = 3
    timeout_seconds: int = 240
    metadata: dict[str, Any] = Field(default_factory=dict)


class TaskResponse(BaseModel):
    task_id: str
    status: str  # accepted | rejected | done
    agent_id: str = ""
    message: str = ""


class CallbackRequest(BaseModel):
    task_id: str
    status: str  # done | failed
    result: str = ""
    token_usage: dict[str, int] = Field(default_factory=dict)
    duration_seconds: float = 0


class HeartbeatRequest(BaseModel):
    status: str = "running"  # running | done | failed
    progress: str = ""
    step: int = 0
    total_steps: int = 0


class AgentCard(BaseModel):
    name: str
    description: str = ""
    skills: list[str] = Field(default_factory=list)
    status: str = "idle"
    version: str = "1.0.0"


# ─── State (injected by start.py) ────────────────────

_state: dict[str, Any] = {
    "spawn_fn": None,      # async (agent_name, msg) -> output
    "agent_card": None,    # AgentCard dict
    "active_tasks": {},    # task_id -> {status, started_at, heartbeat_at}
}


def configure(spawn_fn=None, agent_card: dict | None = None) -> None:
    """由 start.py 呼叫，注入 spawn_fn 和 agent_card。"""
    if spawn_fn:
        _state["spawn_fn"] = spawn_fn
    if agent_card:
        _state["agent_card"] = agent_card


# ─── Endpoints ───────────────────────────────────────

@router.post("/task", response_model=TaskResponse)
async def receive_task(req: TaskRequest, _token: str = Depends(verify_token)):
    """接收派工 — 遠端 coordinator POST 過來的任務。"""
    spawn_fn = _state.get("spawn_fn")
    if not spawn_fn:
        return TaskResponse(task_id=req.task_id, status="rejected", message="No spawn_fn configured")

    # 冪等：已存在的 task 回傳現狀
    if req.task_id in _state["active_tasks"]:
        existing = _state["active_tasks"][req.task_id]
        return TaskResponse(task_id=req.task_id, status=existing["status"], agent_id=existing.get("agent_id", ""))

    # 記錄任務
    now = datetime.now(timezone.utc).isoformat()
    _state["active_tasks"][req.task_id] = {
        "status": "running",
        "started_at": now,
        "heartbeat_at": now,
        "callback_url": req.callback_url,
        "agent_id": "",
    }

    # 非同步執行任務
    import asyncio
    asyncio.create_task(_execute_and_callback(req, spawn_fn))

    return TaskResponse(task_id=req.task_id, status="accepted")


async def _execute_and_callback(req: TaskRequest, spawn_fn) -> None:
    """執行任務完成後 POST 回 callback_url。"""
    import httpx

    message = req.goal
    if req.context:
        message += f"\n\n{req.context}"

    try:
        # 使用本地 spawn_fn 執行
        output = await spawn_fn("auto", message)
        status = "done" if output else "failed"
        result = output or "spawn returned None"
    except Exception as e:
        status = "failed"
        result = str(e)
        log.error("Task %s execution failed: %s", req.task_id, e)

    # 更新本地狀態
    if req.task_id in _state["active_tasks"]:
        _state["active_tasks"][req.task_id]["status"] = status

    # 寫入本地 knowledge/shared/tasks/（Executor 側雙寫）
    _write_local_task(req.task_id, req.goal, status, result)

    # POST 回 callback_url
    if req.callback_url:
        try:
            payload = {
                "task_id": req.task_id,
                "status": status,
                "result": result[:2000] if result else "",
                "token_usage": {},
                "duration_seconds": 0,
            }
            async with httpx.AsyncClient(timeout=30) as client:
                resp = await client.post(req.callback_url, json=payload)
                log.info("Callback sent for %s: %s (%d)", req.task_id, status, resp.status_code)
        except Exception as e:
            log.error("Callback failed for %s: %s", req.task_id, e)

    # 清理
    _state["active_tasks"].pop(req.task_id, None)


@router.post("/callback")
async def receive_callback(req: CallbackRequest, _token: str = Depends(verify_token)):
    """接收遠端回報結果 — resolve pending future。"""
    resolved = resolve_callback(req.task_id, req.result)
    if resolved:
        log.info("Callback resolved for %s: %s", req.task_id, req.status)
        return {"status": "ok", "task_id": req.task_id}
    else:
        log.warning("No pending future for task %s", req.task_id)
        return {"status": "no_pending", "task_id": req.task_id}


@router.get("/card", response_model=AgentCard)
async def get_agent_card():
    """回傳 Agent Card — 能力宣告（discovery 用）。"""
    card = _state.get("agent_card")
    if card:
        return AgentCard(**card)

    # Fallback：從 SOUL.md 動態產生
    soul_path = Path(".kiro/steering/SOUL.md")
    description = ""
    if soul_path.exists():
        lines = soul_path.read_text(encoding="utf-8").splitlines()
        for line in lines:
            if line.strip() and not line.startswith("---") and not line.startswith("#"):
                description = line.strip()[:200]
                break

    return AgentCard(
        name=os.getenv("AGENT_NAME", "ai-bot"),
        description=description,
        skills=[],
        status="idle",
    )


@router.patch("/task/{task_id}")
async def heartbeat(task_id: str, req: HeartbeatRequest, _token: str = Depends(verify_token)):
    """心跳/進度更新 — 遠端 Agent 定期回報。"""
    if task_id not in _state["active_tasks"]:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")

    now = datetime.now(timezone.utc).isoformat()
    _state["active_tasks"][task_id]["heartbeat_at"] = now
    _state["active_tasks"][task_id]["status"] = req.status

    log.debug("Heartbeat for %s: %s (step %d/%d)", task_id, req.status, req.step, req.total_steps)
    return {"status": "ok", "task_id": task_id}


# ─── Helper ──────────────────────────────────────────

def _write_local_task(task_id: str, goal: str, status: str, result: str) -> None:
    """Executor 側寫入本地 knowledge/shared/tasks/（雙寫）。"""
    tasks_dir = Path("knowledge/shared/tasks")
    tasks_dir.mkdir(parents=True, exist_ok=True)

    path = tasks_dir / f"{task_id}.md"
    now = datetime.now(timezone.utc).isoformat()
    content = f"""---
task_id: {task_id}
status: {status}
executed_at: {now}
---
# {goal}

## Output
{result[:1000]}
"""
    path.write_text(content, encoding="utf-8")
