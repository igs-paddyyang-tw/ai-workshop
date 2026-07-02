# 🚀 AI Bot Workshop — 快速上手指南

> 50 分鐘建立你的第一個 AI Telegram Bot，具備意圖路由 + Gemini 即時對話 + 新聞技能。

**作者：** paddyyang
**更新：** 2026-06-22

---

## 🎯 上課目標（50 分鐘）

| 時間 | 動作 | 你做什麼 | Script 做什麼 |
|------|------|---------|-------------|
| 0-5 min | 環境確認 | clone skills + 確認 Python | ark-env-doctor 檢查 |
| 5-15 min | 一鍵建構 | 執行 `build_agent.py my-bot` | 產出完整 Bot 專案 |
| 15-25 min | 設定啟動 | venv + pip + 填 .env | （唯一手動步驟） |
| 25-35 min | TG 實測 | `/start`、問問題、「今天新聞」 | Planner 路由 → 各 Skill |
| 35-50 min | 理解架構 | 看意圖路由流程圖 | — |

### 完成度分級

```
🏆 快速組（35 min 內全完成）
   → Gemini 秒回 + 新聞 Skill 觸發 + 理解路由架構

✅ 標準組（大多數人）
   → Bot 啟動 + /start 有回應 + Gemini 能對話

🎯 保底組（至少完成這個）
   → build_agent.py 執行成功 + Bot 回覆 /start
```

---

## 你需要準備的東西

| 項目 | 說明 |
|------|------|
| Python 3.12+ | https://python.org |
| Git | https://git-scm.com |
| Telegram 帳號 | @BotFather 建立 Bot |
| Gemini API Key | https://aistudio.google.com/apikeys（免費） |

---

## Step 0：環境準備

```bash
python3 --version    # 需要 3.12+
git clone https://github.com/igs-paddyyang-tw/ark-agent-skills .kiro/skills/
```

---

## Step 1：一鍵建構 Bot 專案

```bash
python3 .kiro/skills/ark-agent-builder/scripts/build_agent.py my-bot
```

### 產出內容

```
my-bot/
├── start_bot.py           ← 一鍵啟動
├── src/
│   ├── bot/
│   │   ├── main.py        ← Bot 入口
│   │   ├── handlers.py    ← 指令 + 自然語言處理
│   │   └── planner.py     ← 意圖路由（核心）
│   ├── llm/
│   │   └── gemini_chat.py ← Gemini API 即時對話
│   └── skills/
│       └── internal/
│           ├── echo.py    ← 回聲測試
│           └── news.py    ← 新聞技能
├── .env.example
└── requirements.txt
```

---

## Step 2：設定環境與啟動

### 2.1 建立 venv + 安裝依賴

```bash
cd my-bot
python3 -m venv .venv
source .venv/bin/activate    # Linux/Mac
# .venv\Scripts\activate     # Windows
pip install -r requirements.txt
```

### 2.2 取得 Token & Key

| 項目 | 取得方式 |
|------|---------|
| Telegram Bot Token | Telegram 找 `@BotFather` → `/newbot` → 複製 Token |
| Gemini API Key | https://aistudio.google.com/apikeys → Create API Key |

### 2.3 填入 .env
```bash
cp .env.example .env
```

編輯 `.env`：
```
TELEGRAM_BOT_TOKEN=你的bot_token
GEMINI_API_KEY=你的gemini_key
```

### 2.4 啟動 Bot

```bash
python start_bot.py
```

看到 `✅ Bot 已啟動，開始 polling...` 表示成功。

---

## Step 3：Telegram 實測

### 基本指令

| 📱 你發送 | Bot 回應 |
|-----------|---------|
| `/start` | 歡迎訊息 + 功能介紹 |
| `/help` | 指令清單 |

### Gemini 即時對話（1-3 秒回應）

| 📱 你發送 | Bot 回應 |
|-----------|---------|
| `什麼是 Python？` | Gemini AI 即時回答 ✅ |
| `幫我寫 hello world` | AI 產出程式碼 |

### 新聞技能觸發
| 📱 你發送 | Bot 回應 |
|-----------|---------|
| `今天新聞` | 新聞摘要（news skill 觸發）✅ |
| `最新科技消息` | 同上（關鍵字路由） |

---

## 🧠 教學焦點：意圖路由架構

```
使用者訊息
    │
    ▼
┌─────────┐
│ Planner │ ← 意圖分類（關鍵字 + LLM）
└────┬────┘
     │
     ├─── 一般對話 ──→ Gemini Chat（秒回）
     │
     ├─── 「新聞」 ──→ News Skill（爬蟲 + 摘要）
     │
     └─── 「/指令」 ──→ 指令 Handler（echo / help）
```

### Planner 路由邏輯（核心概念）

```python
# src/bot/planner.py
async def route(message: str):
    if message.startswith("/"):
        return "command"           # 指令 Handler
    if any(kw in message for kw in ["新聞", "news", "今天"]):
        return "skill:news"        # News Skill
    return "gemini_chat"           # Gemini 即時對話
```

> 💡 **這就是所有 AI Agent 的核心** — 理解意圖、路由到對的能力。
> ChatGPT、Claude 內部也是這個架構的複雜版本。

---

## ⚠️ 常見問題

| 錯誤 | 原因 | 解法 |
|------|------|------|
| `No module named 'telegram'` | 沒在 venv 中 | `source .venv/bin/activate` + `pip install -r requirements.txt` |
| Bot 沒回應 | Token 錯 / 沒啟動 | 確認 `.env` 正確 + `python start_bot.py` 有跑 |
| `Gemini API error 429` | 超過免費額度 | 等 1 分鐘重試（免費 60 req/min） |
| `Gemini API error 403` | API Key 無效 | 重新到 aistudio.google.com 產生 |
| `Conflict: terminated by other getUpdates` | 多個 Bot 實例 | 關掉其他 terminal 再啟動 |

---

## 回家自我練習

- 修改 `planner.py` 加入新路由規則（天氣、翻譯）
- 在 `src/skills/internal/` 新增自訂 Skill
- 調整 Gemini system prompt 改變 Bot 個性

---

## 🔜 下堂預告：Skills 開發（Workshop 02）

### 你的 Bot 能回話了，但只有 echo 和新聞兩個技能。

試試看在 Telegram 要求 Bot 做更多事：
```
幫我翻譯這段英文
幫我查天氣
幫我做程式碼審查
```

**你會發現：** Bot 能力有限 → 需要更多 Skill。

### 02 解決什麼？

| 01 你遇到的問題 | 02 怎麼解決 |
|----------------|------------|
| 只有 echo + news 兩個硬編碼技能 | Spec-Driven 開發無限新 Skill |
| 加功能要手寫 + 猜測需求 | 拷問設計 → 產出規格 → 依 Spec 實作 |
| 品質沒保障 | Code-Spec 驗證確保一致性 |
| 技能無法複用 | Skill 標準化，團隊共用 |

### 02 長什麼樣？

```
拷問設計 → 產出 Spec → 依 Spec 實作 → 驗證一致性 → Ship
```

> 📌 你在 01 做的一切不會白費——02 教你用 Spec-Driven 方式開發新 Skill，讓 Bot 能做更多事。

---

## 教材包檔案

| 檔案 | 說明 |
|------|------|
| `QUICKSTART.md` | 本文件（50 分鐘快速版） |
| `agent-build-guide.md` | 完整教學（5 步驟） |
| `bot-responses.md` | Bot 回應範本 |
| `soul-example.md` | Soul 設定範例 |
| `quickstart.html` | HTML 版首頁 |

---

*作者：paddyyang ｜ 更新：2026-06-22*
