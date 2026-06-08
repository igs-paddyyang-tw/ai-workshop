# ⚡ AI Bot Builder — 一句話建 Bot 速成指南

> 一句提詞，全自動產出完整 Telegram AI Bot。不需逐步操作，Skill 直接建好整個專案。

**作者：** paddyyang
**日期：** 2026

**操作位置圖示說明：**
- 📝 = 在 **AI IDE 聊天框**（Kiro / Antigravity）輸入
- 📱 = 在 **Telegram 聊天窗**，對你的 Bot 發送訊息
- 💻 = 在**終端機 / 命令列**執行指令

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

### Skill 自動產出

`ark-ai-bot-builder` 會一次產出完整專案：

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

### 運作原理

```
使用者文字
    │
    ▼
ConversationPlanner（意圖路由）
    │
    ├─ keyword 命中 → 直接執行 Skill
    └─ 其他 → Agent CLI（Gemini）對話
```

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

## 與其他 Workshop 比較

| 項目 | ai-bot-workshop（初階） | ai-bot-advanced（進階） | ai-bot-builder（本課） |
|------|------------------------|------------------------|----------------------|
| 時長 | 100 分鐘（2 堂） | 50 分鐘（1 堂） | 30 分鐘（1 堂） |
| 步驟數 | 7 步驟逐步建 | 6 步驟逐步建 | 1 步產出 + 設定啟動 |
| 提詞次數 | 7+ 次 | 5+ 次 | 1 次（一句搞定） |
| 結構化方式 | Gemini CLI | Gemini API | Agent CLI |
| 適合對象 | 第一次接觸 | 有 Python 基礎 | 想最快看到成果 |
| 學到什麼 | 每層原理 | API 整合 | Skill 系統全貌 |

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
    selector: ".athing"
    title_selector: ".titleline a"
    category: general

  - name: "你想加的網站"
    url: "https://example.com"
    selector: "h3 a"
    category: ai
```

### 切換 LLM 後端

修改 `.env`：

```bash
LLM_BACKEND=kiro      # gemini / kiro / claude
```

---

## 提詞公式

```
ark-ai-bot-builder + 專案名稱 [+ 選項]
```

### 範例

| 想做的事 | 提詞 |
|---------|------|
| 建基礎 Bot | `ark-ai-bot-builder，專案名稱 my-bot` |
| 指定階段 | `ark-ai-bot-builder，專案名稱 my-bot，stages 1-3` |
| 擴充 Skill | `在 src/skills/internal/ 新增 XXX Skill` |
| 改 Bug | `執行出現 ModuleNotFoundError，請修復` |
| 加功能 | `加入排程系統，每天早上 9 點觸發 /daily` |

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

## 教材包檔案

```
ai-bot-builder/
├── QUICKSTART.md                ← 本文件
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

*作者：paddyyang ｜ 2026*
