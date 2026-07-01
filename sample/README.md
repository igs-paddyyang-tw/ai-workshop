# AI Agent Team Platform — 完整版

> 教學完直接拿來用。一套架構，兩種團隊配置。

## 選擇你的團隊

| 配置 | 指令 | 成員 | 適合場景 |
|------|------|------|---------|
| **營運團隊** | `cp team-ops.yaml team.yaml` | admin + pm + market + data + report | 市場監控、數據分析、報告產出 |
| **研發團隊** | `cp team-dev.yaml team.yaml` | admin + pm + ai-dev + coder + qa | AI 開發、全端實作、品質保證 |

## 快速啟動

```bash
# 1. 安裝依賴
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# 2. 設定環境
cp .env.example .env
# 填入 TELEGRAM_BOT_TOKEN（必要）

# 3. 選擇團隊（二擇一）
cp team-ops.yaml team.yaml    # 營運團隊
# cp team-dev.yaml team.yaml  # 研發團隊

# 4. 啟動
python start.py
```

## 架構

```
┌─────────────────────────────────────────────────────────┐
│                   入口層 (Gateway)                        │
│      Telegram Bot │ REST API │ Web Dashboard             │
├─────────────────────────────────────────────────────────┤
│                  協調層 (Coordinator)                      │
│   TaskLifecycle │ A2A Protocol │ EventBus │ Discovery    │
├─────────────────────────────────────────────────────────┤
│                  執行層 (Runtime)                          │
│     CoreDaemon │ AgentProcess │ Scheduler │ MCP Registry │
├─────────────────────────────────────────────────────────┤
│                  服務層 (Services)                         │
│  CostTracker │ AuditLogger │ HealthMonitor │ Autopilot   │
├─────────────────────────────────────────────────────────┤
│                  知識層 (Knowledge)                        │
│          Wiki │ Memory │ raw/ → wiki/ │ FTS Search        │
└─────────────────────────────────────────────────────────┘
```

## 專案結構

```
sample/
├── start.py                 ← 一鍵啟動（asyncio 多進程）
├── start-team.bat           ← Windows watchdog
├── start-team.sh            ← Linux/Mac watchdog
├── team.yaml                ← 當前團隊配置（軟複製）
├── team-ops.yaml            ← 營運團隊配置
├── team-dev.yaml            ← 研發團隊配置
├── scheduler.yaml           ← 排程任務定義
├── .env.example
├── requirements.txt
├── pyproject.toml
│
├── src/
│   ├── bootstrap.py         ← 啟動邏輯（DB→API→Agents→Bot→Scheduler）
│   ├── runtime/             ← 執行層（CoreDaemon + Agent 進程管理）
│   ├── coordinator/         ← 協調層
│   │   ├── a2a/            ← Agent-to-Agent 協議
│   │   ├── db/             ← SQLite 持久化
│   │   ├── events/         ← EventBus 事件系統
│   │   ├── services/       ← 運維服務（費用/審計/健康/自動駕駛）
│   │   └── task_lifecycle.py
│   ├── gateway/             ← 入口層
│   │   ├── api/            ← REST API（21+ 端點）
│   │   ├── telegram/       ← Bot handlers + notifications
│   │   └── gemini_chat.py
│   └── business/            ← 業務技能（新聞/渲染/搜尋）
│
├── agents/                  ← Agent 工作目錄
│   ├── admin-agent/         ← ⚙️ 系統管理者
│   ├── pm-agent/            ← 🧠 專案經理
│   ├── market-agent/        ← 📰 市場研究員（ops）
│   ├── data-agent/          ← 📊 數據分析師（ops）
│   ├── report-agent/        ← 📋 報告專員（ops）
│   ├── ai-dev-agent/        ← 🤖 AI 工程師（dev）
│   ├── coder-agent/         ← 💻 全端工程師（dev）
│   └── qa-agent/            ← 🧪 QA 工程師（dev）
│
├── .kiro/                   ← Admin workspace 配置
├── apps/web/                ← Next.js Dashboard
├── knowledge/               ← 共用知識庫
├── config/                  ← 新聞來源等配置
├── data/                    ← SQLite 資料庫
├── logs/                    ← 運行日誌
├── secrets/                 ← 機密檔案
├── docs/                    ← 設計文件
│   ├── workshop-map.md     ← 程式碼 ↔ 課程對照
│   └── specs/              ← Spec 範例
├── Dockerfile
├── Dockerfile.web
├── docker-compose.prod.yml
└── tests/
```

## 實戰能力

| 能力 | 支撐模組 |
|------|---------|
| 5 Agent 真正並行 | `runtime/daemon.py` — spawn kiro-cli subprocess |
| 任務狀態完整流轉 | `coordinator/task_lifecycle.py` — backlog→queued→executing→done |
| Agent 之間對話 | `coordinator/a2a/protocol.py` — delegate_task / send_to_instance |
| 持久化 | `coordinator/db/` — SQLite（任務/事件/費用不遺失）|
| 費用控管 | `coordinator/services/cost_tracker.py` — daily_limit + 告警 |
| 排程自動化 | `runtime/scheduler.py` + `scheduler.yaml` — cron 觸發 |
| 故障偵測 | `coordinator/services/health_monitor.py` — hang_detector + restart |
| 審計日誌 | `coordinator/services/audit_logger.py` — 所有操作可追溯 |
| Web Dashboard | `apps/web/` — Next.js（KPI + Agent Grid + 即時更新）|
| Docker 部署 | `docker-compose.prod.yml` — 一鍵上線 |

## Telegram Bot 指令

| 指令 | 功能 |
|------|------|
| `/start` | 歡迎訊息 |
| `/status` | 團隊即時狀態 |
| `/agents` | Agent 列表 |
| `/assign <描述>` | 建立任務並派工 |
| `/board` | 看板摘要 |
| `/costs` | 費用報告 |
| `/queue` | 待處理佇列 |

## API 端點（部分）

```bash
curl http://localhost:33333/api/health
curl http://localhost:33333/api/agents
curl http://localhost:33333/api/admin/dashboard/stats
curl http://localhost:33333/api/admin/costs
curl http://localhost:33333/api/admin/audit
```

## Web Dashboard

```bash
cd apps/web && npm install && npm run dev
# http://localhost:3000
```

## Docker 部署

```bash
docker compose -f docker-compose.prod.yml up -d
```

## 加入新 Agent

1. 編輯 `team-ops.yaml`（或 team-dev.yaml）加入新 instance
2. 建立 `agents/new-agent/` 目錄 + `.kiro/steering/SOUL.md`
3. 重啟：`echo "" > restart.flag`（watchdog 3 秒後自動拉起）

## Workshop 對照

本專案 = Workshop 01-05 的完整產出。每堂課對應的程式碼：

| Workshop | 看哪裡 |
|----------|--------|
| 01 Agent 初始 | `agents/*/. kiro/steering/SOUL.md` + `src/gateway/telegram/` |
| 02 Skills | `src/business/` + `config/` |
| 03 Wiki | `knowledge/` + 每 agent 的 `knowledge/` |
| 04 Agent Team | `src/runtime/` + `src/coordinator/a2a/` + `team.yaml` |
| 05 平台管理 | `src/gateway/api/` + `apps/web/` + `src/coordinator/services/` |

---

*架構同 ai-team-agent，可獨立實戰運作。*
