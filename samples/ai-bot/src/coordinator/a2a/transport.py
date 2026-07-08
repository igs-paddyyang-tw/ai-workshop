"""Transport 抽象層 — 本地/遠端透明切換。

local: 走 spawn_fn (AgentProcess.send)
http:  走 httpx POST 到遠端 ai-bot 的 /api/v1/a2a/task
"""
from __future__ import annotations

import asyncio
import logging
import os
import socket
from dataclasses import dataclass, field
from typing import Callable, Awaitable

from .protocol import TaskHandoff

log = logging.getLogger("a2a.transport")

# 等待 callback 回報的暫存區
_pending_callbacks: dict[str, asyncio.Future] = {}


@dataclass
class AgentConfig:
    """Agent 連線設定（從 team.yaml 解析）。"""
    name: str
    role: str = "worker"
    working_directory: str = "."
    transport: str = "local"          # local | http
    endpoint: str = ""                # http 時的遠端位址
    auth_token_env: str = ""          # token 環境變數名
    timeout: int = 240                # 逾時秒數
    description: str = ""             # 從 SOUL 或 Agent Card 取得
    skills: list[str] = field(default_factory=list)


def get_local_ip() -> str:
    """取得本機 LAN IP（非 127.0.0.1）。"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"


def get_port() -> int:
    """取得當前 server port。"""
    return int(os.getenv("PORT", "8000"))


def _build_message(task: TaskHandoff) -> str:
    """組裝給本地 Agent 的訊息。"""
    parts = [task.title]
    if task.context:
        parts.append(task.context)
    if task.acceptance_criteria:
        parts.append(f"驗收條件：{task.acceptance_criteria}")
    return "\n\n".join(parts)


async def dispatch(
    agent_cfg: AgentConfig,
    task: TaskHandoff,
    spawn_fn: Callable[[str, str], Awaitable[str | None]],
) -> str | None:
    """統一派工介面 — 根據 transport 選擇 local 或 http。"""
    if agent_cfg.transport == "local":
        return await local_dispatch(agent_cfg, task, spawn_fn)
    elif agent_cfg.transport == "http":
        return await http_dispatch(agent_cfg, task)
    else:
        raise ValueError(f"Unknown transport: {agent_cfg.transport}")


async def local_dispatch(
    agent_cfg: AgentConfig,
    task: TaskHandoff,
    spawn_fn: Callable[[str, str], Awaitable[str | None]],
) -> str | None:
    """本地派工 — 走 spawn_fn (AgentProcess.send)。"""
    message = _build_message(task)
    log.info("Local dispatch %s → %s", task.task_id, agent_cfg.name)
    return await spawn_fn(agent_cfg.name, message)


async def http_dispatch(agent_cfg: AgentConfig, task: TaskHandoff) -> str | None:
    """HTTP 派工 — POST 到遠端 ai-bot，等待 callback 回報。"""
    import httpx

    token = os.getenv(agent_cfg.auth_token_env, "")
    headers = {
        "X-A2A-Token": token,
        "Content-Type": "application/json",
    }

    callback_url = f"http://{get_local_ip()}:{get_port()}/api/v1/a2a/callback"
    payload = {
        "task_id": task.task_id,
        "goal": task.title,
        "context": task.context,
        "callback_url": callback_url,
        "priority": task.priority,
        "timeout_seconds": agent_cfg.timeout,
        "metadata": {
            "requester": task.from_agent,
            "acceptance_criteria": task.acceptance_criteria,
        },
    }

    log.info("HTTP dispatch %s → %s (%s)", task.task_id, agent_cfg.name, agent_cfg.endpoint)

    try:
        async with httpx.AsyncClient(timeout=agent_cfg.timeout) as client:
            resp = await client.post(
                f"{agent_cfg.endpoint}/api/v1/a2a/task",
                json=payload,
                headers=headers,
            )
            resp.raise_for_status()
            data = resp.json()

        if data.get("status") == "accepted":
            # 等待 callback
            result = await wait_for_result(task.task_id, timeout=agent_cfg.timeout)
            return result
        elif data.get("status") == "done":
            # 同步完成（短任務）
            return data.get("result")
        else:
            log.warning("Unexpected response status: %s", data.get("status"))
            return None

    except httpx.TimeoutException:
        log.error("HTTP dispatch %s timed out (%ds)", task.task_id, agent_cfg.timeout)
        return None
    except httpx.HTTPStatusError as e:
        log.error("HTTP dispatch %s failed: %s", task.task_id, e.response.status_code)
        return None
    except Exception as e:
        log.error("HTTP dispatch %s error: %s", task.task_id, e)
        return None


async def wait_for_result(task_id: str, timeout: int = 240) -> str | None:
    """等待 callback 回報結果。"""
    loop = asyncio.get_event_loop()
    future: asyncio.Future = loop.create_future()
    _pending_callbacks[task_id] = future

    try:
        result = await asyncio.wait_for(future, timeout=timeout)
        return result
    except asyncio.TimeoutError:
        log.error("Callback timeout for task %s (%ds)", task_id, timeout)
        return None
    finally:
        _pending_callbacks.pop(task_id, None)


def resolve_callback(task_id: str, result: str) -> bool:
    """收到 callback 後，resolve 對應的 future。"""
    future = _pending_callbacks.get(task_id)
    if future and not future.done():
        future.set_result(result)
        return True
    return False


async def fetch_agent_card(endpoint: str, token: str = "", timeout: int = 10) -> dict | None:
    """從遠端 ai-bot 取得 Agent Card。"""
    import httpx

    headers = {}
    if token:
        headers["X-A2A-Token"] = token

    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            resp = await client.get(f"{endpoint}/api/v1/a2a/card", headers=headers)
            resp.raise_for_status()
            return resp.json()
    except Exception as e:
        log.warning("Failed to fetch agent card from %s: %s", endpoint, e)
        return None
