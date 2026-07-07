---
title: "AI Bot 系統設計架構"
type: architecture
status: current
created: 2026-07-07
---

# AI Bot 系統設計架構

## 一句話定位

個人 AI Agent 專家開發平台 — 打造各種 Agent 專家 + 管理知識庫。

---

## 系統架構圖

```
┌─────────────────────────────────────────────────────────────────┐
│                        使用者介面                                 │
├──────────┬──────────┬────────┬────────┬──────────┬──────────────┤
│ 💬 Chat  │⚙️ Dashboard│📖 Wiki │🕸️ Graph│🏗️ Builder│ 📡 API Docs │
│ /        │ /admin    │ /wiki  │ /graph │ /builder │ /api-docs    │
├──────────┴──────────┴────────┴────────┴──────────┴──────────────┤
│                     FastAPI (port 8000)                           │
│  /api/v1/chat │ /api/v1/wiki/* │ /api/v1/graph │ /health        │
├─────────────────────────────────────────────────────────────────┤
│                     Telegram Bot（獨立子進程）                     │
│  handlers.py → Planner L1-L4 → 回覆 + Reaction                  │
├──────────┬──────────────────────────────────────────────────────┤
│          │              對話路由（Planner）                       │
│          │  L1: /reset → 清空 session                            │
│          │  L2: /skill_id args → 直接執行 Skill                  │
│          │  L3: keyword → Planner 路由表                         │
│          │  L4: CLI → Wiki RAG → Memory → Gemini → 兜底         │
├──────────┼──────────────────────────────────────────────────────┤
│          │              回覆處理                                  │
│          │  _clean_output → 截斷 3000 → 分段 4000 → 標頭 + 📚   │
│          │  _keep_action_alive（持續 typing）                    │
│          │  _set_reaction（👀→🔥→👍/💔）                        │
├──────────┴──────────────────────────────────────────────────────┤
│                     核心服務層                                     │
├─────────────┬─────────────┬─────────────┬───────────────────────┤
│ AgentProcess│  WikiEngine │   Memory    │   Gemini Chat         │
│ 8 Agent 常駐│  兩層 RAG   │  搜尋注入   │   SOUL + context      │
├─────────────┼─────────────┼─────────────┼───────────────────────┤
│ kiro/gemini │ 私有→全域   │ raw/ 搜尋   │ gemini-2.5-flash      │
│ /claude     │ bigram 分詞 │ 注入 system │ + fallback chain      │
├─────────────┴─────────────┴─────────────┴───────────────────────┤
│                     資料層                                        │
├─────────────────────────────────────────────────────────────────┤
│ knowledge/                    agents/                             │
│ ├── raw/    （原料）          ├── admin-agent/                   │
│ ├── wiki/   （成品，RAG 用）  │   ├── .kiro/steering/SOUL.md    │
│ ├── index.md（索引）          │   ├── skills/ark-*/SKILL.md     │
│ ├── schema.md（規則）         │   └── knowledge/raw/（私有記憶）  │
│ └── log.md  （操作日誌）      ├── market-agent/                  │
│                               ├── ...（共 8 個）                  │
│ .kiro/skills/（5 個 IDE Skill）└── report-agent/                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 啟動架構

```
python start.py
├── 主進程：uvicorn（FastAPI，port 8000，reload=True）
│   └── Web UI 6 頁 + API endpoints
└── 子進程：python -m src.bot.run
    ├── TG Bot polling
    ├── AgentProcess × 8（如果有 kiro-cli）
    └── 獨立 event loop + logging
```

---

## 對話路由（handlers.py）

```
使用者訊息
│
├── 👀 Reaction
├── L1: /reset → session.clear_history()
├── L2: /news /wiki /summarize /translate /ingest → _execute_skill_by_id()
├── L3: Planner keyword 路由 → IntentType.SKILL / WIKI / CHAT
│
├── 🔥 Reaction + _keep_action_alive(typing)
│
├── L4a: AgentProcess.send()（CLI 常駐，優先）
├── L4b: WikiEngine.query()（兩層 RAG）
├── L4c: _search_memory()（歷史記憶注入）
├── L4d: gemini_chat()（SOUL + Memory + 歷史）
├── L4e: 兜底回覆
│
├── _clean_output()（ANSI + 工具噪音 + 結論提取）
├── 截斷 3000 + 分段 4000
├── 👍/💔 Reaction
└── header + reply
```

---

## 知識庫架構（WikiEngine）

### 兩層查詢

```
query(text)
  → 1. 搜尋私有 wiki：agents/{agent}/knowledge/wiki/
  → 2. 搜尋全域 wiki：knowledge/wiki/
  → 合併結果（私有優先）
  → Gemini RAG 合成答案（讀完整文件，每篇 2000 字，最多 5 篇）
```

### Ingest 流程

```
ingest()
  → 掃 raw/（限 2 層深度）
  → 比對 mtime（wiki 版本不比 raw 舊 → 跳過）
  → 補 frontmatter → 寫入 wiki/
  → _update_index()（分類版）
  → _append_log()（有變動才追加）
```

### 搜尋（中文 bigram）

```
_tokenize("老虎機市場趨勢")
  → ["老虎", "虎機", "機市", "市場", "場趨", "趨勢"]
  → any(kw in content) → 命中
```

---

## AgentProcess（對齊 ai-team-agent）

```
AgentProcess
├── name: "admin-agent"
├── working_dir: "agents/admin-agent"
├── model: "auto"（不傳 --model）
├── backend: "kiro" | "gemini" | "claude"
├── timeout: 180s
├── _queue: asyncio.Queue[(text, Future)]
└── _worker_task: 持續消費 queue

send(text) → Future 等待 → worker 執行 → 回傳結果
（忙碌時排隊，不 fallback 到 Gemini）
```

---

## Web UI（6 頁）

| 頁面 | URL | 功能 |
|------|-----|------|
| Chat | `/` | 8 Agent 切換 + 對話（POST /api/v1/chat） |
| Dashboard | `/admin` | KPI + Agent 列表 + 知識庫摘要 + Ingest/Lint |
| Wiki | `/wiki` | 樹狀側欄 + 搜尋 + Markdown 渲染 + frontmatter |
| Graph | `/graph` | 三層力導向圖譜（Agent→Skill→Wiki） |
| Builder | `/builder` | SOUL 編輯 + 知識綁定 + 預覽對話 |
| API Docs | `/api-docs` | 暗黑風 + Try 按鈕 |

---

## API Endpoints

| Method | Path | 功能 |
|--------|------|------|
| GET | `/health` | 健康檢查 |
| POST | `/api/v1/chat` | 統一對話（走完整路由） |
| GET | `/api/v1/skills` | 列出 internal skills |
| GET | `/api/v1/wiki/pages` | 列出 wiki 頁面（樹狀） |
| GET | `/api/v1/wiki/pages/{path}` | 取得頁面內容 |
| POST | `/api/v1/wiki/query` | Wiki 搜尋 |
| POST | `/api/v1/wiki/ingest` | 匯入 raw→wiki |
| GET | `/api/v1/wiki/lint` | 健康檢查 |
| GET | `/api/v1/graph` | 知識圖譜資料 |

---

## Telegram Bot

### 指令選單（10 項）

| 指令 | 功能 |
|------|------|
| /start | 啟動 + 清歷史 |
| /agents | 切換 Agent（Inline Button） |
| /news | 📰 抓新聞 |
| /wiki | 📚 查知識庫 |
| /summarize | 📝 摘要 |
| /translate | 🌐 翻譯 |
| /ingest | ⬆️ 匯入知識 |
| /mode | 查看模式 |
| /history | 對話歷史 |
| /help | 指令說明 |

### 互動回饋

```
👀 收到 → 🔥 處理中（持續 typing）→ 👍 完成 / 💔 失敗
回覆標頭：🗺️ [market-agent]
```

---

## Kiro IDE Skills（5 個）

| Skill | 教學用途 |
|-------|---------|
| ark-grill-me | 02：拷問設計 |
| ark-superpowers | 02：產出 Spec |
| ark-skill-creator | 02：產出 SKILL.md |
| ark-code-spec-validator | 02：驗證 Score |
| ark-wiki-engine | 03：知識庫操作（API/Python/LLM 三模式） |

---

## 檔案結構

```
ai-bot/
├── start.py                     ← 一鍵啟動（主進程 API + 子進程 Bot）
├── .env.example                 ← 環境變數（有註解）
├── start_bot.bat / stop / restart ← Windows 管理
├── .kiro/
│   ├── steering/SOUL.md         ← 根 SOUL（fallback）
│   └── skills/（5 個 IDE Skill）
├── agents/（8 個 Agent）
│   └── {name}-agent/
│       ├── .kiro/steering/SOUL.md
│       ├── skills/ark-*/SKILL.md
│       └── knowledge/raw/（私有記憶）
├── knowledge/（全域知識庫）
│   ├── raw/ → wiki/ → index.md → log.md → schema.md
├── templates/（6 頁 Web UI）
├── src/
│   ├── agent/（process + cli + session + memory + planner）
│   ├── bot/（main + handlers + run）
│   ├── skills/internal/（echo + news + summarize + translate）
│   ├── wiki/（engine — 兩層 + bigram + ingest + lint）
│   ├── llm/（gemini_chat）
│   ├── server/（FastAPI + 路由）
│   └── logging_config.py
├── logs/
├── config/
└── docs/
```

---

## Tier 分級

| Tier | 條件 | 能力 |
|------|------|------|
| 0 | 零設定 | Skills + Wiki + API + Web UI |
| 1 | + TG Token | Bot + Inline Button + Reaction + 8 Agent |
| 2 | + Gemini Key | AI 對話 + RAG + SOUL 人格 |
| 3 | + kiro-cli | 8 Agent 常駐服務（完整 .kiro/ 配置） |
