# Ark Agent Team Platform

> 多 Agent 協作平台 — 基於四層架構（Gateway / Coordinator / Runtime / Business）

## 快速開始

```bash
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # Linux/Mac

pip install -r requirements.txt
cp .env.example .env          # 填入 TELEGRAM_BOT_TOKEN 等

python start.py
```

## 分層啟動（Tier）

| Tier | 功能 | 條件 |
|------|------|------|
| 0 | Prompts + Skills + Wiki + MCP | 永遠可用 |
| 1 | Telegram Bot | 需 TELEGRAM_BOT_TOKEN |
| 2 | kiro-cli Agent | 需 kiro-cli 在 PATH |
| 3 | Team A2A 派工 | 需 team.yaml |

## 架構

```
src/
├── gateway/          # 入口層：Telegram Bot、FastAPI、MCP stdio
├── coordinator/      # 協調層：A2A、DB、Events、Memory、Wiki、Services
├── runtime/          # 執行層：Agent Process、Config、Scheduler、PersistentDaemon
└── business/         # 業務層：Skills、News、Web Search
```

## 進程模式

平台支援雙模式，透過 `team.yaml` 一行切換：

```yaml
defaults:
  persistent: true   # 常駐模式（預設）
  persistent: false  # Spawn 模式（fallback）
```

| 模式 | 延遲 | 資源 | Context |
|------|------|------|---------|
| 常駐 (Persistent) | < 100ms | 常駐佔 RAM | 天然保持 session |
| Spawn | 2-5 秒 | 空閒零佔用 | --resume 每次載入 |

常駐模式使用 `--legacy-ui` + stdin pipe，包含：
- Health Loop（30 秒巡檢、自動重啟、指數退避）
- Message Queue + SQLite Overflow（backpressure 保護）
- Heartbeat（外部 watchdog 偵測凍結）
- FailureMemory（重複錯誤偵測 → soft-pause）

## 對話回覆機制

### 常駐模式（MCP reply 驅動）

```
User(TG) → handle_message → daemon.send_message → stdin pipe → Agent 思考
  → Agent 呼叫 MCP reply(text) → POST /api/chat/reply → TG 回覆使用者
```

- Agent **必須**用 `reply()` tool 回覆使用者（所有 agent steering 已配置）
- 不再依賴 stdout regex 截取（已移除）
- 支援多使用者 routing（per-message chat_id 追蹤）
- 智慧 timeout：300s + 活動偵測寬限 120s

### Spawn 模式（同步等待）

```
User(TG) → handle_message → await agent.send(text) → stdout → TG 回覆
```

- 直接等待進程結束，拿 stdout 回覆
- 無需 MCP reply tool

## Agent 團隊

| Agent | 角色 | 職責 |
|-------|------|------|
| admin-agent | admin | 服務監控、重啟、成本控制、分流 |
| pm-agent | leader | 需求分析、派工、驗收 |
| coder-agent | worker | 全端開發 |
| ai-dev-agent | worker | AI/LLM 工程 |
| qa-agent | worker | 測試、品質保證 |
| data-agent | worker | 數據分析 |
| market-agent | worker | 市場研究 |
| report-agent | worker | 報告產出 |

## Agent 目錄結構

每個 agent 遵循統一結構：

```
agents/{name}/
├── .kiro/
│   ├── steering/     # SOUL + BRAIN + GUARDRAILS + TEAM + ...
│   ├── prompts/      # route-message.md 等
│   └── settings/     # mcp.json
├── knowledge/
│   ├── wiki/         # 私有知識庫
│   └── raw/          # 原始文件
├── memory/
│   ├── memory.md     # 持久事實（≤2000 tokens）
│   ├── recent.md     # 最近經驗
│   └── daily/        # 每日紀錄
└── output/
    ├── drafts/
    ├── exports/
    ├── reports/
    └── skills/
```

## MCP 工具

平台啟動後，Kiro IDE 可透過 MCP stdio server 使用：

- `reply` / `send_to_instance` / `broadcast_all` — 通訊
- `delegate_task` / `create_task` / `update_task` / `list_tasks` — 任務管理
- `query_team_status` — 團隊狀態
- `wiki_query` — 知識庫搜尋
- `record_spend` / `log_to_leader` — 成本與回報

**前提：** 需先 `python start.py` 啟動 backend（port 33333）。

## 環境變數

參見 `.env.example`。
