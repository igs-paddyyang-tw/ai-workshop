# ai-team-agent 優化報告

**日期**：2026-07-27  
**執行者**：CTO  
**涵蓋 commits**：`069b942` → `ef02add`（今日 8 個 commit）

---

## 摘要

今日針對 ai-team-agent 進行全面系統性優化，聚焦三個方向：
1. **架構簡化** — 移除 Gemini/LLM 外部依賴，回歸純 kiro-cli 驅動
2. **對話流程修正** — 修復 5 個影響使用者體驗的路由與通知問題
3. **指令對齊** — 補齊 TG 管理指令與 API 的對應缺口

優化前 Drift Score：97/100（spec 對齊）  
優化後架構更精簡，依賴更少，可靠性更高。

---

## 一、架構簡化（移除 Gemini 依賴）

### 背景

原架構設計了 4 個 Tier（0→1→2→3→4），其中 Tier 2 為 Gemini/OpenAI LLM API。
分析後發現：**Gemini 對核心對話流程完全無關，只服務 3 個輔助功能，且全部有 fallback。**

### 移除項目

| 檔案 / 模組 | 原用途 | 處置 |
|-------------|--------|------|
| `src/gateway/gemini_chat.py` | Gemini 直接呼叫 | 刪除 |
| `src/business/web_search.py` | Gemini grounding 網路搜尋 | 刪除 |
| `src/business/skills/internal/web_search.py` | WebSearchSkill | 刪除 |
| `src/coordinator/services/growth.py` | GrowthDetector 自我成長 | 刪除 |
| `wiki/engine.py` `_rag_answer()` | Gemini RAG 語意合成 | 移除方法 |
| `wiki/search/layer3_rerank.py` | Gemini LLM rerank | 改為 passthrough |
| `memory/daily_log.py` `gemini_fn` | LLM 摘要生成 | 改為 fallback 模板 |
| `memory/consolidate.py` `gemini_fn` | LLM 蒸餾 daily → memory | 移除參數 |

### 簡化後 Tier 架構

```
Tier 0  Skills + Wiki + API
        平台基礎層，零設定可用
        FastAPI / SQLite / EventBus / BM25 搜尋 / Memory

Tier 1  Telegram Bot
        使用者入口，接上 TG
        需要：TELEGRAM_BOT_TOKEN

Tier 2  kiro-cli Agent
        AI 執行核心，Agent 真正「會思考」
        PersistentDaemon / MCP tools / stdin pipe
        需要：kiro-cli 在 PATH

Tier 3  Team A2A
        8-agent 多人協作、任務派送、排程
        admin+pm 常駐，6 workers 動態 lazy spawn
        需要：team.yaml + Tier 2
```

**效益**：
- 移除 `GEMINI_API_KEY` 環境依賴
- 減少 `httpx` 呼叫（外部 API 請求降低）
- 22 files changed，淨減少 335 行程式碼

---

## 二、對話流程修正（5 個問題）

### P0 — `/mode` 指令 AttributeError crash

**根因**：`memory_commands.py cmd_mode` 存取 `tier_status.llm_ok`，
但 `TierStatus` 無此欄位 → 每次執行 `/mode` 必定 crash。

**修正**：`tier.py` 移除 `llm_ok`，Tier 編號重排，`cmd_mode` 對齊新欄位。

---

### P1 — `GET /api/agents` uptime/memory 永遠回傳 0

**根因**：`persistent_daemon.get_status()` 未回傳 `uptime_seconds / memory_mb / tasks_total`，
但 `agents.py list_agents()` 試圖讀取這三個欄位。

**修正**：整合 `psutil`（新增至 requirements.txt），
對每個存活 pid 讀取真實 uptime / RSS memory / output count。

---

### P1b — `allowed_users` 空值無警告且不讀 `.env`

**根因**：白名單只從 `team.yaml` 讀取，`team.yaml` 預設空列表，
啟動時無警告，任何人都能操作 Bot。

**修正**：
- `bootstrap.py` 優先讀 `.env` 的 `ALLOWED_USERS`（逗號分隔 int list）
- 空值時輸出 WARNING
- `/start` 指令顯示用戶 Chat ID 並提示如何加入白名單
- `config.py` 補 `idle_timeout_minutes` property（修復 health loop AttributeError）

---

### P2 — 動態 Agent Lazy Spawn 無進度通知

**根因**：使用者傳訊給 worker agent（coder/qa/ai-dev 等）時，
`send_message()` 觸發 lazy spawn 需 10-15s，使用者只看到 👀，無任何回饋。

**修正**：spawn 前透過 `get_channel().notify()` 推送「⏳ 正在啟動 {name}」通知。

---

### P3 — A2A reply_to 格式污染訊息本文

**根因**：`chat_send` 把 `[reply_to:xxx]` 前綴注入訊息字串，
Agent 不一定能正確解析，且污染原始訊息語意。

**修正**：改為結構化 header 行：
```
[A2A] from=pm-agent reply_to=pm-agent
原始訊息內容...
```
`[A2A]` 行獨立於本文，Agent SOUL.md 可明確識別 metadata。

---

## 三、TG 管理指令對齊（4 個問題）

### 問題一 — `/restart` 在常駐模式下無效

**根因**：`cmd_restart` 操作 `bot_data["agents"]` dict，
常駐模式下此 dict 為空（由 PersistentDaemon 管理）。

**修正**：改呼叫 `POST /api/agents/{id}/rotate`，並加 15s `asyncio.wait_for` timeout。

---

### 問題二 — `/stop` 未真正停止 Agent

**根因**：`stop_confirm` callback 只更新訊息文字，從未呼叫任何 API。

**修正**：改呼叫 `PATCH /api/agents/{id}/persistent {"persistent": false}`。

---

### 問題三 — `/costs` 呼叫不存在路徑

**根因**：`cmd_costs` 呼叫 `GET /api/admin/costs`（此端點不存在）。

**修正**：確認路徑正確（`admin_router` prefix `/api/admin` + `/costs`），加 error fallback。

---

### 問題四 — `/board` refresh 格式不符

**根因**：`refresh_board` callback 呼叫 `GET /api/issues`（flat list），
但 `fmt_board` 期望 kanban 分組格式。

**修正**：改呼叫 `GET /api/board`，展開 status key 轉 flat list 再傳入 `fmt_board`。

---

### 問題五 — 啟動 crash（cp950 UnicodeEncodeError）

**根因**：`tier.py print_tier_banner` 用 Python `print()` 輸出含 emoji 字串，
Windows cp950 編碼無法處理 → 啟動即 crash。

**修正**：改用 `sys.stdout.write` + `encode("ascii", errors="replace")` 輸出，全 ASCII 安全。

---

## 四、通知完整性修正

### TG 任務通知顯示 `#?`

**根因鏈**：
- `notifications.py on_task_completed` — 只讀 `issue_id`，無 title/agent_id
- `scheduler.py _emit_completed` — emit data 只有 `agent_id + job_name`，缺 `issue_id`
- `issues.py complete_issue` — emit data 只有 `issue_id + output`，缺 `title + assignee`

**修正**（三處同步）：
```python
# notifications.py — 完整格式
✅ 任務完成
📋 #a1b2c3d4 — 任務標題
🤖 agent-name
📝 產出摘要

# scheduler.py — 補 issue_id / title / output
# issues.py — emit 後先 SELECT，補帶 title + assignee
```

---

## 五、新增功能

### chat_trace.py — 對話軌跡追蹤

```python
# state/chat_trace.db（SQLite，7 天自動清理）
trace_id → user_input → target_agent → route_path → reply_summary → success
```

每次對話自動建立 trace，MCP reply 完成後標記成功，timeout 標記失敗。
`GET /api/chat/traces` 可查最近 20 筆。

### DB Migration 005

```sql
-- 修正 pending+assignee 狀態不一致
UPDATE issues SET status = 'assigned'
WHERE status = 'pending' AND assignee IS NOT NULL AND assignee != '';
```

### knowledge/shared wiki — 8 篇新增

analytics-methods / llm-integration-guide / market-research-methods /
project-management-guide / report-standards / testing-standards +
2 篇 raw（agent-management-guide / workshop-map）

---

## 六、API 驗證結果

服務啟動後對所有管理端點進行驗證（全部 200）：

| 端點 | 狀態 | 回傳 |
|------|------|------|
| `GET /api/agents` | ✅ 200 | list |
| `GET /api/board` | ✅ 200 | dict（kanban） |
| `GET /api/admin/costs` | ✅ 200 | dict |
| `GET /api/admin/sessions?limit=3` | ✅ 200 | list |
| `GET /api/admin/queue` | ✅ 200 | list |
| `PATCH /api/agents/{id}/persistent` | ✅ 200 | dict |
| `POST /api/agents/{id}/rotate` | ✅ 200（+15s timeout） | dict |

---

## 七、品質指標（優化後）

| 指標 | 優化前 | 優化後 |
|------|--------|--------|
| Drift Score | ~97/100 | ~97/100（維持）|
| smoke_test | 17 passed | 17 passed（維持）|
| Gemini 依賴 | 6 個模組 | 0 |
| Tier 數量 | 5（0-4）| 4（0-3）|
| TG 指令 API 對齊率 | ~60% | 100% |
| 啟動 crash（cp950）| ✅ 修復 | — |
| `/mode` crash | ✅ 修復 | — |
| TG 通知 `#?` | ✅ 修復 | — |
| lazy spawn 無通知 | ✅ 修復 | — |
| `allowed_users` 靜默空值 | ✅ 修復 | — |

---

## 八、待觀察 / 後續建議

| 項目 | 說明 | 優先 |
|------|------|------|
| A2A `[A2A]` header 解析 | 各 Agent SOUL.md 需加入解析規則，reply_to callback 才能可靠觸發 | P2 |
| `last_heartbeat` 欄位 | `get_status()` 目前回 None，待 heartbeat_loop 整合 | P3 |
| idle_timeout 動態 agent evict | `IDLE_TIMEOUT_MINUTES=10` 已設，驗證 worker 閒置後是否正確停止 | P2 |
| smoke_test 補 rotate/persistent | 新增的兩個 API endpoint 目前無對應測試 | P2 |

---

## 九、Commit 清單

| Commit | 說明 |
|--------|------|
| `ef02add` | refactor: remove Gemini/LLM dependency, simplify to Tier 0-3 |
| `f2bb801` | fix: read ALLOWED_USERS from .env + idle_timeout_minutes property |
| `467c0cd` | fix(dialogue-flow): resolve 5 issues in conversation routing |
| `00d64d8` | fix(tg-commands): align all admin commands with real API endpoints |
| `4e54882` | docs: update MEMORY.md + README — 2026-07-27 progress |
| `5f2a64d` | fix(notifications): task-notification-optimization |
| `069b942` | docs(ai-team-agent): closeout report + README rewrite |

---

## 十、pm-agent → leader-agent 更名（下午）

### 異動範圍
- `agents/pm-agent/` → `agents/leader-agent/`（git mv）
- `team.yaml` / `team-dev.yaml` / `team-ops.yaml`
- 8 個 agent TEAM.md、8 個 mcp.json allowed-targets
- 6 個 Python src 檔案、scheduler.yaml、README.md、smoke_test.py
- DB migration `006_rename_pm_to_leader.sql`

**smoke_test 結果：36 passed / 4 skipped ✅**

---

## 十一、對話測試 Debug（下午）—— kiro-cli 三層疊加問題

T01 測試（「你好，介紹一下團隊成員」）失敗，排查耗時約 2 小時，共發現 3 個疊加問題：

### 問題 1：`agent.json` `file://` 路徑解析錯誤（agent 無 SOUL.md）

**現象**：訊息送出，kiro-cli 有輸出，但 reply 永遠不回來。  
**根因**：kiro-cli 把 `file://` 路徑從 **json 檔所在目錄**（`.kiro/agents/`）計算，不是 cwd。

```
# 舊路徑（錯誤）
file://.kiro/steering/SOUL.md
→ 解析成：.kiro/agents/.kiro/steering/SOUL.md  ← File not found

# 新路徑（正確）
file://../steering/SOUL.md
→ 解析成：.kiro/steering/SOUL.md  ← OK
```

**影響**：所有 8 個 agent 的 SOUL.md 載入失敗，agent 沒有 system prompt，不知道要呼叫 `reply` tool。  
**修正**：`agents/*/\.kiro/agents/*.json` 全部從 `.kiro/` 改為 `../`。

---

### 問題 2：`claude-opus-4.6` 模型下架

**現象**：kiro-cli 靜默失敗，不回覆。  
**根因**：`~/.kiro/settings/cli.json` 的 `chat.defaultModel` 設為 `claude-opus-4.6`（已下架）。  
**可用模型**：`auto`（預設）/ `claude-sonnet-4.6` / `claude-opus-4.5` / `claude-haiku-4.5` 等。  
**修正**：`cli.json` 改為 `"chat.defaultModel": "auto"`。

---

### 問題 3：`Set-Content` 寫入 UTF-8 BOM（kiro-cli json parse 失敗）

**現象**：服務啟動 2 秒後 `admin-agent failed to start`，`leader-agent failed to start`。  
**根因**：PowerShell `Set-Content -Encoding UTF8` 預設加 BOM，kiro-cli JSON parser 報 "expected value at line 1 column 1"。  
**這是 MEMORY.md 已有記錄的老問題，但修正 cli.json 時再次觸發。**  
**修正**：用 Python `write_bytes()` 寫入，無 BOM。

```python
p.write_bytes(json.dumps(data, indent=2).encode('utf-8'))
```

### 修正後狀態
```
13:19:42 Instance admin-agent is ready ✅
13:19:55 Instance leader-agent is ready ✅
13:19:57 常駐 agents 就緒 (8/8) ✅
```

### 新增踩坑到 MEMORY.md
| 問題 | 原因 | 修正 |
|------|------|------|
| agent.json file:// 路徑錯誤 | kiro-cli 從 json 所在目錄（.kiro/agents/）解析，非 cwd | `file://.kiro/` → `file://../` |
| claude-opus-4.6 不可用 | 模型已下架，kiro-cli 靜默失敗 | cli.json defaultModel 改 auto |
| cli.json BOM（再次） | PowerShell Set-Content 加 BOM | Python write_bytes() 寫入 |
