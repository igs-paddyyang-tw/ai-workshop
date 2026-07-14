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

## 架構

```
src/
├── gateway/          # 入口層：Telegram Bot、FastAPI、MCP stdio
├── coordinator/      # 協調層：A2A、DB、Events、Memory、Wiki、Services
├── runtime/          # 執行層：Agent Process、Config、Scheduler
└── business/         # 業務層：Skills、News、Web Search
```

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
