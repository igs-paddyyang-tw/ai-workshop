# TG 訊息介面優化報告

**日期**：2026-07-27  
**範圍**：`/start` / `/status` / `/help` 三個核心 TG 指令  
**commit**：待 push

---

## 背景

測試自然語言對話期間，發現三個核心指令的資訊量不足，難以快速判斷系統狀態。

---

## 一、`/start` 優化

### 優化前

```
🤖 Ark Agent Platform

一個由 AI Agent 組成的專案團隊，常駐運行。
...（靜態文字介紹）...

你的 Chat ID：937896656
```

**問題**：
- 無版本號，無法確認是哪個版本
- 常駐/動態 agent 無區分
- Chat ID 不突出，白名單狀態不明確

### 優化後

```
🤖 Ark Agent Platform  v1.0.0
━━━━━━━━━━━━━━━━━━━━━━━
📋 8-agent Team | Tier 3 | model: auto
👤 Chat ID：937896656  ✅ 已授權

📌 系統摘要
• 常駐：admin-agent, leader-agent
• 動態：6 workers（按需啟動）
• 指令入口：leader-agent

🗣️ 使用方式
• 直接打字 → leader-agent 分析並派工
• @agent-name 訊息 → 指定特定 agent
• /help → 完整指令說明
• /status → 平台與 Agent 即時狀態
```

**改善點**：
- 版本號 `v1.0.0`（`APP_VERSION` 常數）
- Tier 等級、model 設定即時顯示
- Chat ID + 授權狀態同一行，一眼判斷
- 常駐/動態 agent 從 `daemon.config` 動態取得
- 未授權時提示如何加入 `ALLOWED_USERS`

---

## 二、`/status` 優化

### 優化前

```
🤖 Agent Team Status
━━━━━━━━━━━━━━━━━━━
⚙️ admin-agent     │ 🟢 idle
🧠 leader-agent    │ 🟢 idle
💻 coder-agent     │ 🟢 idle
...
━━━━━━━━━━━━━━━━━━━
📊 完成 0 │ 進行中 0
💰 $0.00
```

**問題**：
- 沒有主程式（API / TG Bot / Scheduler）狀態
- 常駐與動態 agent 無區分
- 無 uptime / memory 資訊

### 優化後

```
⚙️ 平台狀態
━━━━━━━━━━━━━━━━━━━
🟢 API      port 33333 | 🟢 正常
🟢 TG Bot   已連線
🟢 Scheduler  運行中
💰 今日費用 $0.000 / $15.0

🤖 Agent 狀態
━━━━━━━━━━━━━━━━━━━
常駐（2）
  ⚙️ admin-agent      🟢 idle    2h15m | 607MB
  🧠 leader-agent     🟢 idle    2h13m | 608MB

動態（6）
  💻 coder-agent      ⏸️ 待機
  🧪 qa-agent         ⏸️ 待機
  🤖 ai-dev-agent     ⏸️ 待機
  ...（3 更多）

📊 今日　完成 0 | 進行中 0
```

**改善點**：
- **平台區塊**：API health / TG Bot / Scheduler / 今日費用
- **Agent 區塊**：常駐/動態分組顯示
- **常駐 agent**：顯示 uptime（2h15m）和 memory（607MB）
- **動態 agent**：顯示 stopped → `⏸️ 待機`，啟動中 → `🟡 starting`
- 費用上限從 `/api/admin/costs/budget` 動態取得

---

## 三、`/help` 優化

### 優化前

```
📖 基本指令（所有人）
/start — 歡迎 + Chat ID
/status — 團隊狀態
/help — 本說明

🔒 進階功能（需白名單）
直接打字 → leader-agent 接收
/agents — Agent 列表
/board — 任務看板
...
```

**問題**：
- 自然語言對話和 @mention 只有一行，不清楚用法
- 指令沒有參數說明
- 未授權使用者看到全部進階指令說明（無意義）

### 優化後

```
📖 Ark Agent Platform 使用說明
━━━━━━━━━━━━━━━━━━━━━━━

🌐 基本指令（所有人）
/start  — 系統資訊、版本、Chat ID
/status — 平台狀態 + Agent 運行狀況
/mode   — 查看當前 Tier 等級
/help   — 本說明

🔒 對話（授權後）
  直接打字           → leader-agent 接收分派
  @agent-name 訊息  → 指定特定 agent

📋 任務管理
  /assign <任務描述>  → 建立任務並選指派對象
  /board             → 看板（pending/doing/done）
  /queue             → 待處理佇列

🤖 Agent 管理
  /agents            → Agent 列表（可點擊查詳情）
  /logs <agent_name> → 最近執行記錄
  /restart <agent|all> → 重啟 agent
  /stop <agent_name>  → 停止 agent

💰 監控
  /costs             → 費用報告（今日/歷史）
  /recall <關鍵字>   → 查詢 leader-agent 記憶
```

**改善點**：
- 未授權使用者只看到基本指令，不顯示進階（減少困惑）
- 自然語言 + @mention 有專屬說明區塊
- 每個指令補上 `<參數>` 格式
- 按功能分組：對話 / 任務管理 / Agent 管理 / 監控
- 新增 `/mode` 到基本指令（無需授權）

---

## 四、實作細節

### 修改檔案

| 檔案 | 修改範圍 |
|------|---------|
| `src/gateway/telegram/handlers/commands.py` | `cmd_start` / `cmd_status` / `cmd_help` 全部重寫 |

### 新增 APP_VERSION 常數

```python
APP_VERSION = "1.0.0"
```

### `cmd_status` 資料來源

| 資訊 | API 來源 |
|------|---------|
| API health | `GET /api/health` |
| 費用 | `GET /api/admin/dashboard/stats` |
| 費用上限 | `GET /api/admin/costs/budget` |
| Agent 狀態 | `GET /api/agents` |
| Uptime / Memory | `GET /api/agents/runtime/status` |

### `cmd_start` 動態資料來源

| 資訊 | 來源 |
|------|------|
| 版本號 | `APP_VERSION` 常數 |
| Tier | `bot_data["tier_status"].tier` |
| 常駐/動態清單 | `daemon.config.instances` |
| 授權狀態 | `bot_data["allowed_users"]` |

---

## 五、向後相容

- `fmt_status()` 原函式保留（未刪除），其他地方若有引用不受影響
- `/status` 新版完全替代舊版，不需要遷移

---

## 六、待優化（未來）

| 項目 | 說明 |
|------|------|
| `/start` 版本號 | 改從 git tag 或 `pyproject.toml` 動態讀取 |
| `/status` 重新整理按鈕 | 加 InlineKeyboard refresh 按鈕 |
| `/help` 多語言 | 支援英文版 `/help en` |
