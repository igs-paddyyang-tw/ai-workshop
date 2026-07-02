# ai-bot — 課程 A 產出（個體 Agent）

> 8 個 Agent 可切換，Inline Button 選擇，每次對話自動記憶。

## 快速啟動

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # 填入 Token
python start.py
```

## 8 個 Agent

| 指令 | Agent | 職責 |
|------|-------|------|
| `/agents` | 👑 Admin | 管家 + 智能分流（預設） |
| | 📋 PM | 專案經理 + 派工 |
| | 🧠 AI Dev | AI 工程師 + Prompt 設計 |
| | 💻 Coder | 全端開發 |
| | 🧪 QA | 品質保證 + 測試 |
| | 📊 Data | 數據分析（內部） |
| | 🗺️ Market | 市場研究（外部） |
| | 📝 Report | 報告產出（彙整） |

## 對話流程

```
/agents → Inline Button 選 Agent → 對話 → 自動寫 memory
```

- 一次只能跟一個 Agent 對話
- 每個 user_id 獨立 session
- 對話歷史保留最近 10 輪
- 完成後自動寫入 `agents/{name}/knowledge/raw/`

## 雙模式

| 模式 | 條件 | 能力 |
|------|------|------|
| 🧠 Agent CLI | kiro-cli 已安裝 | .kiro/ 全生效（SOUL + Skills） |
| ⚡ Gemini API | GEMINI_API_KEY | 直呼 API + SOUL 注入 |

輸入 `/mode` 查看當前模式。

## 每個 Agent 的配置

```
agents/{name}-agent/
├── .kiro/
│   ├── steering/SOUL.md       ← 八段式人格
│   ├── steering/KIRO.md       ← 行為規範
│   ├── steering/MEMORY.md     ← 記憶規則
│   ├── steering/USER.md       ← 使用者偏好
│   ├── settings/mcp.json
│   ├── agents/{name}.json
│   └── prompts/route-message.md
├── skills/ark-{skill}/SKILL.md ← Ark Skill 格式
├── knowledge/raw/              ← 知識種子 + memory 累積
└── output/                     ← 產出結果
```

## Bot 指令

| 指令 | 功能 |
|------|------|
| `/start` | 歡迎 + 當前 Agent |
| `/agents` | Inline Button 選 Agent |
| `/mode` | 查看執行模式 |
| `/history` | 查看對話歷史 |
| `/help` | 指令清單 |

## Tier 分級

```
Tier 0 — 零設定：Skills + Wiki + API
Tier 1 — TG Token：Bot + Inline Button + 8 Agent
Tier 2 — Gemini Key：AI 對話 + RAG
```

## 專案結構

```
ai-bot/
├── start.py                    ← 一鍵啟動
├── .kiro/                      ← 根配置（預設 admin）
├── agents/                     ← 8 個 Agent（各有完整 .kiro/）
├── src/
│   ├── agent/                  ← 核心（cli + session + memory + planner）
│   ├── bot/                    ← Telegram（Inline Button + handlers）
│   ├── skills/                 ← 共用 Skills（echo + news + summarize + translate + renderer）
│   ├── wiki/                   ← WikiEngine
│   ├── llm/                    ← Gemini Chat
│   └── server/                 ← FastAPI
├── config/                     ← 配置（news_sources + llm_prompts）
├── templates/                  ← HTML 模板
├── knowledge/                  ← 共用知識庫
└── docs/                       ← 設計文件
```

---

*課程 A 的完整產出。8 個 Agent，Inline Button 切換，自動記憶。*
