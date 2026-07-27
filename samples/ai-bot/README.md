# ai-bot — 🏗️ AI Agent 專家系統平台

> 9 Agent + 四層搜尋 Wiki + Ark Agent 自動派工 + Web UI 6 頁 + Telegram 互動。帶走就能用。

## 前置需求

- Python 3.12+

## 快速啟動

```bash
# macOS / Linux
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # 填入 TELEGRAM_BOT_TOKEN + GEMINI_API_KEY
python start.py

# Windows
start_bot.bat
```

啟動成功畫面：
```
══════════════════════════════════════════════════
  🤖 AI Agent 專家開發平台
══════════════════════════════════════════════════
  Tier 0: ✅ Prompts + Skills + Wiki + MCP（永遠可用）
  Tier 1: ✅ Telegram Bot
  Tier 2: ✅ Gemini AI + RAG
  Tier 3: ✅ Agent CLI 常駐
══════════════════════════════════════════════════

  📦 Skills: IDE 6 | Internal 15
  📚 Wiki:   shared 12 | raw 5 | agents 28
  🔍 Lint:   ✅ 0 issues
  🧠 SOUL:   ✅ 已載入
  🔍 自檢:   ✅ 8 Agent steering + memory 完整
  🧹 Output: ✅ 無過期檔案
  🧠 Memory: daily 5d | memory.md ~120 words
  🤖 Bot:    @your_bot_name 已連線
  🧠 Agent:  8 active (Agent CLI)
  📌 個體模式（無 team.yaml）

  ── Web UI ──────────────────────────────────────
  💬 Chat:      http://localhost:8000
  ⚙️  Dashboard: http://localhost:8000/admin
  📖 Wiki:      http://localhost:8000/wiki
  🕸️  Graph:     http://localhost:8000/graph
  🏗️  Builder:   http://localhost:8000/builder

  ── API ─────────────────────────────────────────
  📡 API Docs:  http://localhost:8000/api-docs
  ❤️  Health:    http://localhost:8000/health

  ⏱️  Ready in 2.3s
```

---

## Web UI（6 頁）

| URL | 頁面 | 功能 |
|-----|------|------|
| `/` | 💬 Chat | 聊天室 — 8 Agent 切換 + Wiki 查詢 |
| `/admin` | ⚙️ Dashboard | KPI + Agent 列表 + 知識庫管理 |
| `/wiki` | 📖 Wiki | 瀏覽器 — 段落搜尋 + 關鍵字高亮 |
| `/graph` | 🕸️ Graph | 知識圖譜 — Agent→Skill→Wiki 力導向圖 |
| `/builder` | 🏗️ Builder | SOUL 編輯 + 知識綁定 + 預覽對話 |
| `/api-docs` | 📡 API | API 文件 + Try 按鈕 |

---

## 三層知識庫

```
knowledge/
└── shared/                         ← 全 Agent 共用
    ├── raw/                        ← 原始素材（AI 只讀不改）
    ├── wiki/                       ← 結構化知識（四層搜尋）
    ├── .index/                     ← 搜尋索引（自動生成）
    ├── schema.md + index.md + log.md

agents/{name}-agent/knowledge/      ← Agent 私有
├── raw/                            ← 記憶寫入處
├── wiki/                           ← 私有知識頁面
├── schema.md + index.md + log.md
```

查詢優先順序：**私有 → shared → {project}**

### 四層搜尋金字塔

```
Layer 3: LLM Rerank（有 Gemini 時啟用）
Layer 2: 語意向量 + 圖譜擴散 + RRF 融合
Layer 1: BM25 持久化索引（jieba + bigram 保險絲）
Layer 0: Metadata 精確 + 子字串兜底（永不掛零）
```

---

## 8 個 Agent（每個都有 SOUL + Skills + Wiki）

| Agent | 角色 | Wiki 知識 |
|-------|------|-----------|
| 👑 Admin | 服務管理、部署、費控 | 5 頁（SOP、部署、監控、費控、故障排除） |
| 🧠 PM | 需求分析、派工、驗收 | 5 頁（需求、派工、驗收、SDD、溝通） |
| 🤖 AI Dev | LLM/Prompt/MCP/Agent 設計 | 4 頁（Prompt、RAG、MCP、Agent 模式） |
| 💻 Coder | 全端開發、API、DB | 4 頁（Python 規範、API、DB、Review） |
| 🧪 QA | 測試、Review、品質 | 4 頁（測試策略、Review、CI/CD、Bug） |
| 📊 Data | 數據分析、KPI 追蹤 | 1 頁（分析方法論） |
| 🗺️ Market | 競品監控、市場研究 | 1 頁（研究方法） |
| 📝 Report | 報告產出、圖表渲染 | 1 頁（報告規範） |

---

## A2A 跨機協作

```
沒有 team.yaml → 個體模式（課程 A）
有 team.yaml  → 團隊模式（本地派工）
team.yaml 含 transport: http → 跨機模式（遠端派工）
```

### TG 團隊指令

| 指令 | 功能 |
|------|------|
| `/assign 描述` | PM discovery 選人 → 派工 |
| `/board` | 看任務狀態 |
| `派工 描述` | 自然語言派工 |

### A2A API

| Method | Path | 功能 |
|--------|------|------|
| POST | `/api/v1/a2a/task` | 接收派工 |
| POST | `/api/v1/a2a/callback` | 接收回報 |
| GET | `/api/v1/a2a/card` | Agent Card |

---

## Telegram 互動

### 指令

| 指令 | 功能 |
|------|------|
| `/start` | 啟動 + 系統資訊（Chat ID / LLM / CLI） |
| `/status` | 系統狀態（LLM / CLI backend / 路由模式） |
| `/agents` | Inline Button 選 Agent（常駐面板，✅ 標示當前） |
| `/chat <問題>` | 強制 Gemini API（帶 6 層完整 context，2-3s） |
| `/recall <query>` | 查詢 Agent 歷史經驗（FTS5） |
| `/skills` | 列出已生效 Skills |
| `/skills pending` | 待審 Skill 提案 |
| `/consolidate` | 手動蒸餾 daily → memory.md |
| `/mode` | 執行模式（agy / Gemini） |
| `/assign <描述>` | 派工給團隊 Agent |
| `/board` | 任務看板 |
| `/help` | 指令清單 |

### 對話模式

| 模式 | 觸發 | 後端 | Context |
|------|------|------|---------|
| 自然對話（Default） | 直接打字 | Gemini ReAct Agent Loop | SOUL + BRAIN + memory + recall + wiki + skills + tools |
| 快問快答 | `/chat 問題` | Gemini ReAct Agent Loop | 同上（帶 Function Calling） |
| Agent 分身 | `/agents` 切換 | Agent CLI | 完整 .kiro/ workspace |
| Skill 執行 | `/skill_id` 或關鍵字 | 本地 Python | Skill 內部邏輯 |

### 對話路由架構（三路徑）

```
使用者發訊息
     │
     ▼
Path 1: /command → CommandHandler
     │ 公開：/start /status /help
     │ 白名單：/agents /recall /skills
     ▼
Path 2: @agent-name msg → 強制指定 Agent（白名單）
     │ 解析 target → Agent CLI 送出
     ▼
Path 3: 自然語言 → Ark Agent（白名單）
     │
     🚀 Ark Agent（Gemini ReAct, max 5 iterations）
     │
     ├── 簡單問答 → 直接回覆（不派工）
     └── 需要專業處理 → dispatch_to_agent(target, task)
          │
          ├── coder-agent（程式碼、API、DB）
          ├── ai-dev-agent（Prompt、RAG、MCP）
          ├── data-agent（數據分析、KPI）
          ├── market-agent（競品、市場研究）
          ├── report-agent（報告產出）
          ├── qa-agent（測試、Review）
          └── admin-agent（部署、費控、SOP）
```

| 路徑 | 觸發 | 速度 | 用途 |
|------|------|------|------|
| /command | 斜線指令 | 即時 | 系統操作 |
| @mention | `@agent-name msg` | 15-20s | 強制指定 Agent |
| 自然語言 | 直接打字 | 3-120s | Ark Agent 判斷 + 自動派工 |

### Gemini ReAct Agent（Default 模式）

Default 模式具備 Tool Calling 能力（Function Calling + ReAct 迴圈）：

```
使用者訊息 → context_builder 組裝 System Prompt → Provider.chat（帶 tools）
     ↓
有 function_call? → dispatch tool → 結果回傳 → 再呼叫 LLM → ...（max 5 次）
     ↓
純文字回覆 → 回覆使用者 → 寫 daily log
```

**可用 Tools（7 個）：**

| Tool | 功能 | 說明 |
|------|------|------|
| `search_wiki` | 搜尋知識庫 | 四層搜尋（exact → BM25 → hybrid → substring 兜底） |
| `web_search` | 搜尋外部網路 | Gemini Grounding + Google Search（查無 wiki 時自動觸發） |
| `dispatch_to_agent` | 派工給專業 Agent | Hub-and-Spoke：Ark Agent → 7 個 Agent（CLI 執行） |
| `save_to_wiki` | 寫入知識庫 | 寫入 wiki/ + 自動 rebuild_index（metadata + BM25） |
| `recall_memory` | 查歷史記憶 | FTS5 查詢 memory + shared wiki |
| `save_memory` | 記錄持久事實 | append 到 `memory/memory.md` |
| `execute_skill` | 載入 Skill | 讀取 SKILL.md → LLM 按步驟執行 |

**搜尋流程（強制，不可跳過）：**
```
search_wiki → 有結果 → 回答（📚 參考）
           → 查無 → web_search → 有結果 → 回答（🔗 來源）
                              → 查無 → 「📚 知識庫與外部搜尋皆無相關資料」
```

### Memory / Wiki / Output 三區分工

| 區域 | 路徑 | 內容 | 誰寫 |
|------|------|------|------|
| Memory | `memory/daily/` + `memory.md` + `recent.md` | 對話記錄、持久事實 | 系統自動 |
| Wiki | `knowledge/*/wiki/` | 結構化知識 | 使用者明確要求（先進 raw/ 再 ingest） |
| Output | `output/{category}/` | 報告、匯出、草稿 | 使用者要求 |

**Output 分類：**
```
output/
├── reports/    ← 報告（.md / .html）
├── skills/     ← Skill 產出
├── exports/    ← 匯出資料（.csv / .json）
└── drafts/     ← 草稿
```

### Reaction + ProgressStack

```
👀 收到 → ProgressStack（⏳→✅→完成） → 👍 完成 / 👎 失敗
```

派工時使用者看到堆疊式進度更新（單一訊息 edit）：
```
🚀 [Ark Agent]

✅ 分析意圖中
✅ 查詢知識庫
⏳ 派工中...
```

---

## 專案結構

```
ai-bot/
├── start.py                        ← 一鍵啟動（含自檢）
├── start_bot.bat / stop_bot.bat    ← Windows
├── agents.yaml                     ← Agent 定義檔（唯一來源）
├── .env.example
├── requirements.txt
├── data/                           ← 運行資料
│   ├── memory.db                   ← FTS5 統一索引
│   └── proposals.json              ← Skill 審批狀態
├── .kiro/
│   ├── steering/SOUL.md + BRAIN.md + MEMORY.md + TEAM.md
│   ├── agents/ai-agent.json        ← AI Agent 開發助手
│   ├── prompts/route-message.md    ← 意圖路由
│   └── skills/ark-wiki-engine/ + ark-superpowers/ + ark-grill-me/ + ...
├── agents/                         ← 8 Agent（.kiro/ + knowledge/ + memory/）
│   └── {name}-agent/
│       ├── .kiro/steering/         ← SOUL + BRAIN + MEMORY + TEAM
│       ├── .kiro/skills/           ← 程序記憶（審批後落地）
│       ├── memory/                 ← 情節 + 語意記憶
│       │   ├── daily/             ← append-only daily log
│       │   ├── memory.md          ← 蒸餾持久事實
│       │   └── recent.md          ← session context
│       └── knowledge/              ← 參考資料
├── knowledge/shared/               ← 全域知識庫
├── templates/                      ← Web UI 6 頁
├── src/
│   ├── agent/                      ← process + cli + planner + session
│   ├── bot/                        ← TG handlers（L1-L4 路由）
│   ├── coordinator/a2a/            ← A2A 派工（router + transport + server）
│   ├── memory/                     ← 記憶子系統（daily_log + recall + consolidate）
│   ├── wiki/                       ← WikiEngine + indexer + search/（四層）
│   ├── skills/internal/            ← 實際 Python Skills
│   ├── tools/                      ← 🆕 Gemini FC Tools（read/write/list + registry）
│   ├── server/                     ← FastAPI + Memory API + A2A endpoints
│   └── llm/                        ← Gemini Chat + 🆕 Agent Loop（ReAct）
├── output/                         ← 🆕 產出目錄（reports/skills/exports/drafts/）
├── docs/                           ← 工程文件（spec + design + plan）
├── logs/
└── tests/
```

---

## 🧠 自我成長系統（NEW）

Agent 具備跨 session 記憶 + Skill 自動推薦能力：

```
任務完成
  ├→ 自動寫 daily log（情節記憶）
  └→ tool calls ≥ 5？
       └→ LLM 生成 Skill 草稿 → TG 推送審批
            ├→ ✅ 核准 → .kiro/skills/ 落地
            └→ ❌ 駁回 → 歸檔
```

### 記憶層次

| 層 | 檔案 | 用途 |
|----|------|------|
| 情節 | `memory/daily/YYYY-MM-DD.md` | 每次任務自動記錄 |
| 語意 | `memory/memory.md` | 蒸餾後持久事實（≤ 2000tk） |
| context | `memory/recent.md` | session 啟動自動注入 |
| 程序 | `.kiro/skills/*/SKILL.md` | 審批後生效的可重用流程 |

### Steering 4 檔制

每個 Agent 的 `.kiro/steering/`：

| 檔案 | 職責 |
|------|------|
| `SOUL.md` | 我是誰（人格、能力、邊界、使用者偏好） |
| `BRAIN.md` | 我怎麼工作 + 安全紅線 + 品質護欄 |
| `MEMORY.md` | 專案狀態 + 技術決策 + 踩坑紀錄 |
| `TEAM.md` | 團隊結構 + 協作規則 |

### Memory API

| Method | Path | 功能 |
|--------|------|------|
| POST | `/api/v1/memory/recall` | FTS5 查詢 |
| GET | `/api/v1/memory/daily` | 取得 daily log |
| POST | `/api/v1/memory/consolidate` | 手動蒸餾 |
| GET | `/api/v1/skills/list` | 列出 skills |
| GET | `/api/v1/skills/pending` | 待審清單 |
| POST | `/api/v1/skills/approve` | 核准提案 |
| POST | `/api/v1/skills/reject` | 駁回提案 |

---

## Tier 分級

| Tier | 條件 | 能力 |
|------|------|------|
| 0 | 零設定 | Prompts + Skills + Wiki + MCP |
| 1 | + TG Token | Bot + Inline Button + 對話 |
| 2 | + Gemini Key | 🚀 Ark Agent（ReAct + 7 Tools + 記憶 + 自動派工） |
| 3 | + Agent CLI | 8 Agent 分身（agy / kiro / claude） |

### Agent 進程架構

```
🚀 Ark Agent（Default）     → Gemini ReAct agent_loop（in-process，3-5s）
👑 Admin ~ 📝 Report（×8）  → CLI spawn per message（動態，15-20s）
```

- Default 不建 CLI 進程，直接走 Provider API
- Agent 分身每次對話 spawn CLI（session 靠磁碟恢復）
- CLI Backend 可切（.env `CLI_BACKEND=agy / kiro / claude`）
- **SOUL inject 策略**：kiro-cli 自動讀 `.kiro/steering/`（不注入）；agy/claude 需手動 prepend SOUL.md 到 prompt

---

*改 SOUL 改風格、改 knowledge/ 改知識、改 memory/ 改記憶、加 team.yaml 變團隊。帶走直接用。*
