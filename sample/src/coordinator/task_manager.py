"""任務管理器 — 建立、列表、指派任務。"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

import yaml


@dataclass
class Task:
    """單一任務。"""

    id: str
    title: str
    assignee: str = ""
    status: str = "pending"
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())


class TaskManager:
    """簡易任務 CRUD。"""

    def __init__(self) -> None:
        self._tasks: dict[str, Task] = {}
        self._counter: int = 0

    def create_task(self, title: str) -> Task:
        self._counter += 1
        task = Task(id=f"T-{self._counter:03d}", title=title)
        self._tasks[task.id] = task
        return task

    def list_tasks(self) -> list[Task]:
        return list(self._tasks.values())

    def assign(self, task_id: str, agent_id: str) -> Task | None:
        task = self._tasks.get(task_id)
        if task:
            task.assignee = agent_id
            task.status = "assigned"
        return task


def get_team_agents() -> list[dict]:
    """讀取專案根目錄的 team.yaml，回傳 agents 列表。"""
    project_root = Path(__file__).resolve().parent.parent.parent
    team_file = project_root / "team.yaml"
    with open(team_file, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return data.get("agents", [])


# Module-level 單例實例
task_manager = TaskManager()
