# ai-bot — 🏗️ AI Agent 專家系統平台

> 8 Agent + 四層搜尋 Wiki + A2A 跨機派工 + Web UI 6 頁 + Telegram 互動。帶走就能用。

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
  Tier 0: ✅ Skills + Wiki + API（永遠可用）
  Tier 1: ✅ Telegram Bot
  Tier 2: ✅ Gemini AI + RAG
══════════════════════════════════════════════════

  📦 Skills: 5 個
  📚 知識庫: 6 篇
  🧠 SOUL: ✅ 已載入
  🤖 Bot: @your_bot_name 已連線

  📌 個體模式（無 team.yaml）

  🚀 API:  http://localhost:8000
  📖 Docs: http://localhost:8000/api-docs
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
| `/start` | 啟動 + 清空 |
| `/agents` | Inline Button 選 Agent |
| `/recall <query>` | 查詢 Agent 歷史經驗（FTS5） |
| `/skills` | 列出已生效 Skills |
| `/skills pending` | 待審 Skill 提案 |
| `/consolidate` | 手動蒸餾 daily → memory.md |
| `/mode` | 執行模式 |
| `/help` | 指令清單 |

### Reaction 動態

```
👀 收到 → 🔥 處理中 → 👍 完成 / 💔 失敗
```

---

## 專案結構

```
ai-bot/
├── start.py                        ← 一鍵啟動（含自檢）
├── start_bot.bat / stop_bot.bat    ← Windows
├── team-ops.yaml                   ← 本地團隊範本
├── team-distributed.yaml           ← 跨機團隊範本
├── .env.example
├── requirements.txt
├── data/                           ← 運行資料
│   ├── memory.db                   ← FTS5 統一索引
│   └── proposals.json              ← Skill 審批狀態
├── .kiro/
│   ├── steering/SOUL.md + USER.md + BRAIN.md
│   └── skills/ark-wiki-engine/ + ark-grill-me/ + ...
├── agents/                         ← 8 Agent（.kiro/ + knowledge/ + memory/）
│   └── {name}-agent/
│       ├── .kiro/steering/         ← SOUL + USER + BRAIN + GUARDRAILS
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
│   ├── memory/                     ← 🆕 記憶子系統（daily_log + recall + recommend + ...）
│   ├── wiki/                       ← WikiEngine + indexer + search/（四層）
│   ├── skills/internal/            ← 實際 Python Skills
│   ├── server/                     ← FastAPI + Memory API + A2A endpoints
│   └── llm/                        ← Gemini Chat
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
| `SOUL.md` | 我是誰（人格、邊界） |
| `USER.md` | 我服務誰（偏好） |
| `BRAIN.md` | 我怎麼工作 + 安全紅線 |
| `GUARDRAILS.md` | 品質標準（核心規則 + 禁止事項） |

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
| 0 | 零設定 | Skills + Wiki + API + Web UI |
| 1 | + TG Token | Bot + Inline Button + 8 Agent |
| 2 | + Gemini Key | AI 對話 + RAG + SOUL |
| 3 | + kiro-cli | 8 Agent 常駐 + 完整 .kiro/ |
| 4 | + team.yaml | 團隊派工 + A2A 跨機 |

---

*改 SOUL 改風格、改 knowledge/ 改知識、改 memory/ 改記憶、加 team.yaml 變團隊。帶走直接用。*
