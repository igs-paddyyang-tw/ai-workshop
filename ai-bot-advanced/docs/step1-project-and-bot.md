# Step 1：專案骨架 + Telegram Bot（10 min）

> 一句話建專案、一句話加 Bot，10 分鐘內 Bot 可回應指令。

---

## 1. 詢問時用的提詞

### 1.1 建立專案骨架

```
建立 ai-bot Web 專案，首頁使用 quickstart.html，
包含 health check API 和 Skill 自動發現機制
```

### 1.2 加入 Telegram Bot

```
加入 Telegram Bot，回應內容參考 bot-responses.md，
/start 回覆歡迎訊息，/help 列出指令，/status 顯示系統狀態，
並設定 Bot Menu 指令選單
```

### 1.3 設定環境變數

```bash
cp .env.example .env
# 填入：
#   TELEGRAM_BOT_TOKEN=你的token
#   GEMINI_API_KEY=你的key
```

---

## 2. 常見問題

### 問題 A：PowerShell 不支援 `&` 串接指令

**解法：** 改用 `;` 分隔，或用 `New-Item -ItemType Directory -Path <路徑> -Force`。

### 問題 B：同一個 Token 不能同時有兩個 polling 實例

**現象：** `telegram.error.Conflict: terminated by other getUpdates request`

**解法：** 停掉另一個 Bot 實例後再啟動。同一個 Bot Token 只能有一個 polling 程序。

---

## 3. 產出結構

```
ai-bot/
├── src/
│   ├── skills/
│   │   ├── base.py              ← BaseSkill 抽象介面
│   │   ├── registry.py          ← SkillRegistry（auto_discover + invoke）
│   │   └── internal/
│   │       └── echo.py          ← 範例 Skill
│   ├── bot/
│   │   ├── main.py              ← Bot 入口 + 指令註冊
│   │   └── handlers.py          ← 指令處理器
│   ├── conversation/
│   │   ├── session.py           ← 對話 Session 管理
│   │   └── planner.py           ← 意圖路由
│   └── server/
│       ├── main.py              ← FastAPI + lifespan
│       └── static/
│           └── index.html       ← quickstart.html 首頁
├── .env
├── .env.example
└── requirements.txt
```

---

## 4. Bot 指令清單

| 指令 | 功能 | 狀態 |
|------|------|------|
| `/start` | 歡迎訊息 | ✅ |
| `/help` | 指令清單 | ✅ |
| `/status` | 系統狀態 | ✅ |
| `/skills` | 列出 Skills | ✅ |
| `/chat` | AI 對話 | ⚠️ Echo（Step 3 啟用） |
| `/daily` | 觸發日報 | ⚠️ 待 Step 5 |

---

## 5. 驗證

| 測試項目 | 結果 |
|---------|------|
| `http://localhost:8000/` | ✅ 顯示首頁 |
| `http://localhost:8000/health` | ✅ `{"status": "ok"}` |
| 📱 Telegram `/start` | ✅ 歡迎訊息 |
| 📱 Telegram `/help` | ✅ 指令清單 |
| 📱 Telegram `/status` | ✅ 系統狀態 |

---

*Step 1 完成，Web + Bot 就緒，可進入 Step 2。*
