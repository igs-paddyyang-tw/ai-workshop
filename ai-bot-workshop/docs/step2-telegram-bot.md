# Step 2：Telegram Bot 介面與指令

> 使用 Skill：`ark-chatbot-generator`
> 觸發語句：「加入 Telegram Bot，回應內容參考 bot-responses.md」

---

## 1. 詢問時用的提詞

```
加入 Telegram Bot，回應內容參考 bot-responses.md，
/start 回覆歡迎訊息，/help 列出指令，/status 顯示系統狀態，
並設定 Bot Menu 指令選單
```

---

## 2. 常見問題

### 問題 A：同一個 Token 不能同時有兩個 polling 實例

**現象：** `telegram.error.Conflict: terminated by other getUpdates request; make sure that only one bot instance is running`

**原因：** 已有另一個 Bot 程序在用同一個 Token 做 polling。

**解法：** 停掉舊的 Bot 程序，再啟動新的。同一個 Bot Token 只能有一個 polling 連線。

---

## 3. 產出結構

```
src/bot/
├── __init__.py
├── main.py              ← create_app() + 指令註冊 + graceful shutdown
└── handlers.py          ← 8 個指令處理器 + 一般訊息路由

src/conversation/
├── __init__.py
├── session.py           ← Session + Turn dataclass
├── session_manager.py   ← SessionManager（TTL 30 分鐘過期）
└── planner.py           ← ConversationPlanner（三層意圖路由）
```

---

## 4. Bot 指令清單

| 指令 | 功能 | 狀態 |
|------|------|------|
| `/start` | 歡迎訊息 + 功能介紹 | ✅ 可用 |
| `/help` | 完整指令清單 | ✅ 可用 |
| `/status` | 系統狀態 | ✅ 可用 |
| `/skills` | 列出已載入 Skills | ✅ 可用 |
| `/chat <問題>` | AI 對話 | ⚠️ Echo 模式（Step 4 啟用） |
| `/config` | 查看排程設定 | ✅ 可用 |
| `/news <url>` | 即時抓取新聞 | ⚠️ 待 Step 5 |
| `/daily` | 手動觸發日報 | ⚠️ 待 Step 6 |

---

## 5. Bot Menu 設定

Bot 啟動時自動呼叫 `set_my_commands()` 設定 Telegram 指令選單：

```python
from telegram import BotCommand

BOT_COMMANDS = [
    BotCommand("start", "歡迎訊息 + 功能介紹"),
    BotCommand("help", "完整指令清單"),
    BotCommand("status", "系統狀態"),
    BotCommand("chat", "與 AI 對話"),
    BotCommand("skills", "列出已載入 Skills"),
]

async def post_init(application) -> None:
    await application.bot.set_my_commands(BOT_COMMANDS)
```

> 💡 設定後使用者在 Telegram 輸入 `/` 就會彈出指令選單。

---

## 6. 意圖路由系統（三層降級）

```
1. keyword 快速路由（毫秒級，不呼叫 LLM）
   「抓新聞」→ news / 「寫程式」→ codegen / 「技能」→ skill_call

2. LLM 意圖分類（Step 4 完成後啟用）
   回傳 intent + skill_id + params + confidence

3. keyword fallback（預設走 chat）
```

| 意圖 | 觸發 | 路由目標 |
|------|------|---------|
| chat | 一般對話 | llm_cli（chat 模式） |
| skill_call | 呼叫 Skill | registry.invoke() |
| news | 新聞相關 | news_scraper |
| unknown | 無法分類 | llm_cli（chat fallback） |

---

## 7. 環境變數

```bash
TELEGRAM_BOT_TOKEN=your_token
```

---

## 8. 驗證

```bash
python -m src.bot.main
```

| 測試項目 | 結果 |
|---------|------|
| 📱 Telegram 輸入 `/` | ✅ 彈出指令選單 |
| 📱 `/start` | ✅ 收到歡迎訊息 |
| 📱 `/help` | ✅ 收到指令清單 |
| 📱 `/status` | ✅ 收到系統狀態 |
| 📱 `/skills` | ✅ 列出已載入 Skills |

---

*Step 2 完成，Bot 介面與對話系統就緒，可進入 Step 3。*
