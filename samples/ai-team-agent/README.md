# Ark Agent Team Platform

> 多 Agent 協作平台 — 8 agents 遊戲開發場景，四層架構（Gateway / Coordinator / Runtime / Business）

## 快速開始

```bash
python -m venv .venv
source .venv/bin/activate   # Linux/Mac
# .venv\Scripts\activate    # Windows

pip install -r requirements.txt
cp .env.example .env        # 填入 TELEGRAM_BOT_TOKEN + GEMINI_API_KEY

python start.py
```

## 架構

```
src/
├── gateway/          # 入口層：Telegram Bot、FastAPI、MCP stdio
├── coordinator/      # 協調層：A2A、DB、Events、Memory、Wiki、Services
├── runtime/          # 執行層：PersistentDaemon、Config、Scheduler
└── business/         # 業務層：Skills、News、Web Search
```

## 團隊配置

3 種 team.yaml 場景：

| 設定 | 指令 | 成員 |
|------|------|------|
| **完整 8 人（預設）** | `python start.py` | admin + pm + coder + qa + ai-dev + market + data + report |
| 研發 5 人 | `cp team-dev.yaml team.yaml` | admin + pm + ai-dev + coder + qa |
| 營運 5 人 | `cp team-ops.yaml team.yaml` | admin + pm + market + data + report |

### Agent 角色與指揮鏈

```
使用者 → admin-agent（預設入口）→ leader-agent（分析+派工）→ workers（執行）→ leader-agent（驗收）→ reply
```

| Agent | 角色 | 職責 | 模式 |
|-------|------|------|------|
| admin-agent | admin | 預設入口、服務監控、成本控制 | 常駐 |
| leader-agent | leader | 需求分析、任務拆解、派工驗收 | 常駐 |
| coder-agent | worker | 全端開發、API 實作 | 動態 |
| qa-agent | worker | 測試策略、Code Review | 動態 |
| ai-dev-agent | worker | LLM 整合、Prompt 工程、MCP 開發 | 動態 |
| market-agent | worker | 競品監控、輿情分析、新聞爬取 | 動態 |
| data-agent | worker | 數據分析、KPI 追蹤、遊戲指標 | 動態 |
| report-agent | worker | 報告產出、圖表渲染、定期摘要 | 動態 |

## 進程模式

透過 `team.yaml` 切換：

| 模式 | 延遲 | MCP Tools |
|------|------|-----------|
| 常駐 (Persistent) | < 100ms | ✅ |
| Spawn (fallback) | 2-5s | ✅ |

## .kiro 駕馭架構（5 檔制）

每個 Agent 的 `.kiro/steering/` 有 5 個檔案：

| 檔案 | 職責 | 載入 |
|------|------|------|
| SOUL.md | 人格、身份、使用者資訊 | 常駐 |
| BRAIN.md | 三層資源規則、品質護欄、MCP 工具 | 常駐 |
| MEMORY.md | 專案狀態、技術決策、踩坑 | 常駐 |
| TEAM.md | 完整 8 人清單 + 指揮鏈 + 協作規則 | 常駐 |
| KIRO.md | Python 程式碼規範 | fileMatch（src/**/*.py）|

## 知識庫

```
agents/{name}/knowledge/
├── wiki/    ← 私有知識（含遊戲業務場景）
└── raw/     ← 原始文件

knowledge/shared/wiki/  ← 全域共用
```

## MCP 工具（11 tools）

`reply` / `send_to_instance` / `delegate_task` / `query_team_status` / `broadcast_all` / `create_task` / `update_task` / `list_tasks` / `wiki_query` / `record_spend` / `log_to_leader`

## MCP 注意事項（Windows）

1. **stderr = 死亡** — MCP server stderr 有輸出 → Transport closed
2. **UTF-8 BOM = 死亡** — mcp.json 有 BOM → JSON parser 失敗
3. **cp950 encode = 死亡** — stdout 含非 ASCII 且未 `ensure_ascii=True` → crash

## API

| 分類 | 端點 |
|------|------|
| Agents | `GET /api/agents` / `GET /api/agents/{id}/health` / `PATCH /api/agents/{id}/persistent` / `POST /api/agents/{id}/rotate` |
| Chat | `POST /api/chat/reply` / `POST /api/chat/send` |
| Memory | `POST /api/v1/memory/recall` / `GET /api/v1/memory/daily/{agent}` |
| Wiki | `GET /api/v1/wiki/search` / `POST /api/v1/wiki/ingest` |
| Skills | `GET /api/v1/skills` / `POST /api/v1/skills/invoke` |
| Health | `GET /api/health` |

## 品質指標（2026-07-27）

| 指標 | 狀態 |
|------|------|
| smoke_test | ✅ 17 passed |
| Spec Drift Score | ✅ ~97/100 |
| API 端點覆蓋 | ✅ 100% |
| 依賴規則違規 | ✅ 0 |
| TG 任務通知 | ✅ 修復（issue_id / title / agent_id / output 完整顯示） |
| 對話軌跡追蹤 | ✅ chat_trace.py（SQLite，7 天清理） |
| DB Migration 005 | ✅ 修正 pending+assignee 狀態不一致 |
