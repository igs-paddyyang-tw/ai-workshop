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
├── runtime/          # 執行層：PersistentDaemon、Config、Scheduler
└── business/         # 業務層：Skills、News、Web Search
```

## 進程模式

透過 `team.yaml` 切換：

| 模式 | 命令 | 延遲 | MCP Tools |
|------|------|------|-----------|
| 常駐 (Persistent) | `--legacy-ui --require-mcp-startup` | < 100ms | ✅ 載入 |
| Spawn (fallback) | `--no-interactive msg` | 2-5s | ✅ 每次重新載入 |

常駐模式特性：
- Health Loop（30 秒巡檢、自動重啟、指數退避）
- Message Queue + SQLite Overflow（backpressure 保護）
- Heartbeat + FailureMemory（錯誤偵測 → soft-pause）

## 對話回覆機制

### 常駐模式（MCP reply 驅動）

```
User(TG) → handle_message → daemon.send_message → stdin pipe → Agent
  → Agent 呼叫 MCP reply(text) → mcp_stdio → POST /api/chat/reply → TG
```

### Spawn 模式（同步等待）

```
User(TG) → handle_message → await agent.send(msg) → stdout → TG
```

## MCP 注意事項（Windows）

kiro-cli 的 MCP stdio 有三個 Windows 特有限制：

1. **stderr = 死亡** — MCP server 的 stderr 有任何輸出 → kiro-cli 判定 Transport closed
2. **UTF-8 BOM = 死亡** — mcp.json 有 BOM → JSON parser 失敗（PowerShell `Set-Content -Encoding UTF8` 會加 BOM）
3. **cp950 encode = 死亡** — stdout 含非 ASCII 字元且未用 `ensure_ascii=True` → UnicodeEncodeError → stderr traceback

解決方案：
- `json.dumps(ensure_ascii=True)` 所有 stdout 輸出
- logging 用 `NullHandler`（不寫 stderr）
- 用 Python 寫 mcp.json（避免 BOM）

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

```
agents/{name}/          ← kiro-cli 的 cwd（MCP 從這裡載入）
├── .kiro/
│   ├── steering/       # SOUL + BRAIN
│   └── settings/       # mcp.json（無 BOM！）
├── knowledge/
│   ├── wiki/           # 私有知識庫
│   └── raw/            # 原始文件
├── memory/
│   ├── memory.md       # 持久事實
│   └── daily/          # 每日紀錄
└── output/
```

## MCP 工具（11 tools）

| 工具 | 用途 |
|------|------|
| `reply(text, summary)` | 回覆使用者（唯一出口） |
| `send_to_instance(instance, msg)` | 跨 agent 通訊 |
| `delegate_task(instance, task)` | 委派任務 |
| `query_team_status()` | 團隊狀態 |
| `broadcast_all(message)` | 廣播全員 |
| `create_task` / `update_task` / `list_tasks` | 任務管理 |
| `wiki_query(query)` | 知識庫搜尋 |
| `record_spend(amount_usd)` | 記錄成本 |
| `log_to_leader(text)` | 回報 leader |

**前提：** 需先 `python start.py` 啟動 backend（port 33333）。

## 環境變數

參見 `.env.example`。
