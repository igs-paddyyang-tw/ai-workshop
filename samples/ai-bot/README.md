# ai-bot — 課程 A 產出（個體 Agent）

> 8 Agent 切換 + Wiki RAG + Web UI + Telegram 互動。帶走就能用。

## 快速啟動

### macOS / Linux
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # 編輯填入 Token（有註解說明）
python start.py
```

### Windows (PowerShell)
```powershell
py -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env   # 編輯填入 Token
python start.py
```

### 啟動成功畫面
```
══════════════════════════════════════════════════
  🤖 課程 A — 個體 Agent
══════════════════════════════════════════════════
  Tier 0: ✅ Skills + Wiki + API（永遠可用）
  Tier 1: ✅ Telegram Bot
  Tier 2: ✅ Gemini AI + RAG
══════════════════════════════════════════════════

  📦 Skills: 5 個
  📚 知識庫: 3 篇
  🧠 SOUL: ✅ 已載入
  🤖 Bot: @your_bot_name 已連線
  🤖 Bot: polling 啟動

  🚀 API:  http://localhost:8000
  📖 Docs: http://localhost:8000/docs
```

### 確認成功
1. 終端 3 個 ✅ + @bot_name 已連線
2. 📱 Telegram 點 Start → 收到回覆 + 左下角出現 `/` 選單
3. 🌐 瀏覽器開 http://localhost:8000 → 看到 Chat UI

## Web UI（五個頁面）

| URL | 頁面 | 功能 |
|-----|------|------|
| `/` | 💬 Chat | 聊天室窗 — 8 Agent 切換 + Wiki 查詢 |
| `/admin` | ⚙️ Dashboard | KPI 卡片 + Agent 列表 + 知識庫管理 + 系統資訊 |
| `/wiki` | 📖 Wiki | 瀏覽器 — 檔案列表 + 搜尋 + Markdown 內容顯示 |
| `/builder` | 🏗️ Builder | Agent Builder — SOUL 編輯 + 知識綁定 + 預覽對話 |
| `/api-docs` | 📡 API | API 文件 — 暗黑風格 + Try 按鈕即時測試 |

統一導航列：💬 Chat | ⚙️ Dashboard | 📖 Wiki | 🏗️ Builder | 📡 API

## Telegram 互動

### 指令選單（左下角 `/`）

| 指令 | 功能 |
|------|------|
| `/start` | 啟動 + 清空歷史 |
| `/agents` | Inline Button 選 Agent |
| `/mode` | 查看執行模式 |
| `/history` | 對話歷史 |
| `/help` | 指令清單 |

### 回覆標頭

每次回覆帶 Agent 身份：
```
👑 [admin-agent]
系統正常運行中。

🗺️ [market-agent]
今日科技新聞 5 則：...
```

### Reaction 動態

訊息右下角即時顯示處理狀態：
```
你：幫我查 Ocean King    👀 ← 收到
你：幫我查 Ocean King    🔥 ← 處理中
你：幫我查 Ocean King    👍 ← 完成
                         💔 ← 失敗（兜底回覆）
```

### 對話處理流程

```
使用者訊息 → 👀
  → L1: /reset → 清空 session
  → L2: /skill_id args → 直接執行（/news /wiki /summarize /translate /ingest）
  → L3: keyword → Planner 路由
  → L4: CLI（8 Agent 常駐）→ Wiki RAG → Memory → Gemini + SOUL
  → _clean_output（ANSI + 工具噪音過濾 + 結論提取）
  → 👍 + 回覆（標頭 + 分段 4000 字）
```

## 8 個 Agent

| Agent | 職責 |
|-------|------|
| 👑 Admin | 管家（預設） |
| 📋 PM | 專案經理 |
| 🧠 AI Dev | AI 工程師 |
| 💻 Coder | 全端開發 |
| 🧪 QA | 品質保證 |
| 📊 Data | 數據分析 |
| 🗺️ Market | 市場研究 |
| 📝 Report | 報告產出 |

## 知識庫（兩層）

```
knowledge/                          ← 全域（所有 Agent 共用）
├── raw/                            ← 丟文件的地方
│   ├── ocean-king-analysis.md      ← 遊戲競品分析
│   ├── super-ace-analysis.md
│   └── fishing-vs-slot-comparison.md
└── wiki/                           ← ingest 後 → TG + Web 能查到

agents/{agent}/knowledge/           ← 私有（只有該 Agent 能查）
├── raw/                            ← memory 自動寫入
└── wiki/                           ← 私有 ingest 後
```

查詢規則：先查私有 → 再查全域 → 合併結果

## 每個 Agent 的配置

```
agents/{name}-agent/
├── .kiro/
│   ├── steering/SOUL.md        ← 人格（01 改這個）
│   ├── steering/MEMORY.md      ← 記憶策略
│   ├── steering/USER.md        ← 使用者偏好
│   ├── settings/mcp.json
│   └── prompts/route-message.md
├── skills/ark-*/SKILL.md       ← 能力宣告（02 產出這個）
├── knowledge/raw/              ← 私有知識（memory 自動寫入）
└── output/
```

## 專案結構

```
ai-bot/
├── start.py                    ← 一鍵啟動（Token 驗證 + 8 Agent 服務 + BotCommand）
├── start_bot.bat               ← Windows 背景啟動
├── stop_bot.bat                ← Windows 停止
├── restart_bot.bat             ← Windows 重啟
├── .env.example                ← 環境變數（有註解）
├── .kiro/
│   ├── steering/SOUL.md        ← 根 SOUL（fallback）
│   └── skills/                 ← Kiro IDE Skills（教學用）
│       ├── ark-grill-me/       ← 02 拷問
│       ├── ark-superpowers/    ← 02 產 Spec
│       ├── ark-skill-creator/  ← 02 產 SKILL.md
│       ├── ark-code-spec-validator/ ← 02 驗證
│       └── ark-wiki-engine/    ← 03 知識庫
├── agents/                     ← 8 個 Agent（各有 .kiro/ + knowledge/）
├── knowledge/                  ← 全域知識庫（所有 Agent 共用）
├── templates/                  ← Web UI（5 頁）
│   ├── index.html              ← 💬 Chat
│   ├── admin.html              ← ⚙️ Dashboard
│   ├── wiki.html               ← 📖 Wiki 瀏覽器
│   ├── builder.html            ← 🏗️ Agent Builder + 預覽對話
│   └── api-docs.html           ← 📡 API
├── src/
│   ├── agent/                  ← 核心（process + cli + session + memory + planner）
│   ├── bot/                    ← Telegram（Planner L1-L4 + Reaction + 標頭）
│   ├── skills/internal/        ← 實際執行工具（Python）
│   ├── wiki/                   ← WikiEngine（兩層查詢）
│   ├── llm/                    ← Gemini Chat（含 logging）
│   ├── server/                 ← FastAPI + /api/v1/chat
│   └── logging_config.py       ← RotatingFileHandler
├── logs/                       ← 執行日誌（自動產生）
├── config/
└── tests/
```

## Tier 分級

| Tier | 條件 | 能力 |
|------|------|------|
| 0 | 零設定 | Skills + Wiki + API + Web UI |
| 1 | + TG Token | Bot + Inline Button + Reaction + 8 Agent |
| 2 | + Gemini Key | AI 對話 + RAG + SOUL 人格 |
| 3 | + kiro-cli | 8 Agent 常駐服務（完整 .kiro/ 配置） |
| 4 | + team.yaml | 團隊模式（PM 派工 + discovery + 任務狀態）|

## 兩種模式

```
沒有 team.yaml → 個體模式（課程 A：駕馭工程）
有 team.yaml  → 團隊模式（課程 B：迴圈工程）

升級方式：cp team-ops.yaml team.yaml → 重啟 → 團隊模式啟用
```

---

*課程 A 完整產出。改 SOUL 改風格、改 knowledge/ 改知識、帶走直接用。*
