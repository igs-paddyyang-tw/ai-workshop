---
title: "ai-bot 建置教學 — 7 步驟從零到完整"
type: guide
created: 2026-05-25
updated: 2026-05-25
language: zh-TW
---

# ai-bot 建置教學 — 7 步驟從零到完整

使用 Ark Skills 建立 Gemini CLI 驅動的自進化 Telegram Bot + FastAPI 服務。

**操作位置圖示說明：**
- 📝 = 在 **AI IDE 聊天框**（Kiro / Antigravity）輸入，觸發 Skill 產出程式碼
- 📱 = 在 **Telegram 聊天窗**，對你的 Bot 發送訊息
- 💻 = 在**終端機 / 命令列**執行指令

---

## 專案定位

**Gemini CLI 驅動的自進化 Telegram Bot + FastAPI 服務**

核心能力：
- 透過 Telegram 與 AI 對話（Session + 意圖路由）
- 自動產出新 Skill 並 hot reload 執行
- 定時抓取新聞並推送日報
- 多 LLM CLI 後端支援（Gemini/Kiro/Claude/Antigravity）

---

## 建置步驟總覽

### 第一堂：命令式開發（Step 0-3）

> 用指令建立專案骨架，Bot 能回應、排程能跑。

| # | Skill | 產出內容 | 必要性 |
|---|-------|---------|--------|
| 0 | ark-env-doctor | 環境檢查 + Skills 取得 | ✅ 必要（前置） |
| 1 | ark-webapp-generator | 專案骨架 + Skill 系統 | ✅ 必要（基礎） |
| 2 | ark-chatbot-generator | TG Bot + 指令 | ✅ 必要（入口） |
| 3 | ark-scheduler-generator | Workflow + 排程 + start.bat | ✅ 必要（自動化） |

### 第二堂：LLM Agent 開發（Step 4-6）

> 接入 LLM，讓 Bot 能思考、能抓資料、能產出日報。

| # | Skill | 產出內容 | 必要性 |
|---|-------|---------|--------|
| 4 | ark-llm-tools | Gemini API 對話（Bot /chat） | ✅ 必要（AI 核心） |
| 5 | ark-web-scraper | 爬蟲 + Markdown 產出 | ✅ 必要（資料來源） |
| 6 | ark-llm-cli + 實戰 | Gemini CLI 結構化 + 科技日報 HTML | 🎯 綜合演練 |

```
── 第一堂：命令式開發 ──────────────────────
Step 0: ark-env-doctor           → 環境準備與 Skills 取得
Step 1: ark-webapp-generator     → Web 專案骨架與 Skill 系統
Step 2: ark-chatbot-generator    → Telegram Bot 介面與指令
Step 3: ark-scheduler-generator  → Workflow 引擎與自動排程 + start.bat

── 第二堂：LLM Agent 開發 ─────────────────
Step 4: ark-llm-tools           → Gemini API 對話（Bot 即時回應）
Step 5: ark-web-scraper         → 網頁爬蟲與素材處理
Step 6: ark-llm-cli + 實戰      → Gemini CLI 結構化 + 科技日報產出
```

---

## Step 0：環境準備與 Skills 取得

### 取得 Skills

從 GitHub 取得 ark-agent-skills 開發用 Skill 集合：

```bash
# Clone Skills repo 到 .kiro/skills/
git clone https://github.com/igs-paddyyang-tw/ark-agent-skills .kiro/skills/
```

**repo 內容：** 45 個 Ark Skills，涵蓋本教學所有步驟所需的 Skill。

### 使用 Skill：`ark-env-doctor`

**觸發語句：** 「檢查我的開發環境」

**用途：** 確認本機環境是否具備所有必要工具與依賴，避免後續步驟卡在環境問題。

**檢查項目：**

| 項目 | 最低需求 |
|------|---------|
| Python | 3.12+ |
| pip / uv | 已安裝 |
| Git | 已安裝 |
| Node.js | 20+（Gemini CLI + Kiro CLI 需要） |
| Gemini CLI | 本地安裝，Gmail 登入 |
| Kiro CLI | 本地安裝，`kiro-cli login` 授權 |
| Telegram Bot Token | 已取得（Step 2 需要） |

### 安裝 Gemini CLI

> 官方網站：https://google-gemini.github.io/gemini-cli/
>
> GitHub：https://github.com/google-gemini/gemini-cli

```bash
# 需要 Node.js 20+
npm install -g @google/gemini-cli
```

安裝完成後首次執行：

```bash
gemini
```

啟動時選擇 **Login with Google**，會開啟瀏覽器進行 Gmail 帳號登入授權。
登入後即可免費使用（60 req/min、1,000 req/day）。

### 安裝 Kiro CLI

```bash
npm install -g kiro-cli
```

安裝完成後登入：

```bash
kiro-cli login
```

瀏覽器授權完成即可。Kiro CLI 是 Agent Team 的 AI 後端，每個 agent 都透過它執行任務。

**產出：**
- 環境診斷報告（pass/fail 清單）
- 缺失項目的安裝建議指令
- `.env.example` 所需環境變數提示

**範例輸出：**
```
── Environment Check ──────────
✅ Python: 3.12.4
✅ uv: 0.7.x
✅ Git: 2.45.x
⚠️ TELEGRAM_BOT_TOKEN: 未設定（Step 2 需要）
⚠️ GEMINI_API_KEY: 未設定（Step 4 需要）
────────────────────────────────
環境就緒，可進入 Step 1。
```

### 可用 Skills 一覽

取得 repo 後，以下 Skills 可在後續步驟中使用：

| Skill 名稱 | 用途 |
|------------|------|
| `ark-webapp-generator` | Step 1 — Web 專案骨架與 Skill 系統 |
| `ark-chatbot-generator` | Step 2 — Telegram Bot 介面與指令 |
| `ark-scheduler-generator` | Step 3 — Workflow 引擎與自動排程 |
| `ark-llm-cli` | Step 4 — LLM CLI 大腦核心封裝 |
| `ark-web-scraper` | Step 5 — 網頁爬蟲與素材處理 |
| `ark-env-doctor` | 環境診斷（本步驟） |
| `ark-docker-deploy` | 容器化部署（進階） |
| `ark-test-runner` | 自動化測試 |
| `ark-security-audit` | 安全性掃描 |

> 💡 完整 45 個 Skills 清單請參考 repo 的 README.md。

### 更多 Skills 資源

除了 ark-agent-skills repo，以下平台可找到更多社群 Skills：

| # | 平台 | 網址 | 說明 |
|---|------|------|------|
| 1 | Skills-Hub.ai | https://skills-hub.ai/ | 4,700+ Skills 聚合平台，一鍵安裝 |
| 2 | AgentSkillsHub.top | https://agentskillshub.top/ | 70K+ 開源目錄，每 8 小時更新 |
| 3 | AgentSkillsHub.dev | https://agentskillshub.dev/ | 1,200+ 安全掃描 Skills，A-F 評級 |
| 4 | SkillsMP.com | https://skillsmp.com/ | Agent Skills Marketplace，職業分類 |
| 5 | LobeHub Skills | https://lobehub.com/skills | 支援 SKILL.md 格式發布 |
| 6 | Anthropic Skills | https://github.com/anthropics/skills | 官方 Skills repo |
| 7 | CavinHuang/claude-skills-hub | https://github.com/CavinHuang/claude-skills-hub | 150+ 免費 Skills |
| 8 | qufei1993/skills-hub | https://github.com/qufei1993/skills-hub | 跨平台桌面 App |

> 安裝方式：`git clone` 到 `.kiro/skills/` 目錄即可使用。多數平台採用 `SKILL.md` 格式（frontmatter 含 name + description）。

---

## Step 1：Web 專案骨架與 Skill 系統

### 使用 Skill：`ark-webapp-generator`

**觸發語句：** 「建立 ai-bot Web 專案，首頁使用 static/index.html」

**定位：** 整個 ai-bot 的地基。產出 FastAPI Server + Skill 插件系統，後續所有功能（Bot、LLM、爬蟲）都以 Skill 形式掛載進來。

**Skill 系統架構：**

```
BaseSkill（介面）
    │
    ├── echo.py          ← 範例 Skill（驗證系統）
    ├── llm_cli.py       ← Step 4 加入
    ├── news_scraper.py  ← Step 5 加入
    └── news_renderer.py ← Step 6 加入

SkillRegistry（auto_discover）
    → 掃描 skills/internal/ 目錄
    → 自動載入所有 BaseSkill 子類別
    → 提供 invoke(skill_id, params) 統一呼叫介面
```

**產出：**
```
ai-bot/
├── src/
│   ├── __init__.py
│   ├── skills/
│   │   ├── base.py              ← BaseSkill + SkillParam + SkillResult
│   │   ├── registry.py          ← SkillRegistry（auto_discover）
│   │   ├── internal/
│   │   │   ├── __init__.py
│   │   │   ├── echo.py          ← 最小範例 Skill
│   │   │   ├── wiki_manager.py  ← 知識庫管理 Skill
│   │   │   └── cost_tracker.py  ← LLM 成本追蹤 Skill
│   │   └── external/
│   ├── agent/
│   │   ├── verifier.py          ← CodeVerifier（自動 pytest）
│   │   ├── error_handler.py     ← 結構化錯誤分類
│   │   └── event_log.py         ← JSONL 操作日誌
│   └── server/
│       ├── main.py              ← FastAPI + lifespan
│       ├── api/
│       │   └── chat.py          ← POST /api/v1/chat
│       ├── core/
│       ├── templates/
│       └── static/
├── knowledge/                   ← 長期知識庫（Schema v3.0）
│   ├── schema.md
│   ├── index.md
│   ├── log.md
│   ├── raw/
│   └── wiki/
├── tests/
├── requirements.txt
├── .env.example
└── README.md
```

**關鍵產出：**
- `BaseSkill` 介面（所有 Skill 的父類別）
- `SkillRegistry`（auto_discover + invoke）
- `echo` Skill（驗證系統運作）
- `wiki_manager` Skill（知識庫查詢/匯入）
- `cost_tracker` Skill（LLM 成本追蹤）
- `knowledge/` 知識庫結構（Schema v3.0）
- `src/agent/` Agent 基礎設施（verifier + error_handler + event_log）
- FastAPI Server（health + skills + chat API）
- **首頁**：瀏覽器開啟 `http://localhost:8000` 顯示 `quickstart.html`

**設定首頁：**

Step 1 產出後，將教材包的 `quickstart.html` 設為 webapp 首頁：

```bash
# 複製到 static 目錄作為首頁
cp quickstart.html src/server/static/index.html
```

FastAPI 的 `main.py` 需包含靜態檔案掛載：

```python
from fastapi.staticfiles import StaticFiles

app.mount("/", StaticFiles(directory="src/server/static", html=True), name="static")
```

> 💡 觸發 Skill 時可直接說明：「建立 ai-bot Web 專案，首頁使用 static/index.html」

**驗證方式：**
```bash
python -m src.server.main
# 瀏覽器開啟 http://localhost:8000 → 看到 quickstart.html 頁面（暗黑科技風 6 頁卡片）
# GET http://localhost:8000/health → {"status": "ok"}
```

---

## Step 2：Telegram Bot 介面與指令

### 使用 Skill：`ark-chatbot-generator`

**觸發語句：** 「加入 Telegram Bot 與對話系統」

分兩階段產出：先建 Bot 入口與基礎指令，再加入 Session 管理與意圖路由。

**產出：**
```
src/bot/
├── __init__.py
├── main.py              ← create_app() + 指令註冊 + graceful shutdown
└── handlers.py          ← cmd_start / cmd_help / cmd_status / cmd_chat

src/conversation/
├── __init__.py
├── session.py           ← Session + Turn dataclass
├── session_manager.py   ← SessionManager（TTL + 生命週期）
└── planner.py           ← ConversationPlanner（三層路由）
```

**Bot 指令：**`
- `/start` — 歡迎訊息 + 功能介紹
- `/help` — 完整指令清單
- `/status` — 系統狀態（Skills 數量、LLM 可用性、排程設定）
- `/chat <問題>` — 與 AI 對話
- `/skills` — 列出已載入 Skills

**設定 Bot Menu（指令選單）：**

Bot 啟動時自動呼叫 `set_my_commands()` 設定 Telegram 指令選單，使用者點擊輸入框旁的 `/` 按鈕即可看到所有指令：

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
    """Bot 啟動後設定 Menu 指令。"""
    await application.bot.set_my_commands(BOT_COMMANDS)

# 建立 Bot 時掛載 post_init
app = ApplicationBuilder().token(token).post_init(post_init).build()
```

> 💡 設定後使用者在 Telegram 輸入 `/` 就會彈出指令選單，不需要記指令。

**意圖路由（三層降級）：**

```
1. keyword 快速路由（毫秒級，不呼叫 LLM）
   「抓新聞」→ news_scraper / 「產出日報」→ news_renderer
2. LLM 意圖分類（有 LLM 時，含對話歷史 context）
   回傳 intent + skill_id + params + confidence
3. keyword fallback（LLM 不可用時的降級）
```

**設定 Bot 回應：**

將教材包的 `bot-responses.md` 中的回應文字套用到 `handlers.py`：

```bash
# bot-responses.md 包含：
# 1. /start 歡迎訊息（功能介紹 + 指引）
# 2. /help 完整指令清單（基礎 + AI + 新聞 + 管理）
# 3. /status 系統狀態（server/bot/skills/llm 狀態）
# 4. handlers.py 完整參考程式碼（可直接複製使用）
```

> 💡 觸發 Skill 時可直接說明：「加入 Telegram Bot，/start 回覆歡迎訊息和功能介紹，/help 列出所有指令，/status 顯示系統狀態，回應內容參考 bot-responses.md」

**驗證方式：**
```bash
python -m src.bot.main
# Telegram 輸入 /start → 收到歡迎訊息
# Telegram 輸入 /help  → 收到指令清單
# Telegram 輸入 /status → 收到系統狀態
```

**意圖路由：**

| 意圖 | 觸發 | 路由目標 |
|------|------|---------|
| chat | 一般對話 | llm_cli（chat 模式） |
| skill_call | 呼叫 Skill | registry.invoke() |
| codegen | 產出程式碼 | llm_cli（codegen 模式） |
| news | 新聞相關 | news_scraper |
| unknown | 無法分類 | llm_cli（chat fallback） |

**環境變數：**
```bash
TELEGRAM_BOT_TOKEN=your_token
```

---

## Step 3：Workflow 引擎與自動排程

### 使用 Skill：`ark-scheduler-generator`

**觸發語句：** 「加入排程系統」

**產出：**
```
src/workflow/
├── __init__.py
└── engine.py            ← WorkflowEngine（YAML 解析 + timeout/retry/continue_on_error）

src/scheduler/
├── __init__.py
└── engine.py            ← ScheduleEngine（APScheduler）

workflows/
├── hello.yaml           ← 測試工作流
├── daily_news.yaml      ← 新聞日報工作流
└── schedules/
    ├── morning_hello.yaml
    └── daily_news.yaml  ← 每日 09:00 觸發
```

**關鍵產出：**
- WorkflowEngine：解析 YAML → 依序執行 Skill 步驟（含 timeout / retry / continue_on_error）
- ScheduleEngine：APScheduler cron 排程
- `daily_news.yaml`：scrape → render → send 三步驟

**步驟 YAML 支援的欄位：**

```yaml
steps:
  - id: scrape
    skill: news_scraper
    timeout: 30          # 秒，預設 60
    retries: 1           # 重試次數，預設 0
    continue_on_error: false  # 失敗是否繼續，預設 false
    params:
      config_path: "config/news_sources.yaml"
```

### 整合 Bot + Web + 排程（統一啟動）

Step 1-3 完成後，將 Bot、Web Server、排程引擎整合為一個啟動入口，一個指令跑起所有服務。

**更新 `src/server/main.py` lifespan：**

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 1. SkillRegistry
    registry = SkillRegistry()
    registry.auto_discover("src.skills.internal")

    # 2. WorkflowEngine
    workflow_engine = WorkflowEngine(registry)
    workflow_engine.load_dir(Path("workflows"))

    # 3. ScheduleEngine
    schedule_engine = ScheduleEngine(workflow_engine)
    schedule_engine.load_schedules(Path("workflows/schedules"))
    schedule_engine.start()

    # 4. Telegram Bot（有 token 才啟動）
    bot_app = None
    if os.getenv("TELEGRAM_BOT_TOKEN"):
        from src.bot.main import create_app
        bot_app = create_app()
        await bot_app.initialize()
        await bot_app.start()
        await bot_app.updater.start_polling(drop_pending_updates=True)

    yield

    # 關閉（反向順序）
    if bot_app:
        await bot_app.updater.stop()
        await bot_app.stop()
        await bot_app.shutdown()
    schedule_engine.stop()
```

**建立啟動 bat 檔 `start.bat`：**

```bat
@echo off
echo ══════════════════════════════════════
echo   ai-bot 啟動中...
echo ══════════════════════════════════════
echo.

REM 載入 .env（如果存在）
if exist .env (
    for /f "usebackq tokens=1,* delims==" %%a in (".env") do (
        if not "%%a"=="" if not "%%a:~0,1%"=="#" set "%%a=%%b"
    )
)

REM 啟動整合服務（Web + Bot + 排程）
echo [1/1] 啟動 Web + Bot + Scheduler...
py -m uvicorn src.server.main:app --host 127.0.0.1 --port 8000

pause
```

**驗證：**

```bash
# 雙擊 start.bat 或命令列執行
start.bat

# 預期輸出：
# Skills loaded: N
# Workflows loaded: N
# ScheduleEngine started (N jobs)
# Bot starting... (polling mode)
# Uvicorn running on http://127.0.0.1:8000
```

一個 bat 檔同時啟動：
- ✅ Web Server（http://127.0.0.1:8000）
- ✅ Telegram Bot（polling）
- ✅ 排程引擎（APScheduler cron）

> 🎉 **第一堂完成！** Bot 是「指令機器人」— 你說什麼它做什麼。接下來第二堂讓它變聰明。

---

## Step 4：Gemini API 對話（Bot 即時回應）

### 使用 Skill：`ark-llm-tools`

**觸發語句：** 「加入 Gemini API 對話能力，Bot /chat 用 API 即時回話」

**定位：** 讓 Bot 具備 AI 對話能力。使用 Gemini API（Python SDK）直接呼叫，回應速度 1-5 秒，適合即時對話場景。

**產出：**
```
src/llm/
├── __init__.py
└── gemini_chat.py       ← Gemini API 封裝（chat 專用）
```

**與 Step 6 的 Gemini CLI 分工：**

| | Step 4：Gemini API | Step 6：Gemini CLI |
|---|---|---|
| 呼叫方式 | `google-genai` Python SDK | subprocess `gemini -p` |
| 延遲 | 1-5 秒 | 5-30 秒 |
| 適用場景 | Bot /chat 即時對話 | 新聞結構化、codegen |
| 何時用 | 使用者在 TG 打字 | Workflow 自動化任務 |

### 取得 Gemini API Key（免費）

Gemini API 需要 `GEMINI_API_KEY`（Step 6 的 Gemini CLI 也共用此 Key）。

**申請步驟：**

1. 前往 https://aistudio.google.com/apikeys
2. 點擊「Create API Key」
3. 選擇或建立 Google Cloud 專案
4. 複製產生的 API Key

**設定方式：**

```bash
# 在 ai-bot/.env 中加入
GEMINI_API_KEY=your_actual_api_key_here
```

> 💡 免費額度：60 req/min、1,000 req/day，足夠開發測試使用。Step 6 的 Gemini CLI 也使用同一個 Key。

### 觸發產出

**在聊天框輸入：**

```
加入 Gemini API 對話能力，產出 src/llm/gemini_chat.py，
Bot /chat 指令和一般文字都用 Gemini API 即時回話
```

**Skill 產出 `src/llm/gemini_chat.py`：**

```python
from google import genai

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

async def chat(message: str, system_prompt: str = "") -> str:
    """呼叫 Gemini API 進行對話。"""
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=message,
        config={"system_instruction": system_prompt} if system_prompt else None,
    )
    return response.text
```

**Bot handlers 整合：**
- `/chat <問題>` → 呼叫 `gemini_chat.chat()`
- 一般文字 → 呼叫 `gemini_chat.chat()`
- 顯示「🤔 思考中...」→ 1-3 秒後更新為回應

**環境變數：**
```bash
GEMINI_API_KEY=your_api_key
```

**依賴：**
```
google-genai>=1.0.0
```

### 驗證方式

```bash
python -m src.bot.main
# Telegram 輸入 /chat 你是誰 → 1-3 秒內收到 AI 回應 ✅
# Telegram 直接輸入「什麼是 Python」→ 收到 AI 回應 ✅
```

> 💡 第一堂完成！Bot 能回應指令 + AI 能即時對話。

---

## Step 5：網頁爬蟲與素材處理

### 使用 Skill：`ark-web-scraper`

**📝 在 AI IDE 聊天框輸入：**

```
在 src/skills/internal/ 產出新聞爬蟲 Skill，
使用 httpx + BeautifulSoup，支援 CSS selector 設定，
產出結構化 Markdown 素材檔，來源設定參考 config/news_sources.yaml
```

**目標：** 抓取科技新聞網頁 → 解析 HTML → 產出 Markdown 素材檔，供 Step 6 的 Gemini CLI 結構化處理。

**💻 安裝依賴：**
```bash
pip install httpx beautifulsoup4
```

**產出：**
```
src/skills/internal/
├── news_scraper.py      ← 網頁爬蟲（httpx + CSS selector，多來源併發）
└── news_parser.py       ← 解析 → 結構化 Markdown

config/
└── news_sources.yaml    ← 新聞來源設定

output/news/raw/
└── 2026-05-29-general.md  ← Markdown 素材產出
```

### 可抓取的新聞來源

以下網站已驗證 httpx 可直接抓取（詳見 `ai-skill-hub-summary.md`）：

| 來源 | 網址 | 類別 | selector | 穩定度 |
|------|------|------|----------|--------|
| **Hacker News** | https://news.ycombinator.com/ | 綜合 | `.athing` + `.titleline a` | ⭐⭐⭐ 推薦 |
| TechCrunch AI | https://techcrunch.com/.../artificial-intelligence/ | AI 焦點 | `h3 a` | ⭐⭐ |
| Skills-Hub.ai | https://skills-hub.ai/ | AI Skills | `h3, .card-title` | ⭐⭐ |
| AgentSkillsHub.top | https://agentskillshub.top/ | AI Skills | `h3, .card-title` | ⭐⭐ |
| AgentSkillsHub.dev | https://agentskillshub.dev/ | AI Skills | `h3, .card-title` | ⭐⭐ |
| LobeHub Skills | https://lobehub.com/skills | AI Skills | `h3, .card-title` | ⭐⭐ |

> 💡 教學建議用 **Hacker News**（純 HTML，最穩定）。AI Skills 平台作為進階練習。

### 抓取策略

1. httpx 快速抓取（毫秒級，帶瀏覽器 User-Agent）
2. 多來源 `asyncio.gather` 併發抓取（Semaphore 限流 3 個）
3. 失敗來源記錄在 `result.data["failed_sources"]`，不中斷其他來源
4. 產出 Markdown 素材檔到 `output/news/raw/`

**news_sources.yaml 設定：**
```yaml
sources:
  # ── 科技新聞（推薦教學用）─────────────────────
  - name: "Hacker News"
    url: "https://news.ycombinator.com/"
    selector: ".athing"
    title_selector: ".titleline a"
    link_selector: ".titleline a"
    category: general

  - name: "TechCrunch AI"
    url: "https://techcrunch.com/category/artificial-intelligence/"
    selector: "h3"
    title_selector: "a"
    link_selector: "a"
    category: ai_focus

  # ── AI Skills 生態 ────────────────────────────
  - name: "Skills-Hub.ai"
    url: "https://skills-hub.ai/"
    selector: "h3, .card-title"
    category: ai_skills

  - name: "AgentSkillsHub.top"
    url: "https://agentskillshub.top/"
    selector: "h3, .card-title"
    category: ai_skills

schedule:
  cron: "0 8 * * *"
  timezone: "Asia/Taipei"
```

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

### Markdown 產出格式

每則新聞產出一個結構化區塊，供 Step 6 的 Gemini CLI 處理：

```markdown
---
source: Hacker News
date: 2026-05-29
category: general
url: https://www.anthropic.com/news/claude-opus-4-8
---

# Claude Opus 4.8

Anthropic 發布 Claude Opus 4.8，新增 dynamic workflow 工具...
```

### Workflow 串接（素材收集階段）

```yaml
# workflows/daily_news.yaml — 素材收集步驟
steps:
  - id: scrape
    type: skill
    skill: news_scraper
    params:
      config_path: "config/news_sources.yaml"
    output: raw_articles

  - id: parse
    type: skill
    skill: news_parser
    params:
      articles: "{{ outputs.raw_articles }}"
      output_dir: "output/news/raw/"
    output: markdown_files
```

> 💡 Step 5 產出的 Markdown 素材 = Step 6 的輸入。Gemini CLI 會把它結構化為日報 JSON。

**依賴：**
```
httpx>=0.27.0           # HTTP 請求
beautifulsoup4>=4.12.0  # HTML 解析
```

---

## 技術棧總結

| 層 | 技術 | 來源步驟 |
|----|------|---------|
| Bot + 對話 | python-telegram-bot 21+ / Session / 意圖路由 | Step 2 |
| API | FastAPI | Step 1 |
| Skills | BaseSkill + Registry + auto_discover | Step 1 |
| LLM 對話 | Gemini API（google-genai SDK） | Step 4 |
| LLM 結構化 | Gemini CLI（`gemini -p`）+ 4 後端 fallback | Step 6 |
| Workflow | YAML Engine（timeout / retry / continue_on_error） | Step 3 |
| 排程 | APScheduler | Step 3 |
| 爬蟲 | httpx + BS4 + Playwright（httpx 優先，併發抓取） | Step 5 |
| 日報渲染 | Jinja2 + HTML 模板 | Step 6 |

---

## 快速複製指南

```bash
# 0. 取得 Skills + 環境檢查
git clone https://github.com/igs-paddyyang-tw/ark-agent-skills .kiro/skills/
觸發 ark-env-doctor → 確認環境就緒

# 1. 產出骨架
觸發 ark-webapp-generator → project_name="my-bot"

# 2. 加入 Bot + 指令
觸發 ark-chatbot-generator → project_dir="my-bot"

# 3. 加入排程（選配）
觸發 ark-scheduler-generator → project_dir="my-bot"

# 4. 加入 Gemini API 對話
觸發 ark-llm-tools → 產出 src/llm/gemini_chat.py
# .env 設定 GEMINI_API_KEY
# Telegram /chat 你是誰 → 1-3 秒收到回應

# 5. 開發爬蟲 Skill
觸發 ark-web-scraper → 產出 news_scraper.py + news_parser.py

# 6. 科技日報實戰（Gemini CLI）
觸發 ark-llm-cli → 產出 llm_cli.py（結構化用）
# gemini -p 將 Markdown 素材 → 結構化 JSON → 套模板 → HTML

# 啟動
pip install -r requirements.txt
cp .env.example .env  # 填入 tokens
python -m src.bot.main
```

---

## Step 6：科技日報實戰（串接全部能力）

> 🎯 目標：5 分鐘內看到你的第一份科技日報 HTML 卡片，再逐步升級為全自動。

### 完整串接流程

```
structured-example.json（mock）或 Step 5 的 Markdown 素材
    │
    ├─ 6.1 直接用 mock ──→ news_renderer ──→ HTML 卡片 🎉
    │
    └─ 6.2 用 Gemini CLI ──→ 結構化 JSON ──→ news_renderer ──→ HTML 卡片
                                                    │
                                                    ▼ 6.3
                                            📱 Telegram /daily 一鍵觸發
```

### 6.1 秒出日報（不需 LLM，保證成功）

**📝 在 AI IDE 聊天框輸入：**

```
用 structured-example.json 的 mock 資料，
透過 news_renderer Skill 產出日報 HTML
```

**產出：** `output/tech-daily-news/tech-daily-{today}.html`

**驗證：** 瀏覽器開啟 → 看到 3 張精美卡片 🎉

> 💡 mock 資料使用線上圖片（placehold.co），不依賴本地檔案，100% 保證顯示。
> 圖片格式：`https://placehold.co/600x400/dde8ff/0d1b5e.png?text=標題`

**`structured-example.json` 圖片欄位：**
```json
"img_src": "https://placehold.co/600x400/dde8ff/0d1b5e.png?text=Gemini+Omni"
```

> ⚠️ 如果要用本地圖片，確保 HTML 與 `imgs/` 資料夾同層，路徑用相對路徑 `imgs/xxx.jpg`。

### 6.2 Gemini CLI 或 Kiro CLI 結構化（選配，二擇一）

#### 使用 Skill：`ark-llm-cli`

**📝 在 AI IDE 聊天框輸入：**

```
封裝 Gemini CLI 為 Skill，用於新聞結構化處理
```

**Skill 產出：** `src/skills/internal/llm_cli.py`（如已存在則跳過）

**與 Step 4 的 Gemini API 分工：**

| | Step 4：Gemini API | Step 6：Gemini CLI / Kiro CLI |
|---|---|---|
| 呼叫方式 | `google-genai` SDK | subprocess CLI |
| 延遲 | 1-5 秒 | 5-120 秒 |
| 用途 | Bot /chat 即時對話 | 新聞結構化、codegen |
| 為什麼用 CLI | — | 可處理長文、支援複雜 prompt |

#### 方案 A：Gemini CLI（快速，需要額度）

**💻 在終端機執行：**
```bash
gemini -p "你是科技日報編輯。請將以下新聞素材轉化為結構化 JSON，格式：
{topic, title, img_src, source, news_date, what, why, summary, tags[{icon,text}]}
關鍵詞用 <span class=\"hl\">包裹</span>

素材：
（貼上 output/news/raw/ 的 Markdown 內容）" --skip-trust
```

#### 方案 B：Kiro CLI（不需要額度，用 Kiro IDE 授權）

**💻 在終端機執行：**
```bash
kiro-cli chat --trust-all-tools --legacy-ui --message "你是科技日報編輯。請將以下新聞素材轉化為結構化 JSON，格式：{topic, title, img_src, source, news_date, what, why, summary, tags[{icon,text}]}。關鍵詞用 <span class='hl'>包裹</span>。素材：（貼上 output/news/raw/ 的內容）"
```

#### 兩者比較

| | Gemini CLI | Kiro CLI |
|---|---|---|
| 安裝 | `npm i -g @google/gemini-cli` | `npm i -g kiro-cli` |
| 授權 | `GEMINI_API_KEY` + Gmail 登入 | AWS 登入（`kiro-cli login`） |
| 額度 | 1,000 req/day（免費） | 無明確限制 |
| 延遲 | 5-15 秒 | 30-120 秒（內部多輪工具呼叫） |
| 適合 | 快速結構化、codegen | Gemini 額度用完時的備案 |
| 特殊能力 | — | 完整 Agent + MCP 工具呼叫 |

#### 注意事項

| 問題 | Gemini CLI 解法 | Kiro CLI 解法 |
|------|----------------|--------------|
| 額度用完（429） | 跳過或等隔天 | 改用 Kiro CLI |
| 503 高需求 | 改用 `-m gemini-1.5-flash` | 不受影響 |
| 信任目錄錯誤 | `--skip-trust` | 不需要 |
| Windows 路徑 | `create_subprocess_shell` | 同左 |
| 未安裝 | `npm i -g @google/gemini-cli` | `npm i -g kiro-cli` + `kiro-cli login`（AWS 授權） |

→ 產出結構化 JSON → 存檔 → 再跑 `news_renderer` → 真實新聞日報

> ⚠️ 兩個都不行？沒關係，6.1 的 mock 日報一樣是完整成品。

### 6.3 Telegram 一鍵觸發

**📱 在 Telegram 輸入：**
```
/daily
```

→ Bot 自動跑完 scrape → structure → render → 發送 HTML 檔案

### 新增檔案

```
templates/
└── tech-daily.html          ← 科技日報卡片模板（860px 淺藍白色系）

src/skills/internal/
├── llm_cli.py               ← Gemini CLI 封裝（結構化用）
└── news_renderer.py         ← 套用模板產出 HTML

output/tech-daily-news/
└── tech-daily-{today}.html  ← 產出結果
```

### HTML 模板變數

| 變數 | 說明 | 範例 |
|------|------|------|
| `{{DATE}}` | 日報日期 | `2026.05.25` |
| `{{TOPIC}}` | 焦點分類 | `AI 焦點` |
| `{{TITLE}}` | 新聞標題（15 字內） | `Gemini Omni 登場` |
| `{{IMG_SRC}}` | 封面圖（URL 或相對路徑） | `https://placehold.co/600x400/...` |
| `{{SOURCE}}` | 新聞來源 | `Google 官方部落格` |
| `{{NEWS_DATE}}` | 新聞原始日期 | `2026-05-25` |
| `{{WHAT}}` | 發生了什麼 | 100 字內，關鍵詞 `<span class="hl">` 標紅 |
| `{{WHY}}` | 為什麼重要 | 80 字內影響分析 |
| `{{SUMMARY}}` | 一句話總結 | 15 字內 |
| `{{TAG1_ICON}}` / `{{TAG1_TEXT}}` | 啟發標籤 | `🎬` / `影片製作門檻大降` |
| `{{PAGE}}` | 頁碼 | `1 / 3` |

### LLM 結構化 Prompt

```
你是科技日報編輯。請將以下新聞素材轉化為結構化格式：

新聞素材：
{Step 5 產出的 Markdown 內容}

請產出：
1. TOPIC：焦點分類（如 AI 焦點、開發工具、硬體趨勢）
2. TITLE：10 字內吸睛標題
3. WHAT：「發生了什麼」— 100 字內白話摘要，關鍵詞用 <span class="hl">包裹</span>
4. WHY：「為什麼重要」— 80 字內影響分析，關鍵詞標紅
5. SUMMARY：一句話總結（15 字內）
6. TAGS：3 個「對團隊的啟發」標籤（emoji + 8 字內文字）
```

### 驗收條件

- [ ] 6.1：mock 資料 → HTML 卡片正確顯示（圖片、標紅、頁碼）✅
- [ ] 6.2：Gemini CLI 結構化產出符合模板變數格式（選配）
- [ ] 6.3：📱 Telegram `/daily` 收到 HTML 檔案
- [ ] 多則新聞可堆疊多張卡片

> 🎉 **第二堂完成！** 你的 AI Agent 能自動產出科技日報了。

---

## Step 7：🚧 單兵瓶頸體驗（選讀，5 分鐘）

> **目標：** 親身感受「一個 Agent 全做」的天花板，理解為什麼需要 Agent Team。

### 7.1 並行測試 — 序列阻塞

📱 在 Telegram 快速連發三則訊息：

```
幫我查今天的科技新聞
翻譯這段：The future of AI is agentic
寫一個 Python 計時器腳本
```

**觀察：**
- Bot 一次只能處理一則（序列排隊）
- 第三則可能等 30 秒以上才回應
- 如果第一則（爬蟲）卡住 → 後面全部阻塞

### 7.2 單點故障 — 一掛全掛

💻 模擬爬蟲掛掉：

```bash
# 把 news_sources.yaml 的 URL 改成一個不存在的網址
# 然後 Telegram 輸入「今天新聞」
# → 整個 Bot 卡在 timeout，其他功能也被阻塞
```

### 7.3 擴充成本 — 改一處動全身

如果你想加入新能力（例如「程式碼審查」）：

```
1. 寫新的 Skill → src/skills/internal/code_review.py
2. 改 planner.py 的路由邏輯 → 加關鍵字
3. 改 handlers.py → 加處理邏輯
4. 重啟整個 Bot → 所有功能短暫中斷
```

每加一個能力 = 修改 3 個檔案 + 重啟服務。10 個能力後 planner.py 變成一團 if-else 麵條。

### 7.4 問題分兩步解決

| 維度 | 01 的痛點 | 02 Skills 開發解決 | 04 Agent Team 解決 |
|------|----------|-------------------|-------------------|
| 能力擴充 | 改 3 檔 + 重啟 | ✅ Spec-Driven 標準化開發 | — |
| 品質保障 | 手寫無規格 | ✅ Code-Spec 驗證一致性 | — |
| 並行能力 | ❌ 序列（一次一個） | — | ✅ 5 Agent 並行 |
| 故障隔離 | ❌ 一掛全掛 | — | ✅ 一個掛不影響其他 |
| 科技日報 | 一人做到死 | ✅ 拆成獨立 Skill | ✅ 各 Agent 各司其職 |

### 7.5 預告：下一堂先解決「能力擴充難」

```
Workshop 02 — Skills 開發：
拷問設計 → 產出 Spec → 依 Spec 實作 → 驗證一致性 → Ship
```

你的 Bot 只有 echo + news 兩個硬編碼技能。02 教你用 Spec-Driven 開發 → 無限擴充技能。04 才處理多人並行。

> 📌 你在 01 做的所有東西（Skills、Planner、Gemini Chat）不會白費——
> 02 教你用標準化方式開發新 Skill，讓 Bot 立刻獲得新能力。
> 
> 🔜 **下堂課（02）**：拷問設計 → Spec → 實作 → 驗證，完整 Spec-Driven 開發迴圈。

---

## 附錄：科技日報機器人 — 完整規格

> 本節為 Step 6 實戰練習的完整系統規格，供正式開發參考。

### 系統定位

自動化科技日報產出機器人：定時抓取 AI/科技新聞 → LLM 結構化摘要 → HTML 卡片渲染 → Telegram 推送。

### 架構圖

```
┌─────────────────────────────────────────────────────────────────┐
│                     科技日報機器人架構                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  [Telegram Bot]                                                   │
│       │                                                           │
│       ├── /news <url>  ──→ 即時單篇產出                           │
│       ├── /daily       ──→ 手動觸發日報                           │
│       └── /config      ──→ 查看排程設定                           │
│                                                                   │
│  [排程引擎] APScheduler                                           │
│       │                                                           │
│       └── cron 0 9 * * * ──→ 觸發 daily_news workflow            │
│                                                                   │
│  [Workflow Pipeline]                                              │
│       │                                                           │
│       ├── 1. scrape    ──→ httpx + Playwright 抓取網頁            │
│       ├── 2. parse     ──→ BeautifulSoup 解析 → Markdown          │
│       ├── 3. structure ──→ Gemini CLI 結構化摘要                  │
│       ├── 4. render    ──→ Jinja2 套用 HTML 模板                  │
│       └── 5. send      ──→ Telegram 發送檔案/圖片                 │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

### 新聞來源（建議清單）

| 來源 | 網址 | 類別 | 抓取方式 | 備註 |
|------|------|------|---------|------|
| Hacker News | https://news.ycombinator.com/ | 綜合 | httpx ✅ | 最穩定，推薦教學用 |
| TechCrunch AI | https://techcrunch.com/category/artificial-intelligence/ | AI 焦點 | httpx ✅ | 部分內容需 JS |
| Skills-Hub.ai | https://skills-hub.ai/ | AI Skills | httpx ✅ | 4,700+ Skills 聚合 |
| AgentSkillsHub.top | https://agentskillshub.top/ | AI Skills | httpx ✅ | 70K+ 最大目錄 |
| AgentSkillsHub.dev | https://agentskillshub.dev/ | AI Skills | httpx ✅ | A-F 安全評級 |
| LobeHub Skills | https://lobehub.com/skills | AI Skills | httpx ✅ | SKILL.md 格式 |
| SkillsMP.com | https://skillsmp.com/ | AI Skills | httpx ✅ | 職業分類篩選 |

> 💡 以上網站皆已驗證 httpx 可直接抓取。The Verge / Google AI Blog 需要 Playwright（JS 渲染）。

### Bot 指令規格

| 指令 | 參數 | 說明 | 回應 |
|------|------|------|------|
| `/news <url>` | 網址 | 即時抓取單篇 → HTML 卡片 | 發送 HTML 檔案 |
| `/daily` | 無 | 手動觸發完整日報流程 | 發送多卡片 HTML |
| `/config` | 無 | 顯示排程設定與來源清單 | 文字訊息 |
| `/add_source <url> <name>` | 網址 + 名稱 | 新增新聞來源 | 確認訊息 |

### 資料流規格

```
Input:  網頁 HTML
    ↓ news_scraper.py
Output: raw HTML content (str)
    ↓ news_parser.py
Output: Markdown 素材檔 (output/news/raw/*.md)
    ↓ news_structurer.py (呼叫 Gemini CLI)
Output: 結構化 JSON (output/news/structured/*.json)
    ↓ news_renderer.py (Jinja2)
Output: HTML 卡片 (output/tech-daily-news/tech-daily-YYYY-MM-DD.html)
    ↓ telegram_send_file.py
Output: Telegram 訊息（檔案或圖片）
```

### 結構化 JSON Schema

```json
{
  "date": "2026.05.25",
  "cards": [
    {
      "topic": "AI 焦點",
      "title": "Gemini Omni 登場",
      "img_src": "imgs/gemini-omni.jpg",
      "img_alt": "Gemini Omni",
      "source": "Google 官方部落格",
      "news_date": "2026-05-25",
      "what": "Google 發布 <span class=\"hl\">Gemini Omni</span> 模型...",
      "why": "開發者可用<span class=\"hl\">單一 API</span> 處理四種模態...",
      "summary": "多模態 AI 進入統一時代",
      "tags": [
        { "icon": "🎬", "text": "影片製作門檻大降" },
        { "icon": "💬", "text": "自然語言取代剪輯" },
        { "icon": "✨", "text": "電影級效果普及化" }
      ]
    }
  ]
}
```

### 環境變數

```bash
# .env
TELEGRAM_BOT_TOKEN=your_bot_token      # @BotFather 取得
TELEGRAM_CHAT_ID=your_chat_id          # 推送目標群組/頻道
NEWS_SCHEDULE_CRON=0 9 * * *           # 排程時間（預設每日 09:00）
NEWS_TIMEZONE=Asia/Taipei              # 時區
LLM_BACKEND=gemini                     # 預設 LLM 後端
```

### 依賴清單

```
# requirements.txt（Step 6 新增）
httpx>=0.27.0
beautifulsoup4>=4.12.0
playwright>=1.40.0
jinja2>=3.1.0
python-telegram-bot>=21.0
apscheduler>=3.10.0
```

### 錯誤處理

| 錯誤場景 | 處理方式 |
|---------|---------|
| 網頁抓取失敗（timeout/403） | 跳過該來源，繼續其他來源，最終報告失敗數 |
| LLM 結構化格式錯誤 | 重試 1 次，仍失敗則用 fallback 模板（僅標題+摘要） |
| Gemini CLI 額度用盡 | 切換到 fallback 後端（claude/本地模型） |
| 圖片下載失敗 | 使用預設 placeholder 圖片 |
| Telegram 發送失敗 | 重試 3 次，間隔 5s，仍失敗則存檔等待手動發送 |

### 效能預算

| 指標 | 目標 |
|------|------|
| 單篇抓取 + 解析 | < 10s |
| LLM 結構化（單篇） | < 15s |
| HTML 渲染 | < 1s |
| 完整日報（5 篇） | < 3 min |
| 記憶體使用 | < 256MB |

### 擴展方向

- **多語言**：加入英文來源，LLM 翻譯為中文摘要
- **歷史存檔**：SQLite 存儲歷史日報，支援 `/history` 查詢
- **訂閱機制**：使用者可選擇關注的類別（AI/硬體/開發工具）
- **圖片自動化**：Playwright screenshot 或 html2png.dev 轉 PNG
- **RSS 整合**：支援 RSS feed 作為新聞來源

---

*產出日期：2026-05-25*
