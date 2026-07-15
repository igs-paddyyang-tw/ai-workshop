# Drift Report — Persistent Process Feature (v2)

> 產出日期：2026-07-15（第二次驗證）
> 前次報告：2026-07-14（v1, score=82）
> Spec: `docs/specs/persistent-process-spec.md`
> Design: `docs/designs/persistent-process-design.md`
> One-Pager: `docs/one-pagers/chat-routing-simplify.md`
> 驗證方法：逐檔比對 spec/design/one-pager 定義 vs 程式碼實作

---

## Overall Score: **91 / 100** (↑9)

| 維度 | 分數 | 變化 | 說明 |
|------|------|------|------|
| 1. API 端點 | **95** | ↑5 | 5 個端點全部存在且路徑正確；runtime/status 回傳結構仍缺少部分欄位 |
| 2. 功能需求覆蓋 | **88** | ↑8 | FR-1~FR-5 完整；FR-3 重啟/通知已修正；FR-4 task-drain 已加入；FR-6 仍未實作 |
| 3. Chat 路由 (One-Pager) | **92** | NEW | 核心路由、權限、typing、reaction、trace 全部到位；Bot Menu 數量偏差 |
| 4. MCP 工具路由 | **95** | ↑20 | 三個 tool 路由全部正確，走 /api/chat/send 而非 /api/agents/spawn |

---

## 上次報告後已修正項目 ✅

| 原 ID | 原嚴重度 | 修正內容 |
|--------|----------|----------|
| D4-1/D4-3 | ⚠️ Medium | `send_to_instance` 改走 `POST /api/chat/send`（透過 daemon.send_message），不再走 `/api/agents/spawn` |
| D2-1 | ⚠️ Medium | 崩潰重啟改為 `start_instance(name, skip_resume=False)`，正確帶 `--resume` 恢復 context |
| D2-2 | ⚠️ Medium | Health loop 超過 max_retries 後呼叫 `send_message("admin-agent", "⚠️ {name} 連續崩潰...")` |
| D2-3 | ⚠️ Medium | `stop_all()` 新增 30 秒 queue-drain 等待邏輯（檢查所有 queue 清空後再逐一 stop） |
| — | NEW | 新增 `POST /api/chat/send` endpoint + `SendPayload` model，agent 間訊息走 daemon |
| — | NEW | `delegate_task` 正確執行：`POST /api/issues` → `POST /api/chat/send` → `POST /api/chat/notify` |

---

## Dimension 1: API 端點 (Score: 95 ↑5)

### 驗證結果

| Spec 定義 | 實際路由檔案 | 完整路徑 | 狀態 |
|-----------|-------------|----------|------|
| `POST /api/chat/reply` (instance, text, summary) | `chat.py: ReplyPayload` + `@router.post("/reply")` | `/api/chat/reply` | ✅ |
| `POST /api/chat/notify` (text, from_agent, to_agent) | `chat.py: NotifyPayload` + `@router.post("/notify")` | `/api/chat/notify` | ✅ |
| `POST /api/chat/send` (target, message, from_agent) | `chat.py: SendPayload` + `@router.post("/send")` | `/api/chat/send` | ✅ NEW |
| `GET /api/chat/traces` (limit param) | `chat.py: @router.get("/traces")` | `/api/chat/traces?limit=20` | ✅ |
| `GET /api/agents/runtime/status` | `agents.py: @router.get("/runtime/status")` | `/api/agents/runtime/status` | ✅ |

### 回傳結構驗證

**POST /api/chat/send 實作：**
- 從 `request.app.state.persistent_daemon` 取得 daemon
- 呼叫 `daemon.send_message(body.target, body.message)`
- 回傳 `{"status": "sent"|"failed"|"no_daemon", "target": ...}`

**GET /api/agents/runtime/status 實作：**
- 回傳 `{"mode": "persistent", "instances": [{"name", "status", "pid", "crash_count", "last_activity"}]}`

### 剩餘 Drifts

| # | 嚴重度 | 說明 |
|---|--------|------|
| D1-1 | 💡 Low | Spec §9 定義的 `uptime_seconds`, `memory_mb`, `tasks_completed` 仍未出現在 runtime/status 回傳中 |
| D1-2 | 💡 Info | Design §11 定義的 `/api/agents/{id}/health` 未實作（非 spec 要求） |

---

## Dimension 2: 功能需求覆蓋 (Score: 88 ↑8)

### FR-1：常駐進程管理 ✅

| 需求 | 程式碼 | 狀態 |
|------|--------|------|
| start_instance / stop / restart | `persistent_daemon.py` 三方法齊備 | ✅ |
| kiro-cli `--legacy-ui --trust-all-tools` | `kiro_backend.py: build_command()` | ✅ |
| per-instance 啟動 | `start_all()` 遍歷 + stagger delay | ✅ |

### FR-2：stdin pipe 通訊 ✅

| 需求 | 程式碼 | 狀態 |
|------|--------|------|
| stdin 寫入 | `managed_process.py: send_input()` | ✅ |
| ring buffer 讀取 | `deque(maxlen=500)` + `_read_output()` | ✅ |
| pipe 保護 + drain timeout | `_pipe_broken` flag + `wait_for(drain(), 10)` | ✅ |
| 逾時標記失敗 | `messages.py: _timeout_guard()` 300s | ✅ |

### FR-3：健康檢查 + 自動重啟 ✅ (已修正)

| 需求 | 程式碼 | 狀態 |
|------|--------|------|
| `_global_health_loop` 30 秒巡檢 | ✅ `while True: await asyncio.sleep(30)` | ✅ |
| 崩潰自動重啟帶 --resume | ✅ `start_instance(name, skip_resume=False)` | ✅ 已修正 |
| 連續 3 次 → cooldown + 通知 admin | ✅ `send_message("admin-agent", "⚠️ ...")` | ✅ 已修正 |
| Error pattern 偵測 | ✅ `KiroBackend.detect_error()` + `FailureMemory` | ✅ |
| Rate limit soft-pause | ✅ 連續 3 次 rate_limit → 90s cooldown | ✅ |

### FR-4：Graceful Shutdown ✅ (已修正)

| 需求 | 程式碼 | 狀態 |
|------|--------|------|
| 停止接收新任務 | `bootstrap.py` 進入 shutdown → 不再 send | ✅ |
| 等待 queue 清空 (max 30s) | ✅ `stop_all()` 新增 deadline loop 檢查 `_msg_queue.empty()` | ✅ 已修正 |
| 發送 /quit 或 SIGTERM | `stop_instance()` → `/quit` → `kill()` | ✅ |
| 確認退出 | `kill()` 中 `wait_for(proc.wait(), 5)` | ✅ |

### FR-5：混合模式 ⚠️ 部分

| 需求 | 程式碼 | 狀態 |
|------|--------|------|
| `team.yaml` persistent: true/false | `InstanceConfig.persistent` 欄位存在 | ✅ |
| defaults.persistent 控制全域 | `TeamConfig.persistent` 從 yaml 讀取 | ✅ |
| 同一團隊混用 spawn + persistent | `bootstrap.py` 用全域 `team_config.persistent` 切換 | ⚠️ D2-4 |

### FR-6：Idle Eviction ❌ 未實作

| 需求 | 程式碼 | 狀態 |
|------|--------|------|
| 閒置 > timeout → 自動 kill | 無 eviction 邏輯 | ❌ |
| 下次任務時 respawn | 無 lazy respawn | ❌ |
| `idle_timeout_minutes` 設定欄位 | config.py / team.yaml 均無 | ❌ |

### 剩餘 Drifts

| # | 嚴重度 | 說明 |
|---|--------|------|
| D2-4 | 💡 Low | Per-instance persistent/spawn 混用邏輯未完成。bootstrap 以全域 flag 決策。 |
| D2-5 | 🔴 High | FR-6 Idle Eviction 完全未實作（Spec 明確要求） |

---

## Dimension 3: Chat 路由 — One-Pager 驗證 (Score: 92)

### 3.1 白名單權限

| 需求 | 程式碼 | 狀態 |
|------|--------|------|
| `handle_message` 非白名單被擋 | `messages.py`: `allowed = context.bot_data.get("allowed_users", [])` + 回覆 `🔒 需要白名單權限` | ✅ |
| `require_whitelist` decorator | `commands.py`: `@require_whitelist` 裝飾 /agents /board /costs /assign /stop /logs | ✅ |
| 顯示使用者 ID | ✅ 回覆含 `user_id` | ✅ |

### 3.2 訊息路由

| 需求 | 程式碼 | 狀態 |
|------|--------|------|
| 無 @ → pm-agent | `messages.py`: `target = "pm-agent"` (else 分支) | ✅ |
| @agent-name → 指定 agent | `re.match(r"@([\w-]+)\s*(.*)", text)` → `target = match.group(1)` | ✅ |
| 送出走 daemon.send_message | `daemon = context.bot_data.get("persistent_daemon")` → `daemon.send_message(target, message)` | ✅ |
| fallback 走 agents dict (spawn) | `agents.get(target)` → `agent_proc.send(message)` | ✅ |

### 3.3 即時回饋：typing loop + reaction

| 需求 | 程式碼 | 狀態 |
|------|--------|------|
| 收到訊息 → 👀 reaction | `_set_reaction(msg, "👀")` | ✅ |
| typing loop 每 4 秒 | `_typing_loop()`: `await bot.send_chat_action(...)` + `sleep(4)` | ✅ |
| reply 成功 → 👍 + 停止 typing | `complete_message()`: cancel task + `_set_reaction(msg, "👍")` | ✅ |
| 失敗/超時 → 👎 + 停止 typing | `_timeout_guard()` 300s → `complete_message(success=False)` | ✅ |

### 3.4 Trace Log

| 需求 | 程式碼 | 狀態 |
|------|--------|------|
| handle_message 建立 trace | `store.create(user_input=message, target_agent=target)` | ✅ |
| reply 完成寫入 summary + success | `chat.py /reply`: `get_trace_store().complete(trace_id, reply_summary=summary)` | ✅ |
| 超時寫入 success=false | `_timeout_guard()`: `get_trace_store().fail(trace_id, "超時")` | ✅ |
| send_to_instance 追加 route_path | `chat.py /notify`: `get_trace_store().append_route(trace_id, body.to_agent)` | ✅ |
| GET /api/chat/traces | `chat.py`: `get_trace_store().recent(limit=limit)` | ✅ |
| SQLite 7 天自動清理 | `ChatTraceStore.cleanup(max_age_days=7)` 方法存在 | ✅ |

### 3.5 /start 與 /help

| 需求 | 程式碼 | 狀態 |
|------|--------|------|
| /start 顯示 chat_id | `commands.py cmd_start()`: `f"你的 Chat ID：<code>{uid}</code>"` | ✅ |
| /help 分基本/進階兩段 | `cmd_help()`: 📖 基本指令 + 🔒 進階功能 兩區塊 | ✅ |

### 3.6 Bot Menu

| 需求 | 程式碼 | 狀態 |
|------|--------|------|
| One-pager 定義 6 項：start/status/help/agents/board/costs | `bootstrap.py` 只設定 3 項：start/status/help | ⚠️ D3-1 |

### 剩餘 Drifts

| # | 嚴重度 | 說明 |
|---|--------|------|
| D3-1 | ⚠️ Medium | One-pager 任務 3 定義 Bot Menu 6 項（start/status/help/agents/board/costs），實際只設 3 項。進階指令不在 Menu 中。 |

---

## Dimension 4: MCP 工具路由 (Score: 95 ↑20)

### mcp_stdio.py Tools → API 路由驗證

| Tool | 預期路由 | 實際程式碼 | 狀態 |
|------|----------|-----------|------|
| `reply` | `POST /api/chat/reply` (instance, text, summary) | `_tool_reply()` → `POST {base}/api/chat/reply` json=`{instance, text, summary}` | ✅ |
| `send_to_instance` | `POST /api/chat/send` (target, message, from_agent) | `_tool_send_to_instance()` → `POST {base}/api/chat/send` json=`{target, message, from_agent}` | ✅ 已修正 |
| `send_to_instance` 通知 | `POST /api/chat/notify` | 附帶 `POST /api/chat/notify` json=`{text: "📋 {from} → {to}", from_agent, to_agent}` | ✅ |
| `delegate_task` step 1 | `POST /api/issues` | `_tool_delegate_task()` → `POST {base}/api/issues` json=`{title, description, assignee}` | ✅ |
| `delegate_task` step 2 | `POST /api/chat/send` | → `POST {base}/api/chat/send` json=`{target, message, from_agent}` | ✅ |
| `delegate_task` step 3 | `POST /api/chat/notify` | → `POST {base}/api/chat/notify` json=`{text: "🔀 轉派...", from_agent, to_agent}` | ✅ |

### 端對端流程確認

```
Agent 呼叫 MCP reply(text, summary)
  → McpBridge._tool_reply()
  → POST /api/chat/reply
  → chat.py: ch.reply() 發 TG 訊息 + trace.complete()
  → TelegramChannel.reply() → complete_fn → 👍 reaction + 停止 typing
  ✅ 全鏈路正確
```

```
Agent 呼叫 MCP send_to_instance(instance, msg)
  → McpBridge._tool_send_to_instance()
  → POST /api/chat/send (target=instance, message=..., from_agent=self)
  → chat.py: daemon.send_message(target, msg)  ← 走 Daemon 不走 spawn
  → POST /api/chat/notify (進度通知)
  → TG 顯示 "📋 {from} → {to}"
  ✅ 全鏈路正確（已修正 spawn 問題）
```

### 剩餘 Drifts

| # | 嚴重度 | 說明 |
|---|--------|------|
| — | — | 無重大 drift。MCP 工具路由全部正確對齊。 |

---

## 彙整：所有剩餘 Drifts

| ID | 嚴重度 | 維度 | 問題摘要 |
|----|--------|------|----------|
| D1-1 | 💡 Low | API | `runtime/status` 回傳缺少 `uptime_seconds`, `memory_mb`, `tasks_completed` |
| D1-2 | 💡 Info | API | Design 定義的 `/api/agents/{id}/health` 未實作 |
| D2-4 | 💡 Low | FR | Per-instance persistent/spawn 混用邏輯未完成（bootstrap 用全域 flag） |
| D2-5 | 🔴 High | FR | FR-6 Idle Eviction 完全未實作 |
| D3-1 | ⚠️ Medium | Chat | Bot Menu 只有 3 項，one-pager 定義 6 項 |
| D3-2 | 💡 Low | Config | `idle_timeout_minutes` / `max_memory_mb` 欄位仍缺失 |
| D3-3 | 💡 Low | Config | `session_rotate_after` / `RestartPolicy` 未引用 |

---

## Recommendations

### 🔴 High Priority

1. **實作 FR-6 Idle Eviction**
   - `config.py` 加入 `idle_timeout_minutes: int = 30` / `max_memory_mb: int = 512`
   - `team.yaml` 加入 `defaults.idle_timeout_minutes: 30`
   - `_global_health_loop()` 加入：`if time.time() - state.last_activity > timeout → stop_instance()`
   - `send_message()` 加入 lazy respawn：status=STOPPED 時自動 `start_instance()`

### ⚠️ Medium Priority

2. **Bot Menu 補齊到 6 項** — `bootstrap.py` 的 `set_my_commands` 加入 agents/board/costs

### 💡 Low Priority

3. **runtime/status 補齊欄位** — 加 `uptime_seconds` (time.time() - start_time), `memory_mb` (psutil), `tasks_completed`
4. **Per-instance 混用** — bootstrap 遍歷 instances 依 `ic.persistent` 分流到 daemon 或 spawn
5. **引用 RestartPolicy** — health loop 從 config 讀取 max_retries / backoff
6. **Session Rotate** — Phase 3 待排

---

## 結論

相較 v1（82 分），本次驗證提升至 **91 分**。核心修正：

- ✅ MCP 工具路由完全對齊（send_to_instance 改走 /api/chat/send）
- ✅ 崩潰重啟正確帶 --resume
- ✅ Admin-agent 通知已加入
- ✅ Graceful shutdown 30s task-drain 已實作
- ✅ 新增 POST /api/chat/send endpoint（agent 間通訊）

剩餘唯一 High 級問題是 **FR-6 Idle Eviction**（Phase 3 交付項）。
其餘均為 Low/Info 級的欄位補齊或邊緣功能。

**系統目前可正常運行，核心功能鏈路完整。**
