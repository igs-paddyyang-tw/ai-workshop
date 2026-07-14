"""Agent CLI — 8 Agent 常駐服務（使用 AgentProcess）。

啟動時建立 8 個 AgentProcess，對話時透過 send() 排隊執行。
架構與 ai-team-agent 完全一致。
"""
from __future__ import annotations

import asyncio
import logging
import shutil
from pathlib import Path

from src.agent.process import AgentProcess

log = logging.getLogger("agent-cli")

# ── 可用 Agent 清單 ──
AVAILABLE_AGENTS = {
    "default": {
        "dir": ".",
        "name": "Ark Agent",
        "emoji": "🚀",
        "desc": "通用 AI 助手（Gemini）",
    },
    "admin": {
        "dir": "agents/admin-agent",
        "name": "Admin Agent",
        "emoji": "👑",
        "desc": "管家 + 智能分流（預設）",
    },
    "pm": {
        "dir": "agents/pm-agent",
        "name": "PM Agent",
        "emoji": "📋",
        "desc": "專案經理 + 派工",
    },
    "ai-dev": {
        "dir": "agents/ai-dev-agent",
        "name": "AI Dev Agent",
        "emoji": "🧠",
        "desc": "AI 工程師 + Prompt 設計",
    },
    "coder": {
        "dir": "agents/coder-agent",
        "name": "Coder Agent",
        "emoji": "💻",
        "desc": "全端開發 + 程式碼實作",
    },
    "qa": {
        "dir": "agents/qa-agent",
        "name": "QA Agent",
        "emoji": "🧪",
        "desc": "品質保證 + 測試",
    },
    "data": {
        "dir": "agents/data-agent",
        "name": "Data Agent",
        "emoji": "📊",
        "desc": "數據分析（內部）",
    },
    "market": {
        "dir": "agents/market-agent",
        "name": "Market Agent",
        "emoji": "🗺️",
        "desc": "市場研究（外部）",
    },
    "report": {
        "dir": "agents/report-agent",
        "name": "Report Agent",
        "emoji": "📝",
        "desc": "報告產出（彙整）",
    },
}

# ── Agent 服務管理 ──

_agents: dict[str, AgentProcess] = {}
_started: bool = False


def is_cli_available() -> bool:
    """檢查指定的 CLI backend 是否已安裝。"""
    backend = get_available_backend()
    cmd = _resolve_cmd(backend)
    return cmd is not None


def get_available_backend() -> str:
    """從 CLI_BACKEND 環境變數取得 backend，未設定則自動偵測。"""
    import os
    env_val = os.getenv("CLI_BACKEND", "").strip().lower()
    if env_val in ("kiro", "agy", "claude"):
        return env_val
    # 自動偵測
    if _resolve_cmd("kiro"):
        return "kiro"
    if _resolve_cmd("agy"):
        return "agy"
    if _resolve_cmd("claude"):
        return "claude"
    return "kiro"


def _resolve_cmd(backend: str) -> str | None:
    """解析 backend 對應的可執行檔完整路徑，找不到回傳 None。"""
    import os
    cmd_map = {"kiro": "kiro-cli", "agy": "agy", "claude": "claude"}
    cmd = cmd_map.get(backend, backend)
    # 先查 PATH
    found = shutil.which(cmd)
    if found:
        return found
    return None


async def start_all_agents() -> int:
    """啟動 8 個 Agent 常駐服務。回傳成功數量。"""
    global _started
    if _started:
        return len(_agents)
    if not is_cli_available():
        log.info("未偵測到任何 CLI backend（kiro-cli / agy / claude），跳過 Agent 服務啟動")
        return 0

    backend = get_available_backend()
    log.info("使用 CLI backend: %s", backend)

    count = 0
    for agent_id, info in AVAILABLE_AGENTS.items():
        name = f"{agent_id}-agent"
        working_dir = info["dir"]
        proc = AgentProcess(
            name=name,
            working_dir=working_dir,
            model="auto",
            skip_resume=True,
            backend=backend,
        )
        proc.timeout = 180
        await proc.start()
        _agents[agent_id] = proc
        count += 1

    _started = True
    log.info("All %d agents started", count)
    return count


async def stop_all_agents() -> None:
    """停止所有 Agent。"""
    global _started
    for proc in _agents.values():
        await proc.kill()
    _agents.clear()
    _started = False


async def agent_cli_chat(
    message: str,
    *,
    agent_id: str = "admin",
    timeout: int = 120,
) -> str | None:
    """透過 AgentProcess 執行對話。

    如果服務已啟動 → 用 send()（排隊執行）
    如果服務沒啟動 → fallback 到直接 subprocess
    """
    # 優先用常駐服務
    proc = _agents.get(agent_id)
    if proc and proc.is_alive():
        result = await proc.send(message)
        return result if result else None

    # Fallback: 直接 subprocess（相容舊行為）
    if not is_cli_available():
        return None

    info = AVAILABLE_AGENTS.get(agent_id, AVAILABLE_AGENTS["admin"])
    working_dir = Path(info["dir"])
    if not (working_dir / ".kiro" / "steering" / "SOUL.md").exists():
        working_dir = Path(".")

    try:
        import re
        backend = get_available_backend()
        # 根據 backend 組裝 fallback 指令
        if backend == "agy":
            cmd = ["agy", "-p", message, "--dangerously-skip-permissions", "--add-dir", str(working_dir.resolve())]
        elif backend == "claude":
            cmd = ["claude", "-p", message]
        else:
            cmd = ["kiro-cli", "chat", "--no-interactive", "--trust-all-tools", message]

        proc_sub = await asyncio.create_subprocess_exec(
            *cmd,
            cwd=str(working_dir),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await asyncio.wait_for(
            proc_sub.communicate(), timeout=timeout
        )
        if proc_sub.returncode != 0:
            return None
        output = stdout.decode("utf-8").strip()
        output = re.sub(r"\x1b\[[0-9;]*m", "", output)
        lines = [line for line in output.split("\n") if line.strip()]
        return "\n".join(lines) if lines else None
    except asyncio.TimeoutError:
        return None
    except Exception:
        return None
