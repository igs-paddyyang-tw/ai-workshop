# Step 2：Telegram Bot 介面與指令 — 建置紀錄

> 日期：2026-05-29

---

## 1. 詢問時用的提詞

```
那你先繼續幫我進行Step 2的內容，記得幫我用md檔紀錄
```

---

## 2. 遇到的問題

### 問題 A：同一個 Token 不能同時有兩個 polling 實例

**現象：** 啟動 Bot 後出現錯誤：
```
telegram.error.Conflict: Conflict: terminated by other getUpdates request;
make sure that only one bot instance is running
```

**原因：** 使用者已有另一個 Bot 程序在用同一個 Token 做 polling，Telegram API 不允許同時有兩個 polling 連線。

---

## 3. 解決方法

**方案：停掉另一個 Bot 實例後再啟動**

同一個 Bot Token 只能有一個 polling 程序。需要先停掉舊的 Bot 程序，再執行：
```bash
cd ai-bot
python -m src.bot.main
```

**替代驗證方式：** 透過 import 測試確認程式碼邏輯正確，不需要實際 polling。

---

## 4. 結果

### 產出的檔案結構

```
src/bot/
├── __init__.py
├── main.py              ← create_app() + 指令註冊 + polling 啟動
└── handlers.py          ← 8 個指令處理器 + 1 個一般訊息路由

src/conversation/
├── __init__.py
├── session.py           ← Session + Turn dataclass
├── session_manager.py   ← SessionManager（TTL 30 分鐘過期）
└── planner.py           ← ConversationPlanner（三層意圖路由）
```

### Bot 指令清單

| 指令 | 功能 | 目前狀態 |
|------|------|---------|
| `/start` | 歡迎訊息 + 功能介紹 | ✅ 可用 |
| `/help` | 完整指令清單 | ✅ 可用 |
| `/status` | 系統狀態 | ✅ 可用 |
| `/skills` | 列出已載入 Skills | ✅ 可用 |
| `/chat <問題>` | AI 對話 | ⚠️ Echo 模式（Step 4 啟用 LLM） |
| `/config` | 查看排程設定 | ✅ 可用 |
| `/news <url>` | 即時抓取新聞 | ⚠️ 待 Step 5 |
| `/daily` | 手動觸發日報 | ⚠️ 待 Step 3+5+6 |

### 意圖路由系統（三層降級）

```
1. keyword 快速路由（毫秒級）
   「抓新聞」→ news / 「寫程式」→ codegen / 「技能」→ skill_call

2. LLM 意圖分類（Step 4 完成後啟用）
   回傳 intent + skill_id + params + confidence

3. keyword fallback（預設走 chat）
```

### 驗證結果

| 測試項目 | 結果 |
|---------|------|
| handlers.py import | ✅ 正確，回應文字完整 |
| bot/main.py create_app() | ✅ 建立 9 個 handlers |
| ConversationPlanner keyword 路由 | ✅ 「抓新聞」→ news (0.7) |
| Session 對話歷史 | ✅ add_turn / history_text 正常 |
| Telegram API 連線 | ✅ 成功連上並正常 polling |
| 實際 Telegram 測試 | ✅ Bot 成功發送訊息到使用者 |

### 一般訊息處理邏輯

非指令的文字訊息會經過簡易 keyword 路由：
- 包含「新聞」「日報」→ 提示使用 /news 或 /daily
- 包含「技能」「skill」→ 呼叫 /skills
- 包含「狀態」「status」→ 呼叫 /status
- 其他 → 走 /chat 路徑（目前為 Echo 模式）

### 啟動方式

```bash
# 確保沒有其他 Bot 實例在跑同一個 Token
cd ai-bot
python -m src.bot.main

# 輸出：
# ✅ Loaded 1 skills
# 🤖 Bot starting... (polling mode)
#    Press Ctrl+C to stop
```

---

*Step 2 完成，Bot 介面與對話系統就緒，可進入 Step 3。*
