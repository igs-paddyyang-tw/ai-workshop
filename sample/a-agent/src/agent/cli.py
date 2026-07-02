"""Agent CLI — 透過 kiro-cli 執行對話（支援多 Agent 切換）。

對話路由：
  預設 → admin-agent（通用助手）
  /agent news → news-agent（科技新聞）
  /agent code → code-agent（程式碼）
  /agent wiki → wiki-agent（知識庫）
  /agent admin → admin-agent（切回預設）

kiro-cli 啟動時從 working_dir 讀取 .kiro/ 配置，
不同 agent 有不同的 SOUL.md → 回覆風格和能力完全不同。
"""
from __future__ import annotations

import asyncio
import re
import shutil
from pathlib import Path

# ── 可用 Agent 清單 ──
AVAILABLE_AGENTS = {
    "admin": {
        "dir": "agents/admin-agent",
        "name": "Admin Agent",
        "emoji": "🤖",
        "desc": "通用 AI 助手（預設）",
    },
    "news": {
        "dir": "agents/news-agent",
        "name": "News Agent",
        "emoji": "📰",
        "desc": "科技新聞專家",
    },
    "code": {
        "dir": "agents/code-agent",
        "name": "Code Agent",
        "emoji": "💻",
        "desc": "程式碼助手",
    },
    "wiki": {
        "dir": "agents/wiki-agent",
        "name": "Wiki Agent",
        "emoji": "📚",
        "desc": "知識庫問答",
    },
}

# 當前使用的 Agent（module-level state）
_current_agent: str = "admin"


def get_current_agent() -> str:
    """取得當前 Agent ID。"""
    return _current_agent


def set_current_agent(agent_id: str) -> bool:
    """切換 Agent。回傳是否成功。"""
    global _current_agent
    if agent_id in AVAILABLE_AGENTS:
        _current_agent = agent_id
        return True
    return False


def get_agent_working_dir() -> Path:
    """取得當前 Agent 的工作目錄。"""
    info = AVAILABLE_AGENTS.get(_current_agent, AVAILABLE_AGENTS["admin"])
    return Path(info["dir"])


def list_agents() -> list[dict]:
    """列出所有可用 Agent。"""
    return [
        {"id": k, "current": k == _current_agent, **v}
        for k, v in AVAILABLE_AGENTS.items()
    ]


def is_cli_available() -> bool:
    """檢查 kiro-cli 是否已安裝。"""
    return shutil.which("kiro-cli") is not None


async def agent_cli_chat(
    message: str,
    *,
    agent_id: str | None = None,
    timeout: int = 60,
) -> str | None:
    """透過 kiro-cli 執行對話。

    Args:
        message: 使用者訊息
        agent_id: 指定 Agent（None = 使用當前 Agent）
        timeout: 超時秒數
    """
    if not is_cli_available():
        return None

    # 決定工作目錄
    aid = agent_id or _current_agent
    info = AVAILABLE_AGENTS.get(aid, AVAILABLE_AGENTS["admin"])
    working_dir = Path(info["dir"])

    # 確認 .kiro/ 存在
    if not (working_dir / ".kiro" / "steering" / "SOUL.md").exists():
        # fallback 到根目錄的 .kiro/
        working_dir = Path(".")

    try:
        proc = await asyncio.create_subprocess_exec(
            "kiro-cli", "chat",
            "--trust-all-tools",
            "--legacy-ui",
            "--message", message,
            cwd=str(working_dir),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await asyncio.wait_for(
            proc.communicate(), timeout=timeout
        )

        if proc.returncode != 0:
            return None

        output = stdout.decode("utf-8").strip()
        output = _clean_output(output)
        return output if output else None

    except asyncio.TimeoutError:
        proc.kill()
        return None
    except Exception:
        return None


def _clean_output(text: str) -> str:
    """移除 ANSI escape codes 和多餘的空行。"""
    text = re.sub(r"\x1b\[[0-9;]*m", "", text)
    lines = [line for line in text.split("\n") if line.strip()]
    return "\n".join(lines)
