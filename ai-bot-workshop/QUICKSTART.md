# 🚀 AI Bot Workshop — 快速上手指南

> 用 AI 幫你寫程式，2 堂 50 分鐘完成一個科技日報機器人。

**作者：** paddyyang
**日期：** 2026

**操作位置圖示說明：**
- 📝 = 在 **AI IDE 聊天框**（Kiro / Antigravity）輸入，觸發 Skill 產出程式碼
- 📱 = 在 **Telegram 聊天窗**，對你的 Bot 發送訊息
- 💻 = 在**終端機 / 命令列**執行指令

---

## 🎯 課程目標（2 堂 × 50 分鐘）

### 第一堂：命令式開發（50 min）

> Step 0-3：用指令建立專案骨架，Bot 能回應、排程能跑。

| 時間 | 步驟 | 你做什麼 | Skill 做什麼 |
|------|------|---------|-------------|
| 0-10 min | Step 0 環境 | clone skills + 確認工具 | ark-env-doctor 自動檢查 |
| 10-25 min | Step 1 骨架 | 📝 一句話描述專案 | 產出 FastAPI + Skill 系統 |
| 25-40 min | Step 2 Bot | 📝 一句話加入 Bot | 產出 Telegram Bot + 指令 |
| 40-50 min | Step 3 排程 | 📝 一句話加入排程 | 產出 Workflow + 排程 + start.bat |

**第一堂完成標準：** `start.bat` 一鍵啟動 Web + Bot + 排程，📱 Telegram `/start` `/help` `/status` 有回應

### 第二堂：LLM Agent 開發（50 min）

> Step 4-6：接入 LLM，讓 Bot 從「指令機器人」升級為「AI Agent」。

| 時間 | 步驟 | 你做什麼 | Skill 做什麼 |
|------|------|---------|-------------|
| 0-15 min | Step 4 對話 | 📝 一句話接 Gemini API | Bot /chat 即時 AI 對話 |
| 15-30 min | Step 5 爬蟲 | 📝 一句話加入爬蟲 | 產出爬蟲 + Markdown 素材 |
| 30-50 min | Step 6 實戰 | 📝 導入 Gemini CLI + 💻 結構化 | 產出科技日報 HTML |

**第二堂完成標準：** 📱 `/chat` 能 AI 對話 + 爬蟲能抓新聞 + Gemini CLI 結構化產出日報 HTML

---

## 你需要準備的東西

| 項目 | 說明 |
|------|------|
| 電腦 | Windows / Mac / Linux |
| AI IDE（擇一） | Kiro 或 Antigravity IDE |
| Gmail 帳號 | Gemini CLI 登入用 |
| Node.js 20+ | https://nodejs.org |
| Python 3.12+ | https://python.org |
| Git | https://git-scm.com |
| Telegram 帳號 | @BotFather 建立 Bot |

### IDE 擇一安裝

| IDE | 下載網址 | Skills 路徑 |
|-----|---------|------------|
| **Kiro** | https://kiro.dev | `.kiro/skills/` |
| **Antigravity** | https://antigravity.google/download | `.agents/skills/` |

---

## Step 0：環境準備與 Skills 取得

### 安裝 Gemini CLI

```bash
npm install -g @google/gemini-cli
gemini    # 選 Login with Google → Gmail 登入
```

### 安裝 Kiro CLI

```bash
npm install -g kiro-cli
kiro-cli login    # 瀏覽器授權
```

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

✅ 全部通過即可進入 Step 1。

---

## Step 1：Web 專案骨架與 Skill 系統

**📝 在 AI IDE 聊天框輸入：**

```
建立 ai-bot Web 專案，首頁使用 quickstart.html，
包含 health check API 和 Skill 自動發現機制
```

**Skill 產出：** FastAPI Server + BaseSkill + SkillRegistry + echo Skill

**驗證：**
```bash
python -m src.server.main
# 瀏覽器開 http://localhost:8000 → 看到首頁
# curl http://localhost:8000/health → {"status": "ok"}
```

---

## Step 2：Telegram Bot 介面與指令

**📝 在 AI IDE 聊天框輸入：**

```
加入 Telegram Bot，回應內容參考 bot-responses.md，
/start 回覆歡迎訊息，/help 列出指令，/status 顯示系統狀態，
並設定 Bot Menu 指令選單
```

**Skill 產出：** Bot 入口 + handlers + Menu 指令選單

**設定 .env：**
```bash
cp .env.example .env
# 填入 TELEGRAM_BOT_TOKEN（從 @BotFather 取得）
```

**Bot Menu 指令：**

| 指令 | 說明 |
|------|------|
| `/start` | 歡迎訊息 + 功能介紹 |
| `/help` | 完整指令清單 |
| `/status` | 系統狀態 |
| `/chat` | 與 AI 對話（Step 4 加入） |
| `/skills` | 列出已載入 Skills |

> 💡 Bot 啟動時自動設定 Menu，使用者輸入 `/` 就會彈出指令選單。

**驗證（在 Telegram 聊天窗）：**
```
📱 Telegram 輸入 / → 看到指令選單彈出
📱 Telegram 輸入 /start → 收到歡迎訊息
📱 Telegram 輸入 /help  → 收到指令清單
📱 Telegram 輸入 /status → 收到系統狀態
```

---

## Step 3：Workflow 引擎與自動排程

**📝 在 AI IDE 聊天框輸入：**

```
加入排程系統，包含 WorkflowEngine 和 APScheduler，
產出 daily_news.yaml 範例 workflow
```

**Skill 產出：** WorkflowEngine + ScheduleEngine + YAML 範例

**驗證：**
```bash
# 確認 workflows/daily_news.yaml 存在
# 確認 src/workflow/engine.py 存在
# 確認 src/scheduler/engine.py 存在
```

### 整合啟動：建立 start.bat

**📝 在 AI IDE 聊天框輸入：**

```
整合 Bot + Web + 排程為統一啟動，建立 start.bat
```

**產出 `start.bat`：**
```bat
@echo off
echo   ai-bot 啟動中...
py -m uvicorn src.server.main:app --host 127.0.0.1 --port 8000
pause
```

一個 bat 檔同時啟動 Web + Bot + 排程：
```bash
start.bat
# Web: http://127.0.0.1:8000 ✅
# Bot: Telegram polling ✅
# 排程: APScheduler cron ✅
```

> 🎉 **第一堂完成！** Bot 是「指令機器人」— 你說什麼它做什麼。接下來第二堂讓它變聰明。

---

## Step 4：Gemini API 對話（Bot 即時回應）

**📝 在 AI IDE 聊天框輸入：**

```
加入 Gemini API 對話能力，Bot /chat 用 API 即時回話，
一般文字訊息也走 AI 對話
```

**Skill 產出：** `src/llm/gemini_chat.py`（Gemini API SDK 封裝）

### 取得 Gemini API Key（免費）

1. 前往 https://aistudio.google.com/apikeys
2. 點擊「Create API Key」→ 複製
3. 填入 `ai-bot/.env`：

```bash
GEMINI_API_KEY=your_actual_api_key_here
```

> 💡 免費額度：60 req/min、1,000 req/day。Step 6 的 Gemini CLI 也共用此 Key。

### 驗證（在 Telegram 聊天窗）

```
📱 Telegram /chat 你是誰 → 1-3 秒收到 AI 回應 ✅
📱 Telegram 直接打字「什麼是 Python」→ 收到 AI 回應 ✅
```

> 💡 Step 4 完成！Bot 從「指令機器人」升級為「AI Agent」— 能即時 AI 對話了。

---

## Step 5：網頁爬蟲與素材處理

**📝 在 AI IDE 聊天框輸入：**

```
在 src/skills/internal/ 產出新聞爬蟲 Skill，
使用 httpx + BeautifulSoup，支援 CSS selector 設定，
產出結構化 Markdown 素材檔，來源設定參考 config/news_sources.yaml
```

**💻 安裝依賴：**
```bash
pip install httpx beautifulsoup4
```

**Skill 產出：**
```
src/skills/internal/
├── news_scraper.py      ← 網頁爬蟲（httpx + CSS selector）
└── news_parser.py       ← 解析 → 結構化 Markdown

config/
└── news_sources.yaml    ← 新聞來源設定（已驗證可抓）

output/news/raw/
└── 2026-05-29-general.md  ← 產出的 Markdown 素材
```

### 可抓取的新聞來源

以下網站已驗證 httpx 可直接抓取（詳見 `ai-skill-hub-summary.md`）：

| 來源 | 類別 | 穩定度 |
|------|------|--------|
| **Hacker News** | 綜合科技 | ⭐⭐⭐ 最穩定（推薦教學用） |
| TechCrunch AI | AI 焦點 | ⭐⭐ 部分內容需 JS |
| Skills-Hub.ai | AI Skills | ⭐⭐ |
| AgentSkillsHub.top | AI Skills | ⭐⭐ |
| AgentSkillsHub.dev | AI Skills | ⭐⭐ |
| LobeHub Skills | AI Skills | ⭐⭐ |

### 驗證

**📝 在 AI IDE 聊天框輸入：**
```
測試 news_scraper 抓取 https://news.ycombinator.com/
```

**預期結果：**
```
Success: True, Count: 5
  - Claude Opus 4.8
  - Volkswagen blocks Home Assistant...
  - I made a million dollar product...
```

✅ `output/news/raw/` 下有 Markdown 檔案產出

> 💡 抓到的 Markdown 素材就是 Step 6 的輸入 — Gemini CLI 會把它結構化為日報 JSON。

---

## Step 6：科技日報實戰（串接全部能力）

> 🎯 目標：5 分鐘內看到你的第一份科技日報 HTML 卡片。

### 6.1 秒出日報（不需 LLM，保證成功）

**📝 在 AI IDE 聊天框輸入：**

```
用 structured-example.json 的 mock 資料，
透過 news_renderer Skill 產出日報 HTML
```

**或直接執行：**
```bash
💻 py -c "import asyncio; from src.skills.internal.news_renderer import NewsRendererSkill; print(asyncio.run(NewsRendererSkill().execute({'data_path':'structured-example.json','template':'templates/tech-daily.html'})))"
```

**驗證：** 瀏覽器開啟 `output/tech-daily-news/tech-daily-{today}.html`

→ 看到 3 張精美卡片（AI 焦點 / 開發工具 / 硬體趨勢）🎉

> 💡 這步不需要 LLM、不需要網路，100% 保證成功。

### 6.2 Gemini CLI 或 Kiro CLI 結構化（選配，二擇一）

把 Step 5 抓到的真實 Markdown 素材丟給 LLM CLI 結構化：

**方案 A：Gemini CLI（需要 API 額度）**

**💻 在終端機執行：**
```bash
gemini -p "你是科技日報編輯。請將以下新聞素材轉化為結構化 JSON，格式：
{topic, title, what, why, summary, tags[{icon,text}]}
素材：（貼上 output/news/raw/ 的內容）" --skip-trust
```

**方案 B：Kiro CLI（不需要額度，用 Kiro IDE 授權）**

**💻 在終端機執行：**
```bash
kiro-cli chat --trust-all-tools --legacy-ui --message "你是科技日報編輯。請將以下新聞素材轉化為結構化 JSON，格式：{topic, title, what, why, summary, tags[{icon,text}]}。素材：（貼上 output/news/raw/ 的內容）"
```

**兩者比較：**

| | Gemini CLI | Kiro CLI |
|---|---|---|
| 安裝 | `npm i -g @google/gemini-cli` | `npm i -g kiro-cli` |
| 授權 | GEMINI_API_KEY + Gmail 登入 | AWS 登入（`kiro-cli login`） |
| 額度 | 1,000 req/day（免費） | 無明確限制 |
| 延遲 | 5-15 秒 | 30-120 秒 |
| 適合 | 快速結構化 | Gemini 額度用完時的備案 |

→ 產出結構化 JSON → 存檔 → 再跑 `news_renderer` → 真實新聞日報

> ⚠️ 兩個都不行？沒關係，6.1 的 mock 日報一樣是完整成品。

### 6.3 Telegram 一鍵觸發

**📱 在 Telegram 輸入：**
```
/daily
```

→ Bot 自動跑完 scrape → structure → render → 發送 HTML 檔案

**驗證：**
- [ ] 📱 Telegram 收到 HTML 檔案
- [ ] 瀏覽器開啟 HTML → 卡片正確顯示（圖片、標紅、頁碼）

> 🎉 **第二堂完成！** 你的 AI Agent 能自動產出科技日報了。

---

## 提詞公式

```
[動作] + [目標] + [細節（選填）]
```

### 進階提詞技巧

**給更多細節 = 更精確的產出：**

```
建立 ai-bot Web 專案，使用 FastAPI，專案名稱 my-news-bot，
包含 health check API 和 Skill 自動發現機制
```

**指定路徑：**

```
在 src/skills/internal/ 產出一個新聞爬蟲 Skill，
使用 httpx + BeautifulSoup，支援 CSS selector 設定
```

**要求修改：**

```
修改 news_scraper.py，加入 Playwright 支援，
當 method 設定為 playwright 時使用瀏覽器渲染
```

**貼錯誤訊息讓 AI 修：**

```
執行 python -m src.bot.main 出現以下錯誤：
ModuleNotFoundError: No module named 'telegram'
請修復
```

---

## 常見問題

### Q：Skill 沒有觸發怎麼辦？

| 想做的事 | ❌ 太模糊 | ✅ 明確觸發 |
|---------|----------|-----------|
| 建專案 | `幫我開始` | `建立 Web 專案` |
| 加 Bot | `我要聊天功能` | `加入 Telegram Bot` |
| 加排程 | `定時執行` | `加入排程系統` |
| 爬蟲 | `抓資料` | `加入新聞抓取功能` |

### Q：Gemini CLI 額度用完了？

免費額度：60 req/min、1,000 req/day。
- 用 `structured-example.json` 跳過 LLM 測試模板
- 等隔天額度重置
- 或改用 `claude -p`（需要 API Key）

### Q：Bot 沒回應？

- 確認 `.env` 的 `TELEGRAM_BOT_TOKEN` 正確
- 確認 Bot 已啟動（`python -m src.bot.main`）
- 確認 Telegram 有跟 Bot 開始對話（先按 /start）

---

## 教材包檔案

```
ai-bot-workshop/
├── QUICKSTART.md                ← 本文件
├── quickstart.html              ← HTML 版（= webapp 首頁）
├── ai-bot-build-guide.md        ← 完整教學（7 步驟詳細說明）
├── bot-responses.md             ← Bot 回應範本
├── template-tech-daily.html     ← 日報 HTML 模板
├── structured-example.json      ← Mock 資料（測試用）
└── .env.example                 ← 環境變數範本
```

---

## 7 步開發藍圖

```
── 第一堂：命令式開發 ──────────────────────
Step 0: 環境準備與 Skills 取得
Step 1: Web 專案骨架與 Skill 系統
Step 2: Telegram Bot 介面與指令
Step 3: Workflow 引擎與自動排程 + start.bat

── 第二堂：LLM Agent 開發 ─────────────────
Step 4: Gemini API 對話（Bot 即時回應）
Step 5: 網頁爬蟲與素材處理
Step 6: 科技日報實戰（串接全部能力）
```

完整細節請參考 `ai-bot-build-guide.md`。

---

*作者：paddyyang ｜ 2026*
