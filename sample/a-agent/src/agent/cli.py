"""Agent CLI — 透過 kiro-cli 執行對話。

當 kiro-cli 已安裝時，Agent 的對話會經過完整的 .kiro/ 配置：
  - .kiro/steering/SOUL.md → 人格注入
  - .kiro/skills/ → 自動觸發已安裝的 Skills
  - .kiro/settings/mcp.json → MCP 工具可用

這是「真正的 Agent」模式 — LLM 不只是回話，它會思考、調用工具、產出結果。
"""
from __future__ import annotations

import asyncio
import shutil
from pathlib import Path


def is_cli_available() -> bool:
    """檢查 kiro-cli 是否已安裝。"""
    return shutil.which("kiro-cli") is not None


async def agent_cli_chat(
    message: str,
    *,
    working_dir: str | Path = ".",
    timeout: int = 60,
) -> str | None:
    """透過 kiro-cli 執行對話（載入 .kiro/ 配置）。

    Args:
        message: 使用者訊息
        working_dir: Agent 工作目錄（含 .kiro/）
        timeout: 超時秒數

    Returns:
        kiro-cli 的回覆文字，或 None（如果失敗）
    """
    if not is_cli_available():
        return None

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
        # kiro-cli 的輸出可能包含 ANSI escape codes，清理它
        output = _clean_output(output)
        return output if output else None

    except asyncio.TimeoutError:
        proc.kill()
        return None
    except Exception:
        return None


def _clean_output(text: str) -> str:
    """移除 ANSI escape codes 和多餘的空行。"""
    import re
    # 移除 ANSI escape codes
    text = re.sub(r"\x1b\[[0-9;]*m", "", text)
    # 移除前後空白和多餘換行
    lines = [line for line in text.split("\n") if line.strip()]
    return "\n".join(lines)
