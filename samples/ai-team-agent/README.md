# Ark Agent Team Platform

> 多 Agent 協作平台 — 8 agents 遊戲開發場景，四層架構（Gateway / Coordinator / Runtime / Business）

## 快速開始

```bash
python -m venv .venv
source .venv/bin/activate   # Linux/Mac
# .venv\Scripts\activate    # Windows

pip install -r requirements.txt
cp .env.example .env        # 填入 TELEGRAM_BOT_TOKEN + ALLOWED_USERS

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
| **完整 8 人（預設）** | `python start.py` | admin + leader + coder + qa + ai-dev + market + data + report |
| 研發 5 人 | `cp team-dev.yaml team.yaml` | admin + leader + ai-dev + coder + qa |
| 營運 8 人 | `cp team-ops.yaml team.yaml` | admin + leader + market + data + report（+ others） |

### Agent 角色與指揮鏈

```
使用者(TG) → leader-agent（入口+派工）→ workers（執行）→ leader-agent（驗收）→ reply
admin-agent（背景：服務監控、成本控制，不處理使用者需求）
```

| Agent | 角色 | 職責 | 模式 | 可被派工 |
|-------|------|------|------|---------|
| admin-agent | admin | 服務監控、重啟、成本控制 | 常駐 | ❌ |
| leader-agent | leader | **使用者入口**、需求分析、任務拆解、派工驗收 | 常駐 | ❌ |
| coder-agent | worker | 全端開發、API 實作 | 動態 | ✅ |
| qa-agent | worker | 測試策略、Code Review | 動態 | ✅ |
| ai-dev-agent | worker | LLM 整合、Prompt 工程、MCP 開發 | 動態 | ✅ |
| market-agent | worker | 競品監控、輿情分析、新聞爬取 | 動態 | ✅ |
| data-agent | worker | 數據分析、KPI 追蹤、遊戲指標 | 動態 | ✅ |
| report-agent | worker | 報告產出、圖表渲染、定期摘要 | 動態 | ✅ |

## 進程模式

透過 `team.yaml` 的 `persistent` 欄位控制：

| 模式 | 說明 | MCP Tools |
|------|------|-----------|
| 常駐 (Persistent) | 啟動時即開，stdin pipe 送訊 | ✅ |
| 動態 (Spawn on demand) | 收到訊息時自動啟動，閒置後回收 | ✅ |

## .kiro 駕馭架構（5 檔制）

每個 Agent 的 `.kiro/steering/` 有 5 個檔案：

| 檔案 | 職責 | 載入 |
|------|------|------|
| SOUL.md | 人格、身份、核心使命、來源標記規則 | 常駐 |
| BRAIN.md | 三層資源規則、Wiki 速查表、品質護欄 | 常駐 |
| MEMORY.md | 專案狀態、技術決策、踩坑 | 常駐 |
| TEAM.md | 完整 8 人清單 + 指揮鏈 + 可派工標記 | 常駐 |
| KIRO.md | Python 程式碼規範 | fileMatch（src/**/*.py）|

## Skills 配置

每個 Agent 的 `.kiro/skills/` 含角色專屬 skills + 共用 skills：

| 共用（所有 agent） | 角色專屬範例 |
|-------------------|-------------|
| ark-wiki-engine | leader: ark-superpowers, ark-project-planning |
| ark-code-spec-validator | coder: ark-webapp-generator, ark-db-query |
| ark-doc-coauthoring | qa: ark-test-runner, ark-code-review |

## 知識庫

```
agents/{name}/knowledge/
├── wiki/    ← 私有知識
└── raw/     ← 原始文件

knowledge/shared/
├── wiki/    ← 全域共用（跨 agent）
└── raw/     ← 共用原始資料
```

## MCP 工具（11 tools）

`reply` / `send_to_instance` / `delegate_task` / `query_team_status` / `broadcast_all` / `create_task` / `update_task` / `list_tasks` / `wiki_query` / `record_spend` / `log_to_leader`

## MCP 注意事項（Windows）

1. **stderr = 死亡** — MCP server stderr 有輸出 → Transport closed
2. **UTF-8 BOM = 死亡** — mcp.json 有 BOM → JSON parser 失敗
3. **cp950 encode = 死亡** — stdout 含非 ASCII 且未 `ensure_ascii=True` → crash

修正：`ensure_ascii=True` + `NullHandler` + Python `write_bytes()` 寫入 mcp.json

## .env 設定

```bash
TELEGRAM_BOT_TOKEN=your-bot-token
API_PORT=33333
ALLOWED_USERS=your-telegram-user-id   # 取得方式：對 Bot 傳 /start
```

## API

| 分類 | 端點 |
|------|------|
| Agents | `GET /api/agents` / `GET /api/agents/{id}/health` / `PATCH /api/agents/{id}/persistent` |
| Chat | `POST /api/chat/reply` / `POST /api/chat/send` / `POST /api/chat/notify` |
| Tasks | `POST /api/tasks` / `GET /api/board` / `PATCH /api/tasks/{id}/complete` / `PATCH /api/tasks/{id}/unblock` |
| Memory | `POST /api/v1/memory/recall` / `GET /api/v1/memory/daily/{agent}` |
| Wiki | `GET /api/v1/wiki/search` / `POST /api/v1/wiki/ingest` |
| Skills | `GET /api/v1/skills` / `POST /api/v1/skills/invoke` |
| Health | `GET /api/health` |
| Issues *(deprecated)* | `GET /api/issues` / `POST /api/issues` / `PATCH /api/issues/{id}/complete` |

## 品質指標（2026-07-27）

| 指標 | 狀態 |
|------|------|
| smoke_test | ✅ 36 passed |
| Spec Drift Score | ✅ ~97/100 |
| API 端點覆蓋 | ✅ 100% |
| 依賴規則違規 | ✅ 0 |
| leader-agent 回覆 | ✅ 修復（7-8 秒，MCP reply 正常）|
| config.py health loop | ✅ 修復（idle_timeout_minutes AttributeError）|
| 指揮鏈 | ✅ IDE→ai-team-agent / TG→leader-agent（雙入口分離）|
| Skills 安裝 | ✅ 所有 agent 補齊共用 skills + leader 核心 skills |
| 駕馭工程 | ✅ BRAIN/SOUL/TEAM/MEMORY 全面強化（from ai-bot 移植）|
| .kiro 主入口 | ✅ ai-team-agent.json（通用 orchestrator）|
| 根目錄記憶架構 | ✅ memory/ 目錄建立（memory.md / recent.md / daily/）|
| 任務系統統一 | ✅ MCP tools 改寫 tasks 表，看板正確顯示 completed |
| /api/issues | ✅ 標記 Deprecated，fallback 仍可用 |
