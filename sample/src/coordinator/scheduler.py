"""簡易排程引擎 — 示範 cron 觸發概念。

Workshop 04/05 的排程基礎：
  - 定義 jobs（cron + target + prompt）
  - 展示「排程派工到 Agent」的概念

注意：這是教學用簡化版，真實版本使用 APScheduler。
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

import yaml


@dataclass
class ScheduleJob:
    """排程任務定義。"""

    id: str
    target: str  # agent_id
    prompt: str
    cron: str  # e.g. "0 8 * * *"
    enabled: bool = True
    last_run: str = ""


class Scheduler:
    """簡易排程管理器。

    使用方式:
        scheduler = Scheduler.from_yaml("scheduler.yaml")
        jobs = scheduler.list_jobs()
        scheduler.trigger("daily-news")  # 手動觸發
    """

    def __init__(self, jobs: list[ScheduleJob] | None = None) -> None:
        self._jobs: dict[str, ScheduleJob] = {j.id: j for j in (jobs or [])}

    @classmethod
    def from_yaml(cls, path: str | Path) -> "Scheduler":
        """從 YAML 載入排程配置。"""
        path = Path(path)
        if not path.exists():
            return cls([])
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        jobs = [
            ScheduleJob(
                id=j["id"],
                target=j.get("target", ""),
                prompt=j.get("prompt", ""),
                cron=j.get("cron", ""),
                enabled=j.get("enabled", True),
            )
            for j in data.get("jobs", [])
        ]
        return cls(jobs)

    def list_jobs(self) -> list[dict[str, Any]]:
        """列出所有排程任務。"""
        return [
            {
                "id": j.id,
                "target": j.target,
                "cron": j.cron,
                "enabled": j.enabled,
                "last_run": j.last_run,
            }
            for j in self._jobs.values()
        ]

    def trigger(self, job_id: str) -> dict[str, Any] | None:
        """手動觸發一個排程任務（模擬執行）。"""
        job = self._jobs.get(job_id)
        if not job:
            return None
        job.last_run = datetime.now().isoformat()
        return {
            "job_id": job.id,
            "target": job.target,
            "prompt": job.prompt,
            "triggered_at": job.last_run,
        }

    def toggle(self, job_id: str) -> bool | None:
        """切換啟用/停用。"""
        job = self._jobs.get(job_id)
        if not job:
            return None
        job.enabled = not job.enabled
        return job.enabled


# ── 預設排程配置（內建，不需要 yaml 也能用）──

DEFAULT_JOBS = [
    ScheduleJob(
        id="daily-news",
        target="market",
        prompt="抓取今日科技新聞（HN + TechCrunch），整理 3-5 則精選",
        cron="0 8 * * *",
    ),
    ScheduleJob(
        id="wiki-lint",
        target="qa",
        prompt="執行 Wiki 健康檢查，回報缺失 frontmatter 和斷連結",
        cron="0 22 * * *",
    ),
]

# Module-level 實例
scheduler = Scheduler(DEFAULT_JOBS)
