from __future__ import annotations
import os
from dataclasses import dataclass, field
from pathlib import Path
import yaml

@dataclass
class InstanceConfig:
    working_directory: str = "."
    description: str = ""
    role: str = "worker"
    model: str = "auto"
    backend: str = "kiro"  # kiro / gemini / claude
    skip_resume: bool = False
    private_chat: int | None = None
    persistent: bool = True  # True = 常駐模式, False = spawn 模式
    auto_start: bool = True
    startup_timeout_ms: int = 60000
    name: str = ""  # 由 load_config 填入


@dataclass
class RestartPolicy:
    max_retries: int = 3
    backoff: str = "exponential"
    health_check_interval_ms: int = 30000


@dataclass
class StartupConfig:
    concurrency: int = 3
    stagger_delay_ms: int = 2000

@dataclass
class TeamConfig:
    name: str = "Agent Team"
    instances: dict[str, InstanceConfig] = field(default_factory=dict)
    health_port: int = 33333
    model: str = "auto"
    channel: dict = field(default_factory=dict)
    access: dict = field(default_factory=dict)
    cost_guard: dict = field(default_factory=dict)
    hang_detector: dict = field(default_factory=dict)
    startup: StartupConfig = field(default_factory=StartupConfig)
    examples: list[str] = field(default_factory=list)
    persistent: bool = True  # 全域預設

    @property
    def timeout_seconds(self) -> int:
        """從 hang_detector.timeout_minutes 計算超時秒數，預設 3600s。"""
        minutes = self.hang_detector.get("timeout_minutes", 60)
        return int(minutes) * 60

def load_config(path: str | Path) -> TeamConfig:
    p = Path(path)
    data = yaml.safe_load(p.read_text(encoding="utf-8"))
    defaults = data.get("defaults", {})
    global_persistent = defaults.get("persistent", True)

    # Startup config
    startup_raw = data.get("startup", {})
    startup = StartupConfig(
        concurrency=startup_raw.get("concurrency", 3),
        stagger_delay_ms=startup_raw.get("stagger_delay_ms", 2000),
    )

    instances = {}
    for name, cfg in data.get("instances", {}).items():
        instances[name] = InstanceConfig(
            working_directory=cfg.get("working_directory", "."),
            description=cfg.get("description", ""),
            role=cfg.get("role", "worker"),
            model=cfg.get("model", defaults.get("model", "auto")),
            backend=cfg.get("backend", defaults.get("backend", "kiro")),
            skip_resume=cfg.get("skip_resume", False),
            private_chat=cfg.get("private_chat"),
            persistent=cfg.get("persistent", global_persistent),
            auto_start=cfg.get("auto_start", True),
            startup_timeout_ms=cfg.get("startup_timeout_ms", 60000),
            name=name,
        )
    return TeamConfig(
        name=data.get("name", "Agent Team"),
        instances=instances,
        health_port=data.get("health_port", 33333),
        model=defaults.get("model", "auto"),
        channel=data.get("channel", {}),
        access=data.get("access", {}),
        cost_guard=data.get("cost_guard", {}),
        hang_detector=data.get("hang_detector", {}),
        startup=startup,
        examples=data.get("examples", []),
        persistent=global_persistent,
    )
