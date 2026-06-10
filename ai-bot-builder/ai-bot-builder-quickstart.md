# ⚡ AI Bot Builder — 一句話建 Bot 速成指南

> 一句提詞，全自動產出完整 Telegram AI Bot。不需逐步操作，Skill 直接建好整個專案。

**作者：** paddyyang
**日期：** 2026

**操作位置圖示說明：**
- 📝 = 在 **AI IDE 聊天框**（Kiro / Antigravity）輸入，觸發 Skill 產出程式碼
- 📱 = 在 **Telegram 聊天窗**，對你的 Bot 發送訊息
- 💻 = 在**終端機 / 命令列**執行指令

---

## 📦 教材包取得

```bash
# 下載教材包（含完整可運行專案）
git clone https://github.com/igs-paddyyang-tw/ai-bot-builder-workshop.git
```

或從講師提供的連結下載 `.7z` 壓縮檔解壓即可。

```
ai-bot-builder/
├── ai-bot-builder-quickstart.md ← 本文件（快速上手指南）
├── ai-bot-builder-quickstart.html ← HTML 版（可瀏覽器開啟）
├── README.md                    ← 目錄說明
└── news-bot/                    ← 完整可運行專案
    ├── src/                     ← 全部程式碼
    ├── config/                  ← 設定檔
    ├── .env.example             ← 環境變數範本
    ├── requirements.txt         ← Python 依賴
    ├── start.bat                ← Windows 啟動
    └── README.md                ← 專案說明
```

---

## 🎯 課程目標（1 堂 × 30 分鐘）

### 前提條件

- ✅ 已安裝 Python 3.12+、Git、Node.js 20+
- ✅ 已有 Telegram 帳號 + 從 @BotFather 取得 Bot Token
- ✅ 已有 Gemini API Key（https://aistudio.google.com/apikeys）
- ✅ 已安裝 AI IDE（Kiro 或 Antigravity）

### 時間分配

| 時間 | 步驟 | 你做什麼 | 產出 |
|------|------|---------|------|
| 0-5 min | Step 0 | clone skills + 確認環境 | 環境就緒 |
| 5-10 min | Step 1 | 📝 一句話建整個專案 | 完整 Bot 專案骨架 |
| 10-15 min | Step 2 | 💻 安裝 + 設定 .env | 依賴安裝完成 |
| 15-20 min | Step 3 | 💻 啟動 Bot + 📱 測試指令 | Bot 上線 |
| 20-25 min | Step 4 | 📱 自然語言對話 | AI 即時回應 |
| 25-30 min | Step 5 | 📱 /daily 觸發日報 | 科技日報 HTML 🎉 |

### 完成標準

```
✅ Bot 回應 /start /skills
✅ 自然語言訊息 → Agent CLI 回答
✅ /daily → 產出科技日報 HTML 卡片
```

---

## Step 0：環境準備（5 min）

### 取得 Skills

```bash
# Kiro 使用者
git clone https://github.com/igs-paddyyang-tw/ark-kiro-skills .kiro/skills/

# Antigravity 使用者
git clone https://github.com/igs-paddyyang-tw/ark-kiro-skills .agents/skills/
```

### 確認環境

**📝 在 AI IDE 聊天框輸入：**

```
檢查我的開發環境
```

✅ 全部通過即進入 Step 1。

---

## Step 1：一句話建 Bot 專案（5 min）

> 🎯 核心步驟！一句提詞產出整個可運行專案。

**📝 在 AI IDE 聊天框輸入：**

```
ark-ai-bot-builder，專案名稱 news-bot
```

### 提詞拆解

```
ark-ai-bot-builder     → 觸發 Skill 名稱（AI IDE 用這個找到對應 Skill）
專案名稱 news-bot      → Skill 參數（決定產出資料夾名稱）
```

**完整格式：**
```
ark-ai-bot-builder，專案名稱 {name}[，stages {n-m}][，llm {backend}]
```

### ark-ai-bot-builder 六階段

| Stage | 產出內容 | 何時用 |
|-------|---------|--------|
| 1 | BaseSkill + Registry + echo | 只要 Skill 系統 |
| 2 | Bot + handlers + 自然語言路由 | 加 Telegram |
| 3 | Gemini API 對話 + LLM Router | 加 AI 能力 |
| 4 | news_scraper + news_renderer | 加日報 |
| 5 | ConversationPlanner + Session | 加意圖路由 |
| 6 | 全部整合 + start.bat | 完整體（預設） |

> 💡 不指定 stages 時，預設產出全部 6 階段。

### Skill 自動產出

```
news-bot/
├── src/
│   ├── skills/               # BaseSkill 插件系統
│   │   ├── base.py           # 基底介面
│   │   ├── registry.py       # 自動發現 + invoke
│   │   └── internal/
│   │       ├── echo.py       # 回聲測試
│   │       ├── llm_cli.py    # Agent CLI 多後端
│   │       ├── news_scraper.py  # 新聞爬蟲
│   │       └── news_renderer.py # HTML 日報渲染
│   ├── bot/
│   │   ├── main.py           # Bot 入口
│   │   └── handlers.py       # 指令 + 自然語言路由
│   ├── llm/
│   │   └── gemini_chat.py    # Gemini API 即時對話
│   └── conversation/
│       ├── planner.py        # 意圖路由（keyword + LLM）
│       └── session.py        # Session 管理
├── config/
│   ├── news_sources.yaml     # 新聞來源設定
│   └── llm_prompts.yaml      # LLM 系統提詞
├── .env.example
├── requirements.txt
└── start.bat
```

> 💡 所有檔案一次到位，不需要逐步 prompt。

---

## Step 2：安裝 + 設定（5 min）

### 2.1 安裝依賴

**💻 在終端機執行：**

```bash
cd news-bot
pip install -r requirements.txt
```

### 2.2 設定環境變數

```bash
cp .env.example .env
```

**編輯 `.env` 填入：**

```bash
TELEGRAM_BOT_TOKEN=你的token        # @BotFather 取得
GEMINI_API_KEY=你的key               # aistudio.google.com/apikeys
LLM_BACKEND=gemini                   # 預設 LLM 後端
```

---

## Step 3：啟動 + 測試指令（5 min）

### 3.1 啟動 Bot

**💻 在終端機執行：**

```bash
python -m src.bot.main
```

**或 Windows 雙擊：**
```bash
start.bat
```

**預期輸出：**
```
📦 Skills loaded: 4
🤖 AI Agent Bot started polling...
```

### 3.2 測試基礎指令

**📱 在 Telegram 輸入：**

| 測試 | 預期結果 |
|------|---------|
| `/start` | ✅ 歡迎訊息 + 功能介紹 |
| `/skills` | ✅ 列出 4 個 Skills |

---

## Step 4：自然語言對話（5 min）

Bot 支援直接打字對話，不需要指令前綴。

**📱 在 Telegram 輸入：**

```
你是誰？你能做什麼？
```

→ 1-5 秒收到 Agent CLI 回應 ✅

```
什麼是 Python 的 async await？
```

→ 收到技術回答 ✅

### 📱 自然語言觸發對照表（Bot 端）

| 你說 | Planner 路由到 | 實際執行 |
|------|--------------|---------|
| 「今天有什麼科技新聞」 | news_scraper | 抓取新聞 |
| 「幫我寫一個計算機」 | llm_cli (codegen) | 產出程式碼 |
| 「echo 測試」 | echo | 回音 |
| 「什麼是 FastAPI」 | Agent CLI (chat) | LLM 深度回答 |
| `/news_scraper` | 直接指定 Skill | 按 ID 執行 |

### 運作原理

```
使用者文字
    │
    ▼
ConversationPlanner（意圖路由）
    │
    ├─ keyword 命中 → 直接執行 Skill
    ├─ /skill_id 指令 → 直接執行 Skill
    └─ 其他 → Agent CLI（Gemini）對話
```

> 💡 路由邏輯：keyword 命中 → 執行 Skill → 否則走 Agent CLI 對話

---

## Step 5：科技日報（5 min）

**📱 在 Telegram 輸入：**

```
/daily
```

### 自動執行流程

```
/daily 觸發
    │
    ▼
news_scraper（httpx 多來源併發）
    │ 抓取新聞
    ▼
news_renderer（HTML 卡片渲染）
    │ 套用模板
    ▼
Telegram 發送 HTML 檔案 📰
```

### 驗證

- [ ] 📱 收到「📡 抓取新聞中...」提示
- [ ] 📱 收到 HTML 檔案
- [ ] 瀏覽器開啟 → 多張精美卡片

> 🎉 **課程完成！** 一句提詞建好的 Bot 能自動抓新聞產日報。

---

## 📐 提詞場景對照

### IDE 端 vs Bot 端

| 場景 | 在哪裡 | 對象 | 目的 | 範例 |
|------|--------|------|------|------|
| 建置/修改程式碼 | 📝 AI IDE | Kiro Agent | 產出檔案 | `新增 weather Skill` |
| 使用 Bot 功能 | 📱 Telegram | 你的 Bot | 執行 Skill | `今天有什麼新聞` |
| 修 Bug | 📝 AI IDE | Kiro Agent | 修復程式碼 | `貼錯誤 + 請修復` |
| 日常對話 | 📱 Telegram | Bot → Agent CLI | 知識問答 | `什麼是 Python` |

> 💡 **記住：** IDE 提詞 = 改程式碼（產出檔案） ／ Bot 提詞 = 用功能（執行 Skill）

---

## 📝 IDE 提詞公式

```
[動作] + [目標] + [細節（選填）]
```

### 建專案提詞

| 想做的事 | 提詞 |
|---------|------|
| 建完整 Bot | `ark-ai-bot-builder，專案名稱 my-bot` |
| 只建 Skill 系統 + Bot | `ark-ai-bot-builder，專案名稱 my-bot，stages 1-3` |
| 指定 LLM 後端 | `ark-ai-bot-builder，專案名稱 my-bot，llm kiro` |

### 擴充功能提詞

| 想做的事 | 提詞 |
|---------|------|
| 新增 Skill | `在 src/skills/internal/ 新增一個天氣查詢 Skill，用 httpx 呼叫 wttr.in/{city}?format=3` |
| 改路由 | `修改 ConversationPlanner，新增 keyword 路由：「天氣」→ weather Skill` |
| 加排程 | `加入排程系統，每天早上 9 點觸發 /daily 並推送到指定 chat_id` |
| 改回覆風格 | `修改 config/llm_prompts.yaml，改為幽默風格回覆` |

### 修 Bug 提詞模板

**❌ 太模糊：**
```
Bot 壞了
```

**✅ 有效提詞：**
```
執行 python -m src.bot.main 出現以下錯誤：
Traceback (most recent call last):
  File "src/bot/main.py", line 3, in <module>
    from telegram import Update
ModuleNotFoundError: No module named 'telegram'
請修復
```

**公式：** `[執行了什麼指令] + [完整錯誤訊息] + [請修復]`

---

## 🏋️ 課後練習

| 難度 | 提詞 | 學到什麼 |
|------|------|---------|
| ⭐ | `在 src/skills/internal/ 新增 weather Skill，用 httpx 呼叫 wttr.in/{city}?format=3` | 新增 Skill |
| ⭐⭐ | `修改 ConversationPlanner，新增 keyword 路由：「天氣」→ weather Skill` | 路由機制 |
| ⭐⭐ | `加入 Gemini API 結構化新聞，用 response_mime_type="application/json"` | API JSON mode |
| ⭐⭐⭐ | `加入排程系統，每天 09:00 自動執行 /daily 並推送到 TELEGRAM_CHAT_ID` | APScheduler 整合 |
| ⭐⭐⭐ | `加入 /report 指令，將最近 7 天日報統計為週報 HTML` | 多 Skill 串接 |

---

## 進階操作

### 新增自定義 Skill

**📝 在 AI IDE 聊天框輸入：**

```
在 news-bot/src/skills/internal/ 新增一個天氣查詢 Skill，
使用 httpx 呼叫 wttr.in API，回傳指定城市天氣
```

→ 產出後 Bot 自動發現新 Skill，不需重啟。

### 修改新聞來源

編輯 `config/news_sources.yaml`：

```yaml
sources:
  - name: "Hacker News"
    url: "https://news.ycombinator.com/"
    type: html
    selector: ".titleline a"
    category: tech_general

  - name: "你想加的網站"
    url: "https://example.com"
    type: html
    selector: "h3 a"
    category: ai
```

### 切換 LLM 後端

修改 `.env`：

```bash
LLM_BACKEND=kiro      # gemini / kiro / claude
```

---

## 常見問題

### Q：一句話就能建好整個專案？

是的。`ark-ai-bot-builder` Skill 內含完整模板和建置邏輯，一次產出所有檔案。
後續擴充功能可以用額外的提詞逐步加入。

### Q：Bot 沒回應？

- 確認 `.env` 的 `TELEGRAM_BOT_TOKEN` 正確
- 確認沒有其他程式在用同一個 Token polling
- 確認有跟 Bot 開始對話（先按 /start）

### Q：Agent CLI 回應很慢？

- Gemini CLI 首次呼叫需 5-15 秒（正常）
- 如超過 60 秒，檢查 `gemini` 或 `kiro-cli` 是否已安裝並登入
- 可改用 Gemini API 模式（修改 handlers.py 走 `gemini_chat.py`）

### Q：/daily 抓不到新聞？

- 優先用 Hacker News（純 HTML 最穩定）
- 確認 `pip install httpx beautifulsoup4`
- 檢查 `config/news_sources.yaml` 設定

### Q：想加入 Gemini API 即時對話？

專案已內建 `src/llm/gemini_chat.py`，在 `.env` 填入 `GEMINI_API_KEY` 即可。
可在 handlers.py 的 `handle_message` 中改為優先走 API（延遲 1-3 秒）。

---

*作者：paddyyang ｜ 2026*
