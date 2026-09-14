#!/usr/bin/env python3
"""依角色矩陣同步各 agent 的 skill（從上游 ark-agent-skills 複製）。

為什麼需要這支腳本
------------------
skill 是**複本**不是 symlink（symlink 指向 repo 外的絕對路徑，clone 到新機器
必斷鏈）。複本讓專案自我完備，代價是上游更新不會自動同步 → 靠本腳本拉齊。

同時做**角色邊界**：每個 agent 只裝該職責用得到的 skill —— skill 會進 agent 的
context window，裝了用不到的等於稀釋它的注意力。

這是「三層分工」的第三層：
    ① ark-agent-team-builder  架構（team.yaml / start.py）
    ② ark-agent-init          人格（.kiro/steering/SOUL.md）
    ③ 本腳本                   技能（.kiro/skills/ 依角色矩陣）

用法
----
    python3 scripts/sync_skills.py            # 依矩陣同步
    python3 scripts/sync_skills.py --dry-run  # 只印要做什麼
    python3 scripts/sync_skills.py --check    # 只檢查是否一致（不改檔）

> 🔴 team.yaml 的 `kiro_files.skills.policy` 必須是 `skip` ——
> 否則套件 `_deploy_skills` 每次啟動會把 bundled skill 推翻本腳本的角色矩陣。
"""
from __future__ import annotations

import argparse
import re
import shutil
import sys
from pathlib import Path

# 上游 skill 庫（git repo: igs-paddyyang-tw/ark-agent-skills）
UPSTREAM = Path.home() / "kiro-cli" / ".kiro" / "skills"

# ── 全員底座（Loop 完整鏈：需求 → 文件 → 執行 → 驗證 → 知識 → 報告）──
COMMON = [
    "ark-grill-me",                 # 拷問釐清
    "ark-superpowers",              # 產 spec / design / plan
    "ark-spec-executor",            # 照 plan 執行 + AC 驗收
    "ark-code-spec-validator",      # 驗 code ↔ spec
    "ark-prompt-spec-validator",    # 驗提詞 / AI 內文
    "ark-wiki-engine",              # 知識庫四層搜尋
    "ark-md-report",                # 給 AI 看的報告（Content 軌）
    "ark-html-report",              # 給人看的報告（View 軌）
]

# ── 角色矩陣（COMMON 之外的專業技能）──────────────────────────
MATRIX: dict[str, list[str]] = {
    # 👑 維運：環境、健康、成本
    "admin-agent": ["ark-env-doctor", "ark-dashboard-health", "ark-cost-tracker",
                    "ark-docker-deploy"],
    # 🧠 統籌：拆解、派工、追蹤
    "leader-agent": ["ark-project-planning", "ark-planning-with-files"],
    # 🤖 AI 工程：Prompt / RAG / MCP
    "ai-dev-agent": ["ark-mcp-builder", "ark-llm-tools", "ark-skill-creator",
                     "ark-agent-cli"],
    # 💻 全端開發
    "coder-agent": ["ark-code-review", "ark-test-runner", "ark-db-query",
                    "ark-uml-generator"],
    # 🧪 品質保證
    "qa-agent": ["ark-test-runner", "ark-code-review", "ark-security-audit"],
    # 🗺️ 市場研究
    "market-agent": ["ark-web-scraper", "ark-browser-tool", "ark-marketing",
                     "ark-daily-news"],
    # 📊 數據分析
    "data-agent": ["ark-db-query", "ark-kpi-calculator", "ark-etl-pipeline",
                   "ark-chart-generator", "ark-anomaly-detector"],
    # 📝 報告產出
    "report-agent": ["ark-chart-generator", "ark-html-dashboard", "ark-daily-news"],
}

ROOT = Path(__file__).resolve().parent.parent

# 本團隊沒有 working_directory="." 的 manager；全部 agent 都在 agents/ 底下。
MANAGER: str | None = None


def wanted(agent: str) -> set[str]:
    """該 agent 應有的 skill 集合。"""
    return set(COMMON) | set(MATRIX.get(agent, []))


def skills_dir(agent: str) -> Path:
    """agent 的 skill 目錄；manager（若有）的 working_directory 是專案根。"""
    base = ROOT if agent == MANAGER else ROOT / "agents" / agent
    return base / ".kiro" / "skills"


def source_of(name: str) -> Path:
    """skill 來源：一律從上游取（本專案無自建 skill；第二堂產出的放 agent 自己的目錄）。"""
    return UPSTREAM / name


def _deprecated(src: Path) -> bool:
    """上游是否已把此 skill 降級（兩種樣態都擋）。

    ① 完全 stub：沒 SKILL.md，只留標 DEPRECATED 的 README
    ② 半降級：SKILL.md 在，但 frontmatter `status:` 非 active
    """
    skill_md = src / "SKILL.md"
    if not skill_md.is_file():
        readme = src / "README.md"
        return readme.is_file() and "DEPRECATED" in readme.read_text(
            encoding="utf-8", errors="replace")[:200]
    head = skill_md.read_text(encoding="utf-8", errors="replace")[:1500]
    m = re.search(r"^\s*status:\s*(\S+)", head, re.M)
    return bool(m) and m.group(1).strip().strip("\"'") != "active"


def _differs(a: Path, b: Path) -> bool:
    """比對兩個 skill 目錄的檔案內容（忽略 __pycache__）。"""
    def snap(root: Path) -> dict[str, bytes]:
        out: dict[str, bytes] = {}
        for f in root.rglob("*"):
            if f.is_file() and "__pycache__" not in f.parts:
                out[str(f.relative_to(root))] = f.read_bytes()
        return out
    return snap(a) != snap(b)


def main() -> int:
    """CLI 入口。回傳 exit code（有問題或 --check 不一致 → 1）。"""
    ap = argparse.ArgumentParser(description="依角色矩陣同步各 agent 的 skill")
    ap.add_argument("--dry-run", action="store_true", help="只印要做什麼")
    ap.add_argument("--check", action="store_true", help="只檢查一致性，不改檔")
    args = ap.parse_args()

    if not UPSTREAM.is_dir():
        print(f"🔴 上游 skill 庫不存在：{UPSTREAM}")
        print("   git clone https://github.com/igs-paddyyang-tw/ark-agent-skills.git "
              f"{UPSTREAM}")
        return 1

    added = removed = updated = 0
    problems: list[str] = []

    for agent in MATRIX:
        d = skills_dir(agent)
        want = wanted(agent)
        have = {p.name for p in d.iterdir() if p.is_dir()} if d.is_dir() else set()

        # 來源缺漏／降級先擋下，不靜默略過
        for name in sorted(want):
            src = source_of(name)
            if not src.is_dir():
                problems.append(f"{agent}: 來源不存在 {src}")
            elif _deprecated(src):
                problems.append(f"{agent}: {name} 已被上游標為 DEPRECATED → 改用替代 skill")

        for name in sorted(want - have):
            src = source_of(name)
            if not src.is_dir():
                continue
            print(f"  ➕ {agent:18} {name}")
            added += 1
            if not (args.dry_run or args.check):
                d.mkdir(parents=True, exist_ok=True)
                shutil.copytree(src, d / name)

        for name in sorted(have - want):
            print(f"  ➖ {agent:18} {name}")
            removed += 1
            if not (args.dry_run or args.check):
                shutil.rmtree(d / name)

        for name in sorted(want & have):
            src = source_of(name)
            if not src.is_dir():
                continue
            if _differs(src, d / name):
                print(f"  🔄 {agent:18} {name}（與來源不同 → 更新）")
                updated += 1
                if not (args.dry_run or args.check):
                    shutil.rmtree(d / name)
                    shutil.copytree(src, d / name)

    for p in problems:
        print(f"  🔴 {p}")

    total = added + removed + updated
    mode = "檢查" if args.check else ("預覽" if args.dry_run else "同步")
    print(f"\n{mode}結果：新增 {added}｜移除 {removed}｜更新 {updated}")
    if problems:
        return 1
    if args.check and total:
        print("⚠️ 與矩陣不一致 → 執行 python3 scripts/sync_skills.py")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
