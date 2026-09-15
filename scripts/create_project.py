#!/usr/bin/env python3
"""一鍵產出可直接跑的 agent 專案（bot 或 team）。

這支腳本存在的理由
------------------
課堂上「裝環境」會吃掉「學東西」的時間。舊流程要七個步驟
（scaffold → 建 venv → 裝 wheel → 驗版號 → 產人格 → 裝 skill → 驗證），
其中六個對學習沒有任何價值 —— 它們只是必要的前置。

本腳本把那七步收成一個指令，**產出當場能 `python start.py` 的專案**。
人要做的只剩兩件事：填 token、改 SOUL（那才是課程內容）。

與上游 scaffolder 的關係
------------------------
`ark-agent-bot-builder` / `ark-agent-team-builder` 是**通用 scaffolder**
（給任何專案用，只產骨架）。本腳本是**教材專用的一鍵入口**：
產出的結構與它們相同，但多做 venv／wheel／preset 人格／驗證。

🔴 為了不讓兩邊漂移：產出後若偵測到上游 validator 存在，**會自動拿它驗**
（`validate_agent.py` / `validate_team.py`）。上游改了規則，這裡就會紅。

用法
----
    python3 scripts/create_project.py bot  my-bot  --wheel ./ark_bot_agent-1.0.16-py3-none-any.whl
    python3 scripts/create_project.py team my-team --wheel ./ark_team_agent-1.8.16-py3-none-any.whl
    python3 scripts/create_project.py bot  my-bot  --preset gamedev --no-venv
    python3 scripts/create_project.py bot  my-bot  --dry-run

preset（`presets/*.yaml`）
    general  通用開發團隊 6 角色（預設）
    gamedev  遊戲開發團隊 8 角色（workshop 貫穿案例）
    minimal  單一 agent，自己從零設計編制
"""
from __future__ import annotations

# 🔴 help 攔截必須在第三方 import 之前 —— help 不該需要依賴。
import argparse
import json
import os
import shutil
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
PRESET_DIR = REPO / "presets"
UPSTREAM_SKILLS = Path.home() / "kiro-cli" / ".kiro" / "skills"

SOUL_TEMPLATE = """# SOUL — {name}（{codename}）

> Agent 的人格定義。**改這個檔案，行為就變** —— 不用改任何程式碼。
> 八段式：身份 / 人格 / 能力 / 邊界 / 工作流程 / 輸出格式 / 成長規則 / 禁制

## 身份

{identity}

## 人格

{traits}

## 能力

{can}

## 邊界

{cannot}

## 工作流程

1. 先確認需求是否清楚 —— 不清楚就問，不要猜
2. 查知識庫（`knowledge/shared/wiki/`）看有沒有既有結論
3. 動手前先說要做什麼；動完回報做了什麼
4. 結果要有依據：測試 rc、log、來源連結

## 輸出格式

{output}

## 成長規則

- 學到的新知識寫進 `knowledge/shared/raw/`，由 ingest 轉成 wiki 頁面
- 踩到的坑寫進記憶（`memory/`），下次先查再動手
- **不要**手寫 `knowledge/shared/wiki/` —— 那層由 ingest 產出

## 禁制

- 🚫 不做超出「邊界」列出的事
- 🚫 不把 token / 金鑰寫進記憶、知識庫或報告
- 🚫 不憑印象回答 —— 查不到就說查不到
"""

AGENTS_MD = """# AGENTS.md — 全域行為準則（多 CLI 共用 SSOT）

> 跨 CLI 的單一真相來源：Kiro CLI 讀 `.kiro/steering/`、Claude Code 讀 `CLAUDE.md`、
> Codex / Cursor 讀 `AGENTS.md`。要共用同一份規範，就讓其他入口**連結**到這裡。

## 這個專案是什麼

`{package}` 套件的**消費端**。框架都在套件裡，本目錄只有**設定與人格**。

## 設定檔分工（不合併）

{config_table}

## 紅線

- 🚫 不要在這個專案手搭 runtime —— 套件已經有了，兩套並存必漂移
- 🚫 不要自創設定欄位 —— **未知欄位會被靜默丟掉**（設定看起來生效了其實沒有）
- 🚫 不要把 token 寫進 `memory/` 或知識庫
- 🚫 知識庫頁面由 ingest 產出，不手寫進 `knowledge/shared/wiki/`

## 產出落點

| 類型 | 路徑 |
|------|------|
| 規格 / 設計 / 計畫 | `docs/specs` · `docs/designs` · `docs/plans` |
| 報告 | `artifacts/reports/` |
| 知識素材 | `knowledge/shared/raw/` → ingest → `knowledge/shared/wiki/` |
| 記憶 | `memory/` |
"""

WIKI_SCHEMA = """# 知識庫 Schema

## tags 白名單
- architecture
- process
- decision
- research
- ops
- troubleshooting

> 🔴 上面的 `- ` 清單必須**緊接**在「## tags 白名單」標題之後。
> 中間插入說明或表格會讓它解析成空集合，而空集合的語意是 **fail-closed**：
> 所有 tag 都不合法 → ingest 全部被擋，而且不會有人發現。

每個 wiki 頁面必須有 frontmatter：

```yaml
---
title: 頁面標題
type: system | entity | process | overview
status: seedling | developing | mature | evergreen
trust: deterministic | llm-distilled
approved: true | false
updated: YYYY-MM-DD
tags: []
---
```

- `raw/` 給人讀（原始素材，只新增不改）
- `wiki/` 給 AI 讀（結構化，由 ingest 產出，**不手寫**）
"""


@dataclass
class Result:
    """一鍵流程的執行結果。"""

    steps: list[tuple[str, bool, str]] = field(default_factory=list)

    def add(self, name: str, ok: bool, detail: str = "") -> None:
        self.steps.append((name, ok, detail))
        mark = "✅" if ok else "❌"
        print(f"  {mark} {name}" + (f" — {detail}" if detail else ""))

    @property
    def ok(self) -> bool:
        return all(ok for _, ok, _ in self.steps)


def load_preset(name: str) -> dict:
    """讀 preset YAML。找不到就列出可用的，不靜默失敗。"""
    import yaml  # 第三方，放在 help 攔截之後

    path = PRESET_DIR / f"{name}.yaml"
    if not path.is_file():
        avail = sorted(p.stem for p in PRESET_DIR.glob("*.yaml"))
        raise SystemExit(f"🔴 找不到 preset「{name}」。可用：{', '.join(avail) or '(無)'}")
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def bullets(items: list[str] | str) -> str:
    """把 preset 的欄位轉成 Markdown 條列。"""
    if isinstance(items, str):
        return items
    return "\n".join(f"- {x}" for x in items)


def write(path: Path, content: str) -> None:
    """寫檔（自動建目錄，UTF-8）。"""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def make_soul(agent: dict) -> str:
    """依 preset 的角色定義產出八段式 SOUL.md。"""
    soul = agent.get("soul", {})
    return SOUL_TEMPLATE.format(
        name=agent.get("name", agent["id"]),
        codename=agent.get("codename", agent["id"]),
        identity=soul.get("identity", "（待填）"),
        traits=bullets(soul.get("traits", ["（待填）"])),
        can=bullets(soul.get("can", ["（待填）"])),
        cannot=bullets(soul.get("cannot", ["（待填）"])),
        output=soul.get("output", "（待填）"),
    )


def scaffold_common(root: Path, preset: dict, package: str, config_table: str) -> None:
    """兩種專案都要的骨架：知識庫、記憶、產出、人格、docs。"""
    # 🔴 三個骨架缺口：knowledge/shared（Wiki 引擎讀這層）、memory、artifacts
    write(root / "knowledge" / "shared" / "schema.md", WIKI_SCHEMA)
    write(root / "knowledge" / "shared" / "index.md", "# Wiki 索引\n\n| 檔案 | 標題 | type | status |\n|---|---|---|---|\n")
    write(root / "knowledge" / "shared" / "log.md", "# 知識庫變更紀錄（append-only）\n")
    write(root / "knowledge" / "shared" / "wiki" / "overview.md",
          "---\ntitle: 知識庫概覽\ntype: overview\nstatus: seedling\n"
          "trust: deterministic\napproved: true\ntags: []\n---\n\n"
          "# 知識庫概覽\n\n這裡放結構化知識。素材放 `../raw/`，用 ingest 轉進來。\n")
    # 🔴 knowledge/raw/memory-archive 是套件的 MEMORY 歸檔落點（路徑寫死不可搬）
    for d in ("knowledge/shared/raw", "knowledge/raw/memory-archive",
              "memory/daily", "artifacts/reports",
              "docs/specs", "docs/designs", "docs/plans", "docs/one-pagers"):
        (root / d).mkdir(parents=True, exist_ok=True)
        (root / d / ".gitkeep").touch()

    write(root / ".kiro" / "steering" / "AGENTS.md",
          AGENTS_MD.format(package=package, config_table=config_table))

    # 每個 agent 的人格 + 工作目錄
    for agent in preset["agents"]:
        base = root if agent["dir"] == "." else root / agent["dir"]
        write(base / ".kiro" / "steering" / "SOUL.md", make_soul(agent))
        for sub in ("knowledge/raw", "knowledge/wiki", "memory/daily", "artifacts"):
            (base / sub).mkdir(parents=True, exist_ok=True)
            (base / sub / ".gitkeep").touch()

    write(root / ".gitignore", "\n".join([
        "# 機密", ".env", "secrets/*", "!secrets/.gitkeep", "",
        "# 執行環境與產物（重啟自動重生，不進版控）",
        ".venv/", "__pycache__/", "*.pyc", "state/", "data/", "logs/", "*.db",
        ".index/", "knowledge/**/.index/", "instances/", "tasks/", "team.pid",
        "memory/daily/*", "!memory/daily/.gitkeep",
        "artifacts/reports/*", "!artifacts/reports/.gitkeep",
        "",
        "# 套件依本機實況產生（含絕對路徑），每次啟動重產",
        "agents/*/AGENTS.md",
        "# skill 是複本，由 scripts/sync_skills.py 重建",
        "agents/*/.kiro/skills/",
        "",
    ]))


def scaffold_bot(root: Path, preset: dict, codename: str) -> None:
    """ark_bot_agent 消費端：agents.yaml + bot.yaml + start.py。"""
    import yaml

    agents: dict[str, dict] = {}
    for a in preset["agents"]:
        entry = {"dir": a["dir"], "name": a.get("name", a["id"]),
                 "codename": a.get("codename", a["id"]), "emoji": a.get("emoji", "🤖"),
                 "desc": a.get("desc", "")}
        if "role" in a and a["id"] != "default":
            entry["role"] = a["role"]
        if "dispatchable" in a:
            entry["dispatchable"] = a["dispatchable"]
        elif a["id"] != "default":
            entry["dispatchable"] = True
        # 🔴 bot 端用 group_members（team 端才是 group）—— 寫反會被靜默忽略
        if "group_members" in a:
            entry["group_members"] = a["group_members"]
        agents[a["id"]] = entry

    header = (
        "# ═══════════════════════════════════════════════════════════════\n"
        "# agents.yaml — Agent 定義（唯一來源，專案根哨兵）\n"
        "#\n"
        "# 🔴 未知欄位會被靜默丟掉 —— 想讓 agent「看到」的約束要寫進 desc 或 SOUL.md。\n"
        "# 🔴 bot 端用 group_members（leader 列成員）；team 端用 group（worker 指 leader）。\n"
        "#    寫反了套件不報錯，只在 log 印一行「欄位不存在」。\n"
        "# ═══════════════════════════════════════════════════════════════\n"
    )
    write(root / "agents.yaml", header + yaml.safe_dump(
        agents, allow_unicode=True, sort_keys=False, default_flow_style=False))

    write(root / "bot.yaml", f"""# bot.yaml —— 只放「怎麼跑」（有誰在 agents.yaml，機密在 .env）
# 整份可刪，全走套件預設。留著是為了顯式可見。
# 檢查解析結果：python -m ark_bot_agent paths
name: "{root.name}"
codename: "{codename}"

server:
  port: 8000
  host: "127.0.0.1"          # 要對外才改 0.0.0.0

modes:
  default: agent             # chat | agent | team
  default_agent: default
  team_leader: leader
  chat:
    max_iterations: 5
    tools: [search_wiki, recall_memory, web_search]

llm:                         # 只有 chat 模式用（agent 走 CLI backend，零 API 費用）
  provider: gemini
  model: gemini-3.5-flash
  temperature: 0.7

backend:
  cli: auto                  # auto | kiro | claude

report:
  enabled: true
  md_dir: artifacts/reports
  render_html: true
  send_to_tg: true

features:
  wiki: true
  memory: true
  scheduler: true
  web_ui: true               # 🔴 有 web_ui 才需要 port；TG 一律 polling
  a2a: false

access:
  admin_chat_ids: []         # 填你自己的 TG chat_id
""")

    write(root / "start.py", '''"""啟動入口 —— 框架在 ark_bot_agent 套件裡。

設定：agents.yaml（有誰）+ bot.yaml（怎麼跑）+ .env（機密）
診斷：python -m ark_bot_agent paths
"""
from ark_bot_agent import run_bot

# 🔴 沒有業務 skill 時就用 run_bot()，不要寫 run_bot(skills=["skills"])
#    —— 指向空目錄會讓啟動橫幅永遠印「注入了 skills 但一個都沒載到」。
run_bot()
''')
    write(root / "requirements.txt",
          "# 🔴 extras 不可省：[search] 缺了四層搜尋靜默降級；[skills] 缺了排程只印一行 WARNING\n"
          "ark_bot_agent[search,skills]   # 由 wheel 安裝，不從 PyPI\n")
    env = ("# 🔴 每個人用自己的 token —— 同一 token 兩處 polling 會隨機吃訊息且不報錯\n"
           "TELEGRAM_BOT_TOKEN=your_token\nGEMINI_API_KEY=your_key\n")
    write(root / ".env.example", env)
    write(root / ".env", env)      # 直接可跑；.env 已被 .gitignore 排除
    (root / "skills").mkdir(exist_ok=True)
    (root / "skills" / ".gitkeep").touch()


def scaffold_team(root: Path, preset: dict, health_port: int) -> None:
    """ark_team_agent 消費端：team.yaml + scheduler.yaml + start.py。"""
    import yaml

    instances: dict[str, dict] = {}
    leader_id = next((a["id"] for a in preset["agents"] if a.get("role") == "leader"), None)
    for a in preset["agents"]:
        if a["dir"] == ".":
            continue  # team 端沒有 chat 引擎；manager 若要走根目錄請自行加
        name = f"{a['id']}-agent" if not a["id"].endswith("-agent") else a["id"]
        entry = {"working_directory": a["dir"],
                 "description": f"{a.get('emoji','')} {a.get('name', a['id'])} — {a.get('desc','')}".strip(),
                 "role": a.get("role", "worker"), "skip_resume": True}
        # 🔴 team 端：worker 用 group 指向所屬 leader（不是 group_members）
        if a.get("role") == "worker" and leader_id:
            entry["group"] = f"{leader_id}-agent"
            entry["persistent"] = False       # lazy spawn，省資源
        instances[name] = entry

    write(root / "team.yaml", f"""# ═══════════════════════════════════════════════════════════════
# team.yaml —— 團隊設定（唯一集中點）。**這份檔案就是架構。**
# 六個區塊：instances · group · access · cost_guard · hang_detector · kiro_files
# ═══════════════════════════════════════════════════════════════

defaults:
  backend: kiro-cli
  model: auto
  persistent: true

knowledge_search_order: [shared]

# 🔴 policy: skip 不是選配 —— 不設的話套件每次啟動會把內建 skill 鋪回去，
#    推翻 scripts/sync_skills.py 定的角色矩陣。
kiro_files:
  skills:
    policy: skip
  steering:
    team_md: always          # 成員表以 team.yaml 為唯一真相，每次啟動重產
    soul_md: once            # 手寫人格不覆蓋

channel:
  bot_token_env: TELEGRAM_BOT_TOKEN

access:
  mode: locked               # locked | group | open
  allowed_users: []          # 🔴 沒填誰都指揮不動（包括你自己）

cost_guard:
  daily_limit_usd: 15.0
  warn_at_percentage: 80
  timezone: Asia/Taipei

hang_detector:
  enabled: true
  timeout_minutes: 60
  escalation_minutes: 180

startup:
  concurrency: 2
  stagger_delay_ms: 3000

instances:
""" + "\n".join(
        "  " + line for line in yaml.safe_dump(
            instances, allow_unicode=True, sort_keys=False).splitlines()
    ) + f"""

# API / health 端點（健康檢查是 /api/health，不是 /health）
# 💡 看板會自動起在 health_port + 5000 → {health_port + 5000}
health_port: {health_port}
""")

    write(root / "scheduler.yaml", """timezone: Asia/Taipei

jobs:
  # 每日摘要 → 管理者私訊
  - id: daily-summary
    target: leader-agent
    prompt: |
      📋 今日摘要。
      規則：有成果 → emoji + 完成項目 + 明日計劃；無成果 → 一句友善話。
      ≤ 100 字，不要輸出 raw 資料。
    cron: "0 21 * * *"
    reply_to: private

  # 知識庫 ingest（讓「產出 → 知識」的迴圈自動化）
  - id: wiki-ingest
    target: admin-agent
    prompt: |
      把 knowledge/shared/raw/ 今天新增的檔案 ingest 進 wiki，
      完成後回報新增幾頁；沒有新檔就靜默不回報。
    cron: "0 22 * * *"
    reply_to: private
""")

    write(root / "start.py", '''"""團隊啟動入口 —— 框架在 ark_team_agent 套件裡。

設定集中在 team.yaml（+ scheduler.yaml 排程 + .env 機密）。
"""
from __future__ import annotations

import asyncio
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

from ark_team_agent.team import run_team

if __name__ == "__main__":
    try:
        asyncio.run(run_team(Path("team.yaml")))
    except KeyboardInterrupt:
        print("\\n平台已停止。")
''')
    write(root / "requirements.txt",
          "ark_team_agent   # 由 wheel 安裝，不從 PyPI\n"
          "# 🔴 換裝後驗 import 版號，不看 pip 輸出\n")
    env = ("# 🔴 每個人用自己的 token —— 同一 token 兩處 polling 會隨機吃訊息且不報錯\n"
           "TELEGRAM_BOT_TOKEN=your_token\nGEMINI_API_KEY=your_key\n")
    write(root / ".env.example", env)
    write(root / ".env", env)
    (root / "secrets").mkdir(exist_ok=True)
    (root / "secrets" / ".gitkeep").touch()


def setup_venv(root: Path, wheel: Path | None, kind: str, res: Result) -> None:
    """建 venv、裝 wheel、**驗 import 版號**（不看 pip 輸出）。"""
    venv = root / ".venv"
    py = venv / "bin" / "python"
    if not py.exists():
        r = subprocess.run([sys.executable, "-m", "venv", str(venv)],
                           capture_output=True, text=True)
        if r.returncode != 0:
            res.add("建立 venv", False, r.stderr.strip()[:200])
            return
    res.add("建立 venv", True, str(venv.relative_to(root)))

    if wheel is None:
        res.add("裝 wheel", False, "未提供 --wheel（之後手動裝，見下一步）")
        return

    pkg = "ark_bot_agent" if kind == "bot" else "ark_team_agent"
    spec = f"{wheel}[search,skills]" if kind == "bot" else str(wheel)
    r = subprocess.run([str(py), "-m", "pip", "install", "-q", spec],
                       capture_output=True, text=True)
    if r.returncode != 0:
        res.add("裝 wheel", False, (r.stderr or r.stdout).strip().splitlines()[-1][:200])
        return
    # 🔴 驗 import 版號，不看 pip 輸出（pip 說成功不代表裝進這個 venv）
    v = subprocess.run([str(py), "-c", f"import {pkg}; print({pkg}.__version__)"],
                       capture_output=True, text=True)
    if v.returncode != 0:
        res.add("驗 import 版號", False, v.stderr.strip().splitlines()[-1][:200])
        return
    res.add("裝 wheel + 驗 import", True, f"{pkg} {v.stdout.strip()}")

    if kind == "bot":
        # extras 缺了不報錯，只會靜默降級 → 明確驗一次
        e = subprocess.run([str(py), "-c", "import bm25s, jieba, apscheduler, jinja2"],
                           capture_output=True, text=True)
        res.add("驗 extras（search + skills）", e.returncode == 0,
                "四層搜尋與排程可用" if e.returncode == 0 else "extras 缺失 → 會靜默降級")


def run_upstream_validator(root: Path, kind: str, res: Result) -> None:
    """用上游 validator 驗產出 —— 上游改規則，這裡就會紅（防兩邊漂移）。"""
    if kind == "bot":
        script = UPSTREAM_SKILLS / "ark-agent-bot-builder" / "scripts" / "validate_agent.py"
        args = [str(root)]
    else:
        script = UPSTREAM_SKILLS / "ark-agent-team-builder" / "scripts" / "validate_team.py"
        args = [str(root / "team.yaml")]
    if not script.is_file():
        res.add("上游 validator", True, f"找不到 {script.name} → 跳過（非本機環境）")
        return
    r = subprocess.run([sys.executable, str(script), *args], capture_output=True, text=True)
    tail = (r.stdout or r.stderr).strip().splitlines()
    res.add("上游 validator", r.returncode == 0, tail[-1][:160] if tail else "")


def next_steps(root: Path, kind: str, wheel: Path | None) -> str:
    """印「還差什麼才能跑」—— 只列真正還沒做的。"""
    lines = ["", "📋 還差這些就能跑：", ""]
    n = 1
    if wheel is None:
        pkg = "ark_bot_agent[search,skills]" if kind == "bot" else "ark_team_agent"
        lines += [f"  {n}. 裝套件：.venv/bin/pip install './<wheel 檔>'"
                  f"{'[search,skills]' if kind == 'bot' else ''}", ""]
        n += 1
    lines += [f"  {n}. 填 token：cp .env.example .env  → 填 TELEGRAM_BOT_TOKEN", ""]
    n += 1
    if kind == "team":
        lines += [f"  {n}. 填權限：team.yaml 的 access.allowed_users 填你的 TG user_id",
                  "     （沒填誰都指揮不動，包括你自己）", ""]
        n += 1
        lines += [f"  {n}. 裝技能：python3 scripts/sync_skills.py（若已備 sync 腳本）", ""]
        n += 1
    lines += [f"  {n}. 啟動：.venv/bin/python start.py", ""]
    if kind == "team":
        lines += ["     ⏱️ 首次啟動兩階段：daemon 約 20 秒；kiro-cli backend 冷啟 2–4 分鐘。",
                  "        「送了沒回」先查 CPU 時間有沒有在動，再懷疑壞掉。", ""]
    lines += ["🎨 要客製化？改這三個地方就夠：", ""]
    if kind == "bot":
        lines += ["   agents.yaml（有誰） · bot.yaml（怎麼跑） · .kiro/steering/SOUL.md（是誰）"]
    else:
        lines += ["   team.yaml（誰在團隊 + 派工歸屬） · scheduler.yaml（何時） · 各 SOUL.md（是誰）"]
    return "\n".join(lines)


def create(kind: str, target: Path, preset_name: str, wheel: Path | None,
           use_venv: bool, health_port: int) -> Result:
    """主流程。回傳每個步驟的結果。"""
    res = Result()
    preset = load_preset(preset_name)
    res.add("讀 preset", True, f"{preset['name']} — {preset['description']}")

    if target.exists() and any(target.iterdir()):
        raise SystemExit(f"🔴 目標目錄非空：{target}（不覆蓋既有專案）")
    target.mkdir(parents=True, exist_ok=True)

    package = "ark_bot_agent" if kind == "bot" else "ark_team_agent"
    table = ("| `agents.yaml` | 有誰 ← 專案根哨兵 |\n| `bot.yaml` | 怎麼跑 |\n| `.env` | 只放機密 |"
             if kind == "bot" else
             "| `team.yaml` | 誰在團隊 + 派工歸屬（**架構本身**） |\n"
             "| `scheduler.yaml` | 何時自動做什麼 |\n| `.env` | 只放機密 |")
    scaffold_common(target, preset, package, table)
    res.add("產骨架（knowledge/shared · memory · artifacts · 人格）", True,
            f"{len(preset['agents'])} 個 agent")

    if kind == "bot":
        scaffold_bot(target, preset, preset.get("codename", "助手"))
        res.add("產設定檔", True, "agents.yaml · bot.yaml · start.py")
    else:
        scaffold_team(target, preset, health_port)
        res.add("產設定檔", True,
                f"team.yaml · scheduler.yaml · start.py（health {health_port} / 看板 {health_port + 5000}）")

    if use_venv:
        setup_venv(target, wheel, kind, res)
    else:
        res.add("建立 venv", True, "已跳過（--no-venv）")

    run_upstream_validator(target, kind, res)
    return res


def main(argv: list[str] | None = None) -> int:
    """CLI 入口。"""
    ap = argparse.ArgumentParser(
        description="一鍵產出可直接跑的 agent 專案（bot 或 team）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="範例：\n"
               "  create_project.py bot my-bot --wheel ./ark_bot_agent-1.0.16-py3-none-any.whl\n"
               "  create_project.py team my-team --preset gamedev --no-venv\n")
    ap.add_argument("kind", choices=["bot", "team"], help="bot=ark_bot_agent / team=ark_team_agent")
    ap.add_argument("target", help="輸出目錄（必須不存在或為空）")
    ap.add_argument("--preset", default="general", help="presets/*.yaml 的名字（預設 general）")
    ap.add_argument("--wheel", default=None, help="套件 wheel 檔路徑")
    ap.add_argument("--no-venv", action="store_true", help="不建 venv、不裝套件")
    ap.add_argument("--health-port", type=int, default=23050, help="team 的 health port（預設 23050）")
    ap.add_argument("--dry-run", action="store_true", help="只印會做什麼，不動檔案")
    args = ap.parse_args(argv)

    target = Path(args.target).resolve()
    wheel = Path(args.wheel).resolve() if args.wheel else None
    if wheel and not wheel.is_file():
        raise SystemExit(f"🔴 wheel 檔不存在：{wheel}")

    if args.dry_run:
        preset = load_preset(args.preset)
        print(f"📋 dry-run：{args.kind} 專案 → {target}")
        print(f"   preset  : {preset['name']}（{len(preset['agents'])} 個 agent）")
        print(f"   venv    : {'否' if args.no_venv else '是'}")
        print(f"   wheel   : {wheel or '(未提供)'}")
        print(f"   agents  : {', '.join(a['id'] for a in preset['agents'])}")
        return 0

    print(f"🚀 建立 {args.kind} 專案：{target}\n")
    res = create(args.kind, target, args.preset, wheel, not args.no_venv, args.health_port)
    print(next_steps(target, args.kind, wheel))
    ok = res.ok
    print(f"\n{'✅ 完成' if ok else '⚠️ 完成（有步驟未通過，見上方 ❌）'}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
