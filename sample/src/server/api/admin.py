"""Admin 端點（Dashboard 統計 + 管理）。"""
from __future__ import annotations

from fastapi import APIRouter

router = APIRouter()


@router.get("/dashboard/stats")
async def dashboard_stats():
    return {"agents": 3, "tasks": 12, "completed": 8, "pending": 4}


@router.get("/agents")
async def admin_agents():
    return [
        {"id": "admin", "role": "管理者", "status": "active"},
        {"id": "dev", "role": "開發者", "status": "active"},
        {"id": "qa", "role": "測試者", "status": "idle"},
    ]


@router.get("/tasks")
async def admin_tasks():
    return [
        {"id": "t1", "title": "建立 API", "status": "done", "assignee": "dev"},
        {"id": "t2", "title": "撰寫測試", "status": "in_progress", "assignee": "qa"},
        {"id": "t3", "title": "部署上線", "status": "todo", "assignee": None},
    ]


@router.get("/audit")
async def admin_audit():
    return [
        {"ts": "2026-06-26T10:00:00Z", "action": "task.created", "actor": "admin"},
        {"ts": "2026-06-26T10:05:00Z", "action": "task.assigned", "actor": "admin"},
    ]


@router.get("/config")
async def admin_config():
    return {"version": "0.3.0", "tier": "platform", "max_agents": 10}
