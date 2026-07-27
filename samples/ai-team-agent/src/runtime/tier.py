"""Tier 分級啟動偵測。"""
from __future__ import annotations

import os
import shutil
from dataclasses import dataclass
from pathlib import Path


@dataclass
class TierStatus:
    """各 Tier 啟用狀態。"""
    tier: int = 0
    skills_ok: bool = True    # Tier 0: 永遠可用
    wiki_ok: bool = True      # Tier 0: 永遠可用
    api_ok: bool = True       # Tier 0: 永遠可用
    tg_ok: bool = False       # Tier 1: 需 TG token
    llm_ok: bool = False      # Tier 2: 需 Gemini/OpenAI API key
    cli_ok: bool = False      # Tier 3: 需 kiro-cli
    team_ok: bool = False     # Tier 4: 需 team.yaml


def detect_tier() -> TierStatus:
    """偵測環境，回傳當前可達 Tier。"""
    status = TierStatus()

    # Tier 1: Telegram Bot Token
    tg_token = os.environ.get("TELEGRAM_BOT_TOKEN", "")
    if tg_token and len(tg_token) > 10:
        status.tg_ok = True
        status.tier = 1

    # Tier 2: LLM API key（Gemini 或 OpenAI）
    gemini_key = os.environ.get("GEMINI_API_KEY", "")
    openai_key = os.environ.get("OPENAI_API_KEY", "")
    if gemini_key or openai_key:
        status.llm_ok = True
        if status.tier >= 1:
            status.tier = 2

    # Tier 3: kiro-cli 在 PATH
    if shutil.which("kiro-cli"):
        status.cli_ok = True
        if status.tier >= 2:
            status.tier = 3

    # Tier 4: team.yaml 存在
    if Path("team.yaml").exists():
        status.team_ok = True
        if status.tier >= 3:
            status.tier = 4

    return status


def print_tier_banner(status: TierStatus) -> None:
    """印出 Tier 狀態 banner（ASCII 安全，避免 cp950 crash）。"""
    import sys
    out = sys.stdout

    def _p(text: str) -> None:
        out.write(text.encode("ascii", errors="replace").decode("ascii") + "\n")
        out.flush()

    check = "[OK]"
    empty = "[  ]"

    _p("=" * 50)
    _p("  Ark Agent Team Platform")
    _p("=" * 50)
    _p(f"  Tier 0: {check} Prompts + Skills + Wiki + MCP")
    _p(f"  Tier 1: {check if status.tg_ok else empty} Telegram Bot")
    _p(f"  Tier 2: {check if status.llm_ok else empty} LLM API (Gemini/OpenAI)")
    _p(f"  Tier 3: {check if status.cli_ok else empty} kiro-cli Agent")
    _p(f"  Tier 4: {check if status.team_ok else empty} Team A2A")
    _p("=" * 50)
    _p(f"\n  Current Tier: {status.tier}")
