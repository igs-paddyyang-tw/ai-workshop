# ⚡ AI Bot Workshop（進階班）— 50 分鐘速成指南

> 進階班：一堂課完成科技日報 Telegram Bot，全程 API 驅動，不依賴 CLI 工具。

**作者：** paddyyang
**日期：** 2026

**操作位置圖示說明：**
- 📝 = 在 **AI IDE 聊天框**（Kiro / Antigravity）輸入，觸發 Skill 產出程式碼
- 📱 = 在 **Telegram 聊天窗**，對你的 Bot 發送訊息
- 💻 = 在**終端機 / 命令列**執行指令

---

## 🎯 課程目標（1 堂 × 50 分鐘）

### 前提條件

- ✅ 已安裝 Python 3.12+、Git、Node.js 20+
- ✅ 已有 Telegram 帳號 + 從 @BotFather 取得 Bot Token
- ✅ 已有 Gemini API Key（https://aistudio.google.com/apikeys）
- ✅ 已安裝 AI IDE（Kiro 或 Antigravity）

### 時間分配

| 時間 | 步驟 | 你做什麼 | 產出 |
|------|------|---------|------|
| 0-5 min | Step 0 | clone skills + 確認環境 | 環境就緒 |
| 5-15 min | Step 1 | 📝 一句話建專案 + 加 Bot | FastAPI + Bot + 指令 |
| 15-25 min | Step 2 | 📝 一句話加排程 + 整合啟動 | Workflow + start.bat |
| 25-35 min | Step 3 | 📝 一句話接 Gemini API | /chat AI 對話 |
| 35-45 min | Step 4 | 📝 一句話加爬蟲 + 結構化 | 爬蟲 + API 結構化 JSON |
| 45-50 min | Step 5 | 📱 /daily 觸發 | 科技日報 HTML 完成 🎉 |

### 完成標準

```
✅ Bot 回應 /start /help /status
✅ /chat 能 AI 即時對話
✅ /daily 產出科技日報 HTML 卡片
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

在 AI IDE 聊天框輸入：

```
檢查我的開發環境
```

✅ 全部通過即進入 Step 1。

---

## Step 1：專案骨架 + Telegram Bot（10 min）

### 1.1 建立專案骨架

**📝 在 AI IDE 聊天框輸入：**

```
建立 ai-bot Web 專案，首頁使用 quickstart.html，
包含 health check API 和 Skill 自動發現機制
```

### 1.2 加入 Telegram Bot

**📝 在 AI IDE 聊天框輸入：**

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

### 驗證

```bash
📱 Telegram /start → 收到歡迎訊息 ✅
📱 Telegram /help  → 收到指令清單 ✅
```

---

## Step 2：排程系統 + 整合啟動（10 min）

### 2.1 加入排程

**📝 在 AI IDE 聊天框輸入：**

```
加入排程系統，包含 WorkflowEngine 和 APScheduler，
產出 daily_news.yaml 範例 workflow
```

### 2.2 整合啟動

**📝 在 AI IDE 聊天框輸入：**

```
整合 Bot + Web + 排程為統一啟動，建立 start.bat
```

### 驗證

```bash
start.bat
# Web: http://127.0.0.1:8000 ✅
# Bot: Telegram polling ✅
# 排程: APScheduler cron ✅
```

---

## Step 3：Gemini API 對話（10 min）

**📝 在 AI IDE 聊天框輸入：**

```
加入 Gemini API 對話能力，使用 google-genai SDK，
Bot /chat 用 API 即時回話，一般文字訊息也走 AI 對話
```

**產出：** `src/llm/gemini_chat.py`（Gemini API SDK 封裝）

### 核心實作邏輯

```python
from google import genai

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

async def chat(message: str) -> str:
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=message
    )
    return response.text
```

### 驗證

```
📱 Telegram /chat 你是誰 → 1-3 秒收到 AI 回應 ✅
📱 Telegram 直接打字「什麼是 Python」→ 收到 AI 回應 ✅
```

---

## Step 4：爬蟲 + API 結構化（10 min）

### 4.1 加入爬蟲

**📝 在 AI IDE 聊天框輸入：**

```
在 src/skills/internal/ 產出新聞爬蟲 Skill，
使用 httpx + BeautifulSoup，支援 CSS selector 設定，
產出結構化 Markdown 素材檔，來源設定參考 config/news_sources.yaml
```

### 4.2 加入 Gemini API 結構化

**📝 在 AI IDE 聊天框輸入：**

```
在 src/skills/internal/ 產出 news_structurer.py，
使用 Gemini API 將爬蟲產出的 Markdown 素材結構化為 JSON，
輸出格式參考 structured-example.json，
用 response_mime_type="application/json" 確保回傳 JSON
```

**產出：** `src/skills/internal/news_structurer.py`

### 核心實作邏輯

```python
from google import genai

STRUCTURE_PROMPT = """你是科技日報編輯。請將以下新聞素材轉化為結構化 JSON。
格式：{"date":"YYYY.MM.DD","cards":[{topic, title, what, why, summary, tags:[{icon,text}]}]}

素材：
{raw_markdown}
"""

async def structure_news(raw_markdown: str) -> dict:
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=STRUCTURE_PROMPT.format(raw_markdown=raw_markdown),
        config={
            "response_mime_type": "application/json"
        }
    )
    return json.loads(response.text)
```

### 驗證

**📝 在 AI IDE 聊天框輸入：**
```
測試 news_scraper 抓取 https://news.ycombinator.com/
然後用 news_structurer 結構化為 JSON
```

✅ `output/news/structured/` 下有 JSON 檔案產出

---

## Step 5：科技日報實戰（5 min）

### 5.1 秒出日報（Mock 資料保底）

**📝 在 AI IDE 聊天框輸入：**

```
用 structured-example.json 的 mock 資料，
透過 news_renderer Skill 產出日報 HTML
```

**驗證：** 瀏覽器開啟 `output/tech-daily-news/tech-daily-{today}.html` → 看到 3 張精美卡片 🎉

### 5.2 Telegram 一鍵觸發

**📱 在 Telegram 輸入：**
```
/daily
```

→ Bot 自動跑完：scrape → Gemini API 結構化 → render HTML → 發送檔案

### 驗證

- [ ] 📱 Telegram 收到 HTML 檔案
- [ ] 瀏覽器開啟 HTML → 卡片正確顯示

> 🎉 **課程完成！** 你的 AI Bot 能自動抓新聞 → API 結構化 → 產出精美日報。

---

## 完整流程圖

```
/daily 觸發
    │
    ▼
news_scraper（httpx + BeautifulSoup）
    │ 產出 Markdown 素材
    ▼
news_structurer（Gemini API + JSON mode）
    │ 產出結構化 JSON
    ▼
news_renderer（HTML 模板套入）
    │ 產出 HTML 卡片
    ▼
Telegram 發送 HTML 檔案 📰
```

---

## 提詞公式

```
[動作] + [目標] + [細節（選填）]
```

### 範例

| 想做的事 | 提詞 |
|---------|------|
| 建專案 | `建立 ai-bot Web 專案` |
| 加 Bot | `加入 Telegram Bot` |
| 加排程 | `加入排程系統` |
| 加對話 | `加入 Gemini API 對話能力` |
| 加爬蟲 | `產出新聞爬蟲 Skill` |
| 加結構化 | `產出 news_structurer，使用 Gemini API 結構化` |
| 改東西 | `修改 news_scraper.py，加入 timeout 30 秒` |
| 修 bug | `執行出現 ModuleNotFoundError，請修復` |

---

## 常見問題

### Q：Gemini API Key 哪裡取得？

1. 前往 https://aistudio.google.com/apikeys
2. 點擊「Create API Key」→ 複製
3. 填入 `.env` 的 `GEMINI_API_KEY=`

免費額度：60 req/min、1,000 req/day。

### Q：Bot 沒回應？

- 確認 `.env` 的 `TELEGRAM_BOT_TOKEN` 正確
- 確認 Bot 已啟動（`start.bat`）
- 確認有跟 Bot 開始對話（先按 /start）

### Q：結構化 JSON 格式錯誤？

使用 `response_mime_type="application/json"` 強制 Gemini 回傳合法 JSON。
如果仍有問題，加上 `response_schema` 定義預期結構。

### Q：爬蟲抓不到內容？

- 優先用 Hacker News（純 HTML 最穩定）
- 確認 `pip install httpx beautifulsoup4`
- 加入 User-Agent header

---

## 教材包檔案

```
ai-bot-advanced/
├── QUICKSTART.md                ← 本文件
├── bot-responses.md             ← Bot 回應範本
├── template-tech-daily.html     ← 日報 HTML 模板
├── structured-example.json      ← Mock 資料（測試 + 保底用）
├── ai-skill-hub-summary.md      ← 爬蟲來源參考
└── .env.example                 ← 環境變數範本
```

---

## 與初階班差異

| 項目 | 初階班（2 堂） | 進階班（1 堂） |
|------|--------------|--------------|
| 時長 | 100 分鐘 | 50 分鐘 |
| 結構化方式 | Gemini CLI / Kiro CLI | Gemini API（程式碼內直接呼叫） |
| 前置條件 | 無 | 需已備好環境 + API Key |
| 產出完整度 | 逐步驗證 | 快速串接一次到位 |
| 適合對象 | 第一次接觸 | 有 Python 基礎 |

---

*作者：paddyyang ｜ 2026*
