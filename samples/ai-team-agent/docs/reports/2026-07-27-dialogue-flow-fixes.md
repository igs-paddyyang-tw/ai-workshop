# 對話流程與常駐狀況修正報告

**日期**：2026-07-27  
**版本**：commit pending  
**範圍**：自然語言對話流程、Persistent Daemon、TierStatus、A2A  

---

## 背景

對 ai-team-agent 自然語言對話流程與常駐 agent 狀況進行全面分析，發現 5 個問題，
本次修正全部納入同一個 commit。

---

## 問題清單與修正詳情

### P0 — `/mode` 指令 AttributeError crash

**問題**  
`memory_commands.py cmd_mode` 存取 `tier_status.llm_ok`，但 `TierStatus` dataclass
僅有 `tg_ok / cli_ok / team_ok` 三個欄位，無 `llm_ok`，呼叫 `/mode` 時必定 AttributeError。

**根因**  
`detect_tier()` 原設計只有 3 個 Tier，未考慮 LLM API key 作為獨立 Tier。
`cmd_mode` 在撰寫時超前引用了尚未定義的欄位。

**修正**（`src/runtime/tier.py`）
- `TierStatus` 新增 `llm_ok: bool = False`
- `detect_tier()` 偵測 `GEMINI_API_KEY` / `OPENAI_API_KEY`，有值則 `llm_ok=True, tier=2`
- Tier 編號重排：0=基礎 / 1=TG / 2=LLM / 3=kiro-cli / 4=Team
- `print_tier_banner()` 對應更新顯示文字

---

### P1 — `GET /api/agents` uptime/memory 永遠回傳 0

**問題**  
`agents.py list_agents()` 從 `daemon.get_status()` 讀取 `uptime_seconds / memory_mb / tasks_total`，
但 `persistent_daemon.get_status()` 回傳的 dict 不包含這三個欄位，導致 enriched 結果永遠是 0。

**根因**  
`get_status()` 最初只回傳基礎欄位（name/status/pid/crash_count），未設計 runtime metrics。

**修正**（`src/runtime/persistent_daemon.py`）
- 安裝 `psutil>=5.9.0`（加入 `requirements.txt`）
- `get_status()` 對每個存活 pid 呼叫 `psutil.Process`，讀取：
  - `uptime_seconds`：`time.time() - proc.create_time()`
  - `memory_mb`：`proc.memory_info().rss / 1024 / 1024`
  - `tasks_total`：process._output_count（輸出行數累計）
  - `last_heartbeat`：預留欄位（目前回 None）
- `NoSuchProcess / AccessDenied` 例外捕獲，不影響正常回傳

---

### P1b — `allowed_users` 空值無警告

**問題**  
`team.yaml access.allowed_users: []` 空列表時，白名單檢查形同關閉，任何人都能操作 Bot，
但啟動時沒有任何警告提示。

**修正**  
- `bootstrap.py`：allowed_users 為空時印出 `WARNING` log，提示填入 TG user_id
- `commands.py cmd_start`：使用者傳 `/start` 時，若不在白名單，附加提示顯示其 Chat ID
  及如何加入 `team.yaml` 的操作說明

---

### P2 — 動態 agent Lazy Spawn 無進度通知

**問題**  
使用者傳訊給 worker agent（coder/qa/ai-dev 等）時，`send_message()` 會先 lazy spawn，
啟動耗時 ~10–15s，期間使用者只看到 👀 reaction，沒有任何進度回報，體驗差。

**修正**（`src/runtime/persistent_daemon.py`）
```python
# lazy spawn 前通知使用者
await ch.notify(f"⏳ 正在啟動 {name}，請稍候...")
```
透過 `get_channel()` 取得目前的 TelegramChannel 實例，
在 start_instance() 阻塞前推送一條進度通知。

---

### P3 — A2A reply_to 格式污染訊息本文

**問題**  
`chat_send` 將 `reply_to` 以 `[reply_to:xxx]` 前綴注入訊息字串，
這個字串直接進入 agent 的訊息 context，Agent 不一定能正確解析，
且污染原始訊息格式，導致 A2A callback 機制難以可靠執行。

**修正**（`src/gateway/api/chat.py`）
改為結構化 header 行，獨立於訊息本文：
```
[A2A] from=pm-agent reply_to=pm-agent
原始訊息內容...
```
格式一致，Agent SOUL.md 可透過 `[A2A]` 前綴明確識別 metadata 行，
與訊息本文分離，不影響訊息語意。

---

## 修改檔案清單

| 檔案 | 修改內容 |
|------|---------|
| `src/runtime/tier.py` | 新增 `llm_ok` 欄位；Tier 重排為 0–4；`detect_tier` 偵測 LLM key |
| `src/runtime/persistent_daemon.py` | `get_status()` 補 uptime/memory/tasks；lazy spawn 加通知 |
| `src/gateway/api/chat.py` | A2A `reply_to` 改 `[A2A]` header 格式，不污染本文 |
| `src/gateway/telegram/handlers/commands.py` | `/start` 補白名單狀態提示 |
| `src/bootstrap.py` | allowed_users 空時輸出 WARNING |
| `requirements.txt` | 新增 `psutil>=5.9.0` |

---

## 驗證

```bash
# 語法驗證（全部通過）
python -c "
import runtime.tier as t
assert 'llm_ok' in t.TierStatus.__dataclass_fields__, 'llm_ok missing'
import runtime.persistent_daemon as d
import gateway.api.chat as c
import gateway.telegram.handlers.commands as cmd
print('All imports OK')
"
# 輸出：All imports OK

# psutil 安裝確認
python -c "import psutil; print('psutil', psutil.__version__)"
# 輸出：psutil 7.2.2
```

---

## 對話流程現況（修正後）

```
User (TG)
  │
  ├─ 白名單空 → bootstrap WARNING + /start 顯示 Chat ID 提示
  │
  ▼
handle_message()
  │
  ├─ @agent 或預設 pm-agent
  ├─ ChatTrace 建立
  │
  ▼
daemon.send_message(target, text)
  │
  ├─ STOPPED (動態 agent)
  │   ├─ 推送 "⏳ 正在啟動 {name}" 通知  ← 新增
  │   └─ start_instance() (~10–15s)
  │
  └─ RUNNING → _queue_worker → stdin pipe
       │
       └─ Agent MCP reply() → /api/chat/reply → TG 回覆
```

## 常駐狀態（team.yaml 定義）

| Agent | 模式 | 啟動時機 |
|-------|------|---------|
| admin-agent | 常駐 | 服務啟動立即 |
| pm-agent | 常駐 | 服務啟動立即 |
| coder-agent | 動態 | 第一次收訊息 |
| qa-agent | 動態 | 第一次收訊息 |
| ai-dev-agent | 動態 | 第一次收訊息 |
| market-agent | 動態 | 第一次收訊息 |
| data-agent | 動態 | 第一次收訊息 |
| report-agent | 動態 | 第一次收訊息 |

Health loop 每 30s 巡檢。崩潰最多重試 3 次（指數退避），超過進入 600s 冷卻。
動態 agent idle_timeout 分鐘到期後自動 evict（節省資源）。

---

## 待觀察

- A2A `[A2A]` header 格式需各 Agent SOUL.md 加入解析說明，才能觸發可靠的 callback
- `last_heartbeat` 欄位目前回 None，待 heartbeat_loop 整合後補上真實值

---

## 追加修正（2026-07-27 14:00）— MCP Reply 鏈路修復

### 問題診斷

MCP `reply()` tool 呼叫 `POST /api/chat/reply` 時回傳 **404 Not Found**，所有 Agent 無法回覆使用者。進一步診斷發現 7 個問題。

### 修正內容

| # | 問題 | 嚴重度 | 修正 |
|---|------|--------|------|
| 1 | **Chat Router 未註冊** | P0 | `router.py` 加入 `chat_router` import + include（prefix="/api/chat"） |
| 2 | **bootstrap.py sync/async 混用** | P0 | `_on_complete_with_db` / `_on_failed_with_db` / `_on_task_assigned` 改 `get_async_db()` + `await` + `conn.close()` |
| 3 | **DB 連線洩漏** | P1 | 同 #2，統一加 try/finally/close |
| 4 | **MCP stdio UTF-8 surrogate** | P1 | `mcp_stdio.py` 加入 `io.TextIOWrapper(encoding='utf-8', errors='replace')`（Windows only） |
| 5 | **allowed_users 為空** | P2 | 待使用者填入 team.yaml |
| 6 | **get_status() 私有屬性** | P3 | `_output_count` → `output_count` property |
| 7 | **殘留 test task** | P3 | 待下次啟動清理 |

### 修改檔案

| 檔案 | 變更 |
|------|------|
| `src/gateway/api/router.py` | +2 行（import + include chat_router） |
| `src/bootstrap.py` | 3 個 handler 改 async DB |
| `src/gateway/mcp_stdio.py` | +6 行 Windows UTF-8 pipe guard |
| `src/runtime/persistent_daemon.py` | 1 行 property 修正 |

### 驗證結果

```
POST /api/chat/reply  → 200 (was 404)
POST /api/chat/notify → 200 (was 404)
POST /api/chat/send   → 200 (was 404)
GET  /api/chat/traces → 200 (was 404)
bootstrap.py          → compile OK
mcp_stdio.py          → compile OK
persistent_daemon.py  → compile OK
```

### 注意

- UTF-8 surrogate 修正需**重啟平台**才生效（當前 session 仍用舊版 mcp_stdio 進程）
- One Pager 已產出：`docs/one-pagers/mcp-reply-hotfix.md`
