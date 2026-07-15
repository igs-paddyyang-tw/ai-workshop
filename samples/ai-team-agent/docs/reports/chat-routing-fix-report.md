# 對話路由修正報告

> 日期：2026-07-15 | 方案：A（統一 MCP reply 路徑）

## 問題摘要

常駐模式下對話訊息傳遞存在三條回覆路徑互相打架，導致：
- 重複回覆（MCP reply + stdout 截取同時推 TG）
- 零回覆（兩條路徑時序不一致，都未觸發）
- 單使用者綁定（`TelegramChannel._chat_id` 只設一次）
- Timeout 處理粗暴（300s 超時直接標失敗，無智慧判斷）
- A2A 無回報（Agent A → Agent B，B 完成後 A 不知道）
- Spawn 模式不等結果（fire-and-forget 造成回覆遺失）

---

## 修正內容

### 1. 移除 stdout 截取回覆機制（核心修正）

**檔案**：`src/runtime/persistent_daemon.py`

| 移除 | 說明 |
|------|------|
| `_wait_for_reply()` | 不再輪詢 stdout 等 `▸ Time:` 標記 |
| `_push_reply()` | 不再自動 POST `/api/chat/reply` |
| queue worker 等待邏輯 | 簡化為只負責 `send_input`，不截不推 |

**現在**：queue worker 只管投遞訊息到 stdin pipe，Agent 自行決定何時用 MCP `reply()` tool 回覆。

---

### 2. 消除常駐模式的重複 TG 推送

**檔案**：`src/bootstrap.py`

- `_on_agent_output` 的 `tg_reply_fn` 加 `if not persistent_daemon` 判斷
- 常駐模式回覆全由 MCP reply → `/api/chat/reply` → TelegramChannel 驅動
- Spawn 模式保留 callback（因為 spawn 沒有 MCP）

---

### 3. 多使用者 Routing（TelegramChannel 重構）

**檔案**：`src/gateway/api/chat.py`

| 改動 | Before | After |
|------|--------|-------|
| chat_id 解析 | 固定 `_chat_id` 單值 | `_resolve_chat_id()` — 指定 > pending > 預設 |
| configure 介面 | `(bot, chat_id, complete_fn)` | `(bot, chat_id, allowed_chat_ids)` |
| complete 機制 | 外部注入 callback | 內建直接呼叫 `complete_by_chat` |
| reply/notify | 無 chat_id 參數 | 新增 `chat_id` 參數支援多使用者 |

新增 helper：`get_latest_pending_chat_id()` — 從 pending messages 取最近的 chat_id。

---

### 4. 智慧 Timeout Guard

**檔案**：`src/gateway/telegram/handlers/messages.py`

| Before | After |
|--------|-------|
| 300s 硬超時 → 直接標失敗 | 300s 後偵測 agent 活動 → 活躍中則寬限 +120s |
| 無使用者通知 | 超時後通知使用者「可能還在處理」 |
| 無 trace 原因 | 標記「Agent 未用 reply tool 回覆」 |

---

### 5. A2A Callback（send_to_instance 回報鏈）

**檔案**：`src/gateway/mcp_stdio.py` + `src/gateway/api/chat.py`

- `send_to_instance` 現在自動帶 `reply_to: self.instance`
- `/api/chat/send` endpoint 新增 `reply_to` 欄位
- 訊息前綴注入 `[reply_to:agent-name]` metadata
- 目標 Agent 完成後可解析 metadata 並回報來源

---

### 6. Spawn 模式對齊（同步等待回覆）

**檔案**：`src/gateway/telegram/handlers/messages.py`

| Before | After |
|--------|-------|
| `asyncio.create_task(agent.send())` fire-and-forget | `await agent.send(message)` 同步等結果 |
| 回覆由 `_on_agent_output` callback 推 | 直接 `msg.reply_text(result)` |
| 走 pending + timeout guard 機制 | 獨立處理，完成即 return |

---

### 7. Agent Steering 補齊

**檔案**：3 個 `agents/*/\.kiro/steering/SOUL.md`

| Agent | 新增內容 |
|-------|---------|
| market-agent | `reply` 指示 + MCP tools 表格 + Output Marker + Critical Rules |
| data-agent | 同上 |
| report-agent | 同上 |

---

## 修正後的唯一回覆路徑

### 常駐模式（persistent）

```
User(TG) → handle_message
  → daemon.send_message(target, text)
    → queue → process.send_input(text) [stdin pipe]
      → Agent 思考...
        → Agent 呼叫 MCP reply(text, summary)
          → mcp_stdio.py → POST /api/chat/reply
            → TelegramChannel.reply(instance, text, chat_id)
              → bot.send_message(chat_id, text)
              → complete(chat_id) → reaction 👀→👍 + 停 typing
```

### Spawn 模式（fallback）

```
User(TG) → handle_message
  → await agent.send(text)
    → fork kiro-cli --no-interactive text
      → 等待 stdout + exit
        → msg.reply_text(result)
          → reaction 👀→👍
```

---

## 影響範圍

| 檔案 | 改動量 |
|------|--------|
| `src/runtime/persistent_daemon.py` | -55 行（移除），+15 行（簡化） |
| `src/bootstrap.py` | ~10 行修改 |
| `src/gateway/api/chat.py` | 全檔重寫（~170 行） |
| `src/gateway/telegram/handlers/messages.py` | ~60 行新增/修改 |
| `src/gateway/mcp_stdio.py` | ~5 行修改 |
| `agents/market-agent/.kiro/steering/SOUL.md` | +40 行 |
| `agents/data-agent/.kiro/steering/SOUL.md` | +40 行 |
| `agents/report-agent/.kiro/steering/SOUL.md` | +40 行 |

---

## 驗證清單

- [ ] 啟動常駐模式，TG 發訊息 → Agent 用 reply 回覆 → TG 收到 + reaction 👍
- [ ] @mention 指定 agent → 正確路由 + 回覆
- [ ] Agent A → send_to_instance(B) → B 完成 → reply 回使用者
- [ ] 300s 超時 → 使用者收到超時通知 + reaction 👎
- [ ] 多使用者（兩個 allowed_users）→ 各自收到自己的回覆
- [ ] Spawn 模式啟動 → TG 發訊息 → 同步等待 → 直接回覆
- [ ] market/data/report agent 被 @mention → 正確用 reply 回覆

---

## 後續建議

1. **End-to-end 整合測試**：需要實際啟動 bootstrap + TG bot 驗證
2. **Reply 超時告警**：如果 Agent 忘了 reply，可加 health loop 偵測「有 stdin 輸入但 5 分鐘無 reply tool call」→ admin-agent 告警
3. **A2A 結構化 callback**：目前用 metadata prefix `[reply_to:xxx]`，未來可改為結構化 JSON 欄位
4. **Gemini 快速回覆整合**：簡單問題走 Gemini 秒回路徑（如 GitHub 原版），複雜任務才走 Agent
