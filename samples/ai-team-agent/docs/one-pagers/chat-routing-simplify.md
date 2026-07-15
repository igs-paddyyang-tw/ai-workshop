---
title: "對話路由精簡化"
type: onepager
status: draft
created: 2026-07-15
language: zh-TW
---

# 對話路由精簡化

## 問題

1. handle_message 有 Gemini 分支 → 使用者不知道誰在回答
2. 常駐模式下 `agents` dict 為空 → 回覆「Agent 不可用」
3. 關鍵字路由與 /command 重複
4. 無權限控制 — 任何人都能操作
5. Bot Menu 指令過多；/start 沒顯示 chat_id

## 方案

### 對話路由（三條路徑）

```
TG 訊息
  ├─ /command → CommandHandler
  │    ├─ 公開：/start /status /help
  │    └─ 白名單：/agents /board /costs /assign /restart /stop
  ├─ @agent-name msg → 送指定 agent（白名單）
  └─ 自然語言 → pm-agent（白名單）
```

### 權限模型

| 層級 | 功能 | 誰 |
|------|------|-----|
| 公開 | /start /status /help | 所有人 |
| 白名單 | 對話、@mention、進階指令 | `access.allowed_users` |

---

## 執行計畫

### 任務清單

| # | 任務 | 檔案 | AC |
|---|------|------|-----|
| 1 | 重寫 handle_message | `messages.py` | 無@→pm-agent；@→指定agent；非白名單被擋 |
| 2 | /start 顯示 chat_id + /help 分段 | `commands.py` | /start 含 ID；/help 分基本/進階 |
| 3 | Bot Menu 精簡 + 進階指令白名單 | `bootstrap.py` | Menu 3 個（start/status/help）；進階需白名單手動輸入 |
| 4 | .env 精簡 | `.env` + `.env.example` | 移除未用項；分必要/可選兩區 |

### 任務 1：handle_message 重寫

**移除：** KEYWORD_ROUTES、is_complex、Gemini 回覆、_extract_conclusion、等待 agent 回覆的 blocking loop

**新邏輯：**

```python
async def handle_message(update, context):
    user_id = msg.from_user.id
    allowed = context.bot_data.get("allowed_users", [])
    if user_id not in allowed:
        await msg.reply_text(f"🔒 需要權限。你的 ID：{user_id}")
        return

    # @mention → 指定 agent
    if match := re.match(r"@([\w-]+)\s*(.*)", text, re.DOTALL):
        target, message = match.group(1), match.group(2).strip() or text
    else:
        target, message = "pm-agent", text

    # 送出（fire-and-forget，agent 用 MCP reply 回覆）
    daemon = context.bot_data.get("persistent_daemon")
    if daemon:
        ok = await daemon.send_message(target, message)
    else:
        agent = context.bot_data.get("agents", {}).get(target)
        ok = bool(agent and await agent.send(message))

    await _set_reaction(msg, "👀" if ok else "👎")
    if not ok:
        await msg.reply_text(f"⚠️ {target} 不可用")
```

### 任務 2：/start + /help

```python
# /start
async def cmd_start(update, context):
    uid = update.effective_user.id
    await update.message.reply_text(
        f"👋 歡迎！\n你的 Chat ID：`{uid}`\n輸入 /help 查看說明。",
        parse_mode="Markdown")

# /help
HELP_TEXT = """
📖 *基本指令*（所有人）
/start — 歡迎 + Chat ID
/status — 團隊狀態
/help — 本說明

🔒 *進階功能*（需白名單）
直接打字 → pm-agent 接收
@agent-name → 指定 agent
/agents /board /costs /assign /restart /stop
"""
```

### 任務  + 權限 wrapper

```python
# bootstrap.py — Menu 精簡
await tg_app.bot.set_my_commands([
    BotCommand("start", "歡迎"),
    BotCommand("status", "團隊狀態"),
    BotCommand("help", "使用說明"),
    BotCommand("agents", "Agent 列表"),
    BotCommand("board", "任務看板"),
    BotCommand("costs", "費用"),
])

# 權限 decorator
def require_whitelist(fn):
    async def wrapper(update, context):
        uid = update.effective_user.id
        if uid not in context.bot_data.get("allowed_users", []):
            await update.message.reply_text(f"🔒 需要權限。你的 ID：{uid}")
            return
        return await fn(update, context)
    return wrapper
```

### 任務 4：.env

```dotenv
# ═══ 必要 ═══
TELEGRAM_BOT_TOKEN=your-bot-token-here
API_PORT=33333

# ═══ 可選 ═══
# PLATFORM_API_KEYS=key:admin  # API RBAC（不設=開發模式全通）
```

移除：GEMINI_API_KEY / OPENAI_API_KEY / DATABASE_URL / GOOGLE_APPLICATION_CREDENTIALS

> 本版本所有 LLM 能力統一由 Kiro CLI（常駐 agent）提供，不直接呼叫 Gemini API。

---

## Agent 間互相對話

agent 用 MCP `send_to_instance("target-agent", msg)` 轉發。
不走 TG handler，直接 Daemon.send_message()。

## 回滾

```bash
git checkout HEAD -- src/gateway/telegram/handlers/messages.py \
  src/gateway/telegram/handlers/commands.py src/bootstrap.py .env .env.example
```

## 驗收

- [ ] 非白名單發訊 → 回覆「需要權限 + ID」
- [ ] 白名單無 @ → pm-agent 收到
- [ ] @coder-agent xxx → coder-agent 收到
- [ ] /start → 顯示 Chat ID
- [ ] /help → 基本/進階兩段
- [ ] /status → 所有人可用
- [ ] /assign → 非白名單被擋
- [ ] Bot Menu 3 個指令（start/status/help）
- [ ] .env.example 精簡
- [ ] 收到訊息 → 👀 reaction + typing 狀態
- [ ] agent reply 成功 → 👍 reaction + 停止 typing
- [ ] agent 失敗/超時 → 👎 reaction + 停止 typing
- [ ] 轉派時 TG 收到進度通知

---

## 進度回饋機制（任務 5-7）

### 使用者體驗

```
使用者發訊 → 👀 + typing...
         → 📋 pm-agent 正在分析...
         → 🔀 已轉派給 coder-agent
         → ⏳ coder-agent 執行中...
         → ✅ reply 內容 + 👍
```

### Reaction 狀態機

| 階段 | Reaction | typing |
|------|----------|--------|
| 收到訊息 | 👀 | 開始（每 4 秒續傳） |
| agent reply 成功 | 👍（覆蓋） | 停止 |
| 失敗/超時 5 分鐘 | 👎（覆蓋） | 停止 |

### 進度通知觸發

| MCP Tool 被呼叫 | TG 通知 |
|-----------------|---------|
| `send_to_instance(target, msg)` | 📋 {from} → {target} |
| `delegate_task(target, task)` | 🔀 轉派 {target}：{task 前 30 字} |
| `reply(text)` | 直接回覆 + 👍 + 停止 typing |

### 任務清單（追加）

| # | 任務 | 檔案 |
|---|------|------|
| 5 | typing loop + message_id 追蹤 | `messages.py` |
| 6 | MCP bridge 推送 TG 通知 | `mcp_stdio.py` |
| 7 | TG notify API + reaction 更新 | `api/router.py` + bootstrap |

---

## Chat Trace Log（任務 8）

### 目標

記錄每次對話的摘要軌跡，追蹤：誰問了什麼 → 誰處理 → 結果是否成功。
不存完整內容，只存摘要重點。由 Agent 在 reply 時順便整理。

### 資料結構

```
trace_id | timestamp | user_input_summary | target_agent | route_path | reply_summary | success
---------|-----------|--------------------|--------------| -----------|---------------|--------
abc123   | 10:30:01  | 幫我分析競品       | pm-agent     | pm→market  | 已產出報告     | ✅
def456   | 10:35:22  | @coder 加分頁      | coder-agent  | coder      | PR 已開        | ✅
ghi789   | 10:40:15  | 部署到 prod        | pm-agent     | pm→coder   | 超時           | ❌
```

### 寫入時機

| 事件 | 寫入欄位 |
|------|----------|
| handle_message 收到 | trace_id, timestamp, user_input_summary (前 50 字), target_agent |
| send_to_instance / delegate_task | route_path 追加 |
| reply() 被呼叫 | reply_summary (Agent 整理, 前 80 字), success=true |
| 超時 5 分鐘 | success=false |

### Agent 整理摘要

MCP `reply(text, summary)` 新增 optional `summary` 參數：
- Agent 回覆時順手附上一句摘要（≤80 字）
- 若未附，系統取 reply text 前 80 字作為 fallback

### 儲存

- SQLite `state/chat_trace.db` — 一張 `traces` 表
- 保留 7 天，超過自動清理

### 查詢

- `GET /api/chat/traces?limit=20` — 最近 20 筆
- `/logs` TG 指令可顯示最近對話軌跡

### 任務清單

| # | 任務 | 檔案 |
|---|------|------|
| 8a | ChatTrace model + SQLite | `src/gateway/chat_trace.py`（新增） |
| 8b | handle_message 寫入 trace | `messages.py` |
| 8c | reply endpoint 寫入 summary + success | `api/chat.py` |
| 8d | timeout 寫入 success=false | `messages.py` |
| 8e | GET /api/chat/traces endpoint | `api/chat.py` |
| 8f | MCP reply 加 optional summary 參數 | `mcp_stdio.py` |
