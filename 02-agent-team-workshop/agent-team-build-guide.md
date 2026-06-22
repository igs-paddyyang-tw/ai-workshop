---
title: "Agent Team 建置教學 — 5 步驟從零到協作"
type: guide
created: 2026-05-26
updated: 2026-05-27
author: paddyyang
language: zh-TW
---

# Agent Team 建置教學 — 5 步驟從零到協作

使用 Ark Skills 建立多 Agent 協作團隊，透過 Telegram 指揮 AI 艦隊。

---

## 專案定位

**多 Agent 協作開發平台 — AI 團隊自動派工、開發、驗證**

核心能力：
- 多個 AI Agent 並行工作（各有獨立工作目錄）
- 透過 Telegram 指揮團隊（Group Topics 或私聊 @mention）
- Leader 自動拆解需求並派工
- 跨 Agent MCP 通訊（delegate_task / send_to_instance）
- 費用控管 + 掛起偵測 + 自動重啟

---

## 建置步驟總覽

| # | 方式 | 產出內容 | 必要性 |
|---|------|---------|--------|
| 0 | ark-env-doctor | 環境確認 + Skills 取得 | ✅ 必要 |
| 1 | ark-agent-team-builder | **完整專案骨架**（team.yaml + 目錄 + start.py + ark_team_core/ + .kiro/ 基礎） | ✅ 必要 |
| 2 | ark-kiro-init | 每個 agent 的完整 .kiro/ 配置（批次產出） | ✅ 必要 |
| 3 | 手動設定 | .env + Telegram Group（唯一手動步驟） | ✅ 必要 |
| 4 | start-team.bat | 雙擊啟動 | ✅ 必要 |
| 5 | 實戰派工 | 科技日報自動化（串接全部能力） | 🎯 驗證 |

```
Step 0: ark-env-doctor           → 環境確認 + 取得 Skills
Step 1: ark-agent-team-builder   → 一鍵產出完整可運作專案
         └─ scripts/build_team.py 執行後產出：
            team.yaml + scheduler.yaml + start.py
            src/ark_team_core/（16 模組）
            agents/ + tasks/ + docs/ + secrets/ + knowledge/
            .kiro/（admin 基礎配置）
            start-team.bat + requirements.txt + ...
Step 2: ark-kiro-init            → 批次產出所有 agent .kiro/
         └─ scripts/build_kiro.py 執行後產出：
            .kiro/（admin 完整版：SOUL + TEAM + KIRO + mcp.json）
            agents/{name}/.kiro/（每個 agent 完整配置）
Step 3: 手動設定                 → .env + Telegram Group + topic_id
Step 4: start-team.bat           → 雙擊啟動（py start.py）
Step 5: 實戰派工                 → 科技日報自動化（Telegram 收到 HTML 日報）
```

> **設計原則：** Script 產出確定性結構，AI 只做串聯和功能疊加。初始就有可以運作的版本。

---

## Step 0：環境準備

### 取得 Skills

```bash
git clone https://github.com/igs-paddyyang-tw/ark-kiro-skills .kiro/skills/
```

### 確認工具

```bash
kiro-cli --version
python --version      # 3.11+
git --version
```

### 觸發環境檢查（選用）

在 Kiro 聊天框輸入：

```
檢查我的開發環境
```

**檢查項目：**

| 項目 | 最低需求 |
|------|---------|
| Python | 3.11+ |
| kiro-cli | 已安裝且 login 完成 |
| Git | 已安裝 |
| Telegram Bot Token | 已取得（Step 3 需要） |

---

## Step 1：建立完整專案骨架

### 方式 A：Script 直接產出（推薦）

```bash
# 產出完整專案到指定目錄
python .kiro/skills/ark-agent-team-builder/scripts/build_team.py my-team

# 驗證結構完整性
python .kiro/skills/ark-agent-team-builder/scripts/build_team.py --validate my-team
```

### 方式 B：AI 觸發（自動呼叫 script）

在 Kiro 聊天框輸入：

```
建立 5 人 AI 團隊，角色：admin + leader + market + report + coder
```

AI 會呼叫 `build_team.py` 並產出完整結構。

### 產出結構

```
{project}/
├── team.yaml                    ← 團隊配置（含 topics / skip_resume / access）
├── scheduler.yaml               ← 排程定義（4 jobs，含 reply_to）
├── start.py                     ← 一鍵啟動（CoreDaemon + TelegramAdapter + Scheduler）
├── start-team.bat               ← Windows watchdog
├── start-team.sh                ← Mac/Linux watchdog
├── pyproject.toml
├── requirements.txt             ← python-telegram-bot + fastapi + uvicorn + ...
├── .env.example
├── .gitignore
├── README.md
│
├── src/
│   ├── ark_team_core/           ← 核心引擎（vendored，16 模組）
│   └── {project}_agent/         ← 業務層
│       ├── telegram_adapter.py  ← TG Bot 收發 + 路由
│       ├── api.py               ← HTTP API（reply/send/status）
│       ├── event_log.py         ← 事件日誌
│       ├── mcp_setup.py         ← 業務 MCP 工具骨架
│       └── tools/               ← 業務工具目錄
│
├── agents/                      ← 各 agent 工作目錄
│   ├── AGENTS.md
│   └── {name}-agent/
│       ├── docs/ + output/ + data/ + knowledge/
│
├── tasks/ + docs/ + secrets/ + knowledge/
│
└── .kiro/                       ← admin workspace（基礎版）
```

### 驗證

```bash
python .kiro/skills/ark-agent-team-builder/scripts/build_team.py --validate my-team
# ✅ 結構完整
```

---

## Step 2：配置每個 Agent 的 .kiro/

### Script 批次產出（推薦）

```bash
# 批次產出所有 agent 的 .kiro/
python .kiro/skills/ark-kiro-init/scripts/build_kiro.py my-team/team.yaml my-team

# clone 共用 Skills 倉庫
python .kiro/skills/ark-kiro-init/scripts/build_kiro.py --clone-skills my-team

# 驗證 .kiro/ 結構
python .kiro/skills/ark-kiro-init/scripts/build_kiro.py --validate my-team
```

### 每個 agent 產出

```
agents/{name}-agent/.kiro/
├── agents/{name}.json           ← Agent 定義
├── settings/mcp.json            ← MCP 設定（team_mcp.py 完整參數）
├── prompts/                     ← 提詞模板
└── steering/
    ├── SOUL.md                  ← 八段式角色定義
    ├── AGENTS.md + KIRO.md + MEMORY.md + TEAM.md + USER.md
```

### 驗證

```bash
python .kiro/skills/ark-kiro-init/scripts/build_kiro.py --validate my-team
# ✅ .kiro/ 結構完整
```

---

## Step 3：設定 Telegram（唯一手動步驟）

### 安裝依賴

```bash
cd my-team
pip install -r requirements.txt
```

### 建立 Bot + .env

```bash
# 1. Telegram 找 @BotFather → /newbot → 取得 token
cp .env.example .env
# 填入 TELEGRAM_BOT_TOKEN=你的token
```

### 純私聊模式（個人使用，最快）

team.yaml 不設 `group_id`，用 @mention 指定 agent：

```yaml
channel:
  bot_token_env: TELEGRAM_BOT_TOKEN
  # group_id 不設 → 純私聊 @mention 模式
```

### Group Topics 模式（多人協作）

```bash
curl "https://api.telegram.org/bot你的TOKEN/getUpdates" | python -m json.tool
```

找到 `chat.id`（group_id）和 `message_thread_id`（topic_id），填入 team.yaml。

---

## Step 4：啟動團隊

### Windows

```bash
start-team.bat
```

### Mac / Linux

```bash
bash start-team.sh
```

### 驗證啟動

```bash
curl http://127.0.0.1:13030/api/status
```

---

## Step 5：實戰派工 — 科技日報自動化

> **目標：** 讓 Agent 團隊每日自動抓取科技新聞、產出 HTML 日報、推送到 Telegram。

### 5.1 任務描述

在 Telegram 對 leader 發送：

```
@leader 建立每日科技日報系統：
- market-agent 每日 08:00 抓取 AI/工具/遊戲 重大新聞（過去 24 小時）
- report-agent 整理成 HTML 日報（暗黑科技風格）
- 自動推送到 Telegram news_daily topic
```

### 5.2 Leader 自動拆解任務

Leader 收到需求後，用 `delegate_task` 分派：

```
📋 任務：科技日報爬蟲 Skill
📄 規格：docs/specs/daily-news-spec.md
🎯 你負責：用 web search 蒐集今日 AI/工具/遊戲 新聞，整理 2-3 則精選
📁 範圍：agents/market-agent/
✅ 驗收：能回傳結構化新聞列表（標題 + 摘要 + 連結）
📏 大小：S
```

```
📋 任務：HTML 日報渲染
📄 規格：docs/specs/daily-news-spec.md
🎯 你負責：將新聞列表渲染為暗黑科技風格 HTML，含 emoji + 標題 + 金句
📁 範圍：agents/report-agent/output/
✅ 驗收：產出 daily-news-{日期}.html，可瀏覽器開啟
📏 大小：S
```

### 5.3 Agents 執行

**market-agent** 使用 `ark-web-scraper` Skill：

```
在 Kiro 聊天框（market-agent 工作目錄）輸入：
「用 web search 蒐集今日 AI/工具/遊戲 重大新聞，整理 2-3 則精選，
 格式：標題 + 一句話摘要 + 連結」
```

**report-agent** 使用 `ark-news-daily` Skill：

```
在 Kiro 聊天框（report-agent 工作目錄）輸入：
「將以下新聞整理成暗黑科技風格 HTML 日報，
 產出到 output/daily-news-{今日日期}.html」
```

### 5.4 排程自動化

編輯 `scheduler.yaml` 加入每日觸發：

```yaml
timezone: Asia/Taipei

jobs:
  - id: daily-news
    target: market-agent
    prompt: |
      執行每日科技新聞流程（ark-news-daily Skill）：
      1. 用 web search 蒐集今日 AI/工具/遊戲/硬體 重大新聞（過去 24 小時）
      2. 整理 2-3 則精選（標題 + 一句話摘要 + 連結）
      3. 產出完整版 → output/{今日日期}/daily-news-{今日日期}.md
      4. 組裝精簡版摘要（emoji + 標題 + 金句）
      5. 用 push_to_topic("news_daily", 精簡版摘要) 推送到通報群
    cron: "0 8 * * *"
    reply_to: news_daily
```

### 5.5 驗收標準

| 項目 | 驗收條件 |
|------|---------|
| 新聞蒐集 | market-agent 回傳 2-3 則結構化新聞 |
| HTML 日報 | report-agent 產出 HTML 檔案，可瀏覽器開啟 |
| 排程推送 | 每日 08:00 Telegram 收到精簡版摘要 |
| 格式正確 | emoji + 標題 + 金句，≤ 150 字 |

### 5.6 Telegram 收到的效果

```
📰 今日科技日報 2026-05-27

🤖 OpenAI 發布 GPT-5 Turbo
→ 推理速度提升 3x，API 費用降低 50%

🎮 Unity 宣布免費方案回歸
→ 取消 Runtime Fee，開發者社群熱烈回應

🔧 GitHub Copilot 支援 Claude 4
→ 可在 VS Code 直接切換 LLM 後端

📎 完整日報：[daily-news-20260527.html]
```

---

## 技術棧總結

| 層 | 技術 | 來源 |
|----|------|------|
| 團隊骨架 | team.yaml + 目錄 + bat | ark-agent-team-builder / build_team.py |
| 核心引擎 | ark_team_core（16 模組） | ark-agent-team-builder（vendored） |
| 業務層 | telegram_adapter + api + event_log | ark-agent-team-builder（vendored） |
| Agent 配置 | .kiro/ steering + mcp.json + skills | ark-kiro-init / build_kiro.py |
| AI 後端 | kiro-cli subprocess | kiro-cli |
| 通訊 | Telegram Bot API | python-telegram-bot |
| 跨 Agent | MCP Tools（team_mcp.py） | ark_team_core |
| 排程 | scheduler.yaml + Scheduler | ark_team_core |
| 新聞蒐集 | web search + ark-web-scraper | market-agent |
| 日報渲染 | ark-news-daily | report-agent |

---

## 參考：team.yaml 完整格式

```yaml
# Agent Team 配置
channel:
  bot_token_env: TELEGRAM_BOT_TOKEN
  group_id: -100xxxxxxxxxx        # 有值 = Group Topics；無值 = 純私聊
  general_topic_id: 4

topics:
  news_daily: 3                   # 科技日報推送 topic
  assistant_chat: 4               # 助理對話區

access:
  mode: locked
  allowed_users:
    - 123456789

defaults:
  backend: kiro-cli
  model: auto

cost_guard:
  daily_limit_usd: 15.0
  warn_at_percentage: 80
  timezone: Asia/Taipei

hang_detector:
  enabled: true
  timeout_minutes: 60
  escalation_minutes: 180

instances:
  admin-agent:
    working_directory: "."
    description: "⚙️ 管理者 — 服務監控、重啟、成本控制"
    private_chat: 123456789
    role: admin
    skip_resume: true

  leader-agent:
    working_directory: agents/leader-agent
    description: "🧠 專案經理 — 需求分析、派工、驗收"
    topic_id: 4
    general_topic: true
    role: leader
    skip_resume: true

  market-agent:
    working_directory: agents/market-agent
    description: "📰 市場研究員 — 社群輿情、競品監控、產業新聞"
    role: worker
    skip_resume: true

  report-agent:
    working_directory: agents/report-agent
    description: "📋 報告專員 — 洞察整理、圖表、HTML Dashboard"
    role: worker
    skip_resume: true

  coder-agent:
    working_directory: agents/coder-agent
    description: "💻 程式設計師 — FastAPI / 前後端實作"
    role: worker
    skip_resume: true

health_port: 13030
```

---

## 進階主題

### 新增 Agent

```bash
# 1. 編輯 team.yaml 加入新 instance
# 2. 重新執行 build_kiro.py（冪等，只補缺少的）
python .kiro/skills/ark-kiro-init/scripts/build_kiro.py team.yaml
# 3. 重啟服務
```

### 新增業務 MCP Tool

在 `src/{team}_agent/tools/` 下新增工具，在 `mcp_setup.py` 註冊：

```python
# src/my_team_agent/tools/push_to_topic.py
def push_to_topic(topic: str, text: str) -> str:
    """推送訊息到指定 Telegram Topic。"""
    # 實作略
    return "已推送"
```

### 排程自動化

```yaml
# scheduler.yaml — 用 id 不用 name，必須有 reply_to
jobs:
  - id: daily-news
    target: market-agent
    prompt: "執行每日科技新聞流程..."
    cron: "0 8 * * *"
    reply_to: news_daily
```

### 重啟服務

```bash
echo "" > restart.flag   # watchdog 3 秒後自動拉起
```

---

## 附錄：完整建置流程圖

```
Step 0: git clone ark-kiro-skills .kiro/skills/
         │
         ▼
Step 1: build_team.py my-team
         │
         ├── team.yaml + scheduler.yaml
         ├── start.py + start-team.bat + start-team.sh
         ├── src/ark_team_core/（16 模組）
         ├── src/{project}_agent/（業務層：TG + API + event_log）
         ├── agents/（三件套 + 知識庫五件套）
         ├── tasks/ + docs/ + secrets/ + knowledge/
         └── .kiro/（admin 基礎版）
         │
         ▼
Step 2: build_kiro.py team.yaml
         │
         ├── .kiro/（admin 完整版）
         └── agents/{name}/.kiro/（每個 agent）
         │
         ▼
Step 3: 手動填 .env + TG Group
         │
         ▼
Step 4: start-team.bat
         │
    ┌────┴────┬────────┬────────┐
    ▼         ▼        ▼        ▼
  admin    leader   market   report   ← 各 Agent 並行
             │
             ▼
     delegate_task → workers          ← Step 5 派工

Step 5 科技日報流程：
  leader → market-agent（蒐集新聞）
         → report-agent（渲染 HTML）
         → push_to_topic("news_daily", 摘要)
         → Telegram 收到日報 📰
```

---

*作者：paddyyang ｜ 更新：2026-05-27*
