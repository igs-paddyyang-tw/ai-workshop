# a-agent — 課程 A 產出（個體 Agent）

> 一個有靈魂的 AI Bot：SOUL + Skills + Wiki + Gemini 對話。

## 快速啟動

```bash
cd examples/a-agent
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # 填入 Token
python start.py
```

## 這是什麼

課程 A（01-03）的完整產出：

| 能力 | 來自哪堂 | 對應檔案 |
|------|---------|---------|
| 有人格（SOUL） | 01 | `soul.md` |
| 意圖路由 | 01 | `src/bot/handlers.py` |
| Gemini 對話 | 01 | `src/llm/gemini_chat.py` |
| Skills 系統 | 02 | `src/skills/` |
| Wiki 知識庫 | 03 | `src/wiki/` + `knowledge/` |

## Tier 分級

```
Tier 0 — 零設定：Skills echo + Wiki ingest/lint + API health
Tier 1 — TG Token：Bot 對話 + 新聞觸發
Tier 2 — Gemini Key：AI 對話（注入 SOUL）+ RAG 問答
```

## Bot 指令

| 指令 | 功能 |
|------|------|
| `/start` | 歡迎（受 SOUL 人格影響） |
| `/help` | 指令清單 |
| `/status` | 系統狀態（Skills 數量 + LLM 狀態） |
| 直接打字 | Gemini 對話（SOUL 風格） |
| 「今天新聞」| NewsSkill 觸發 |
| 「wiki 查 XX」| Wiki RAG 問答 |

## 結構

```
a-agent/
├── start.py              ← 一鍵啟動
├── soul.md               ← ⭐ 系統提詞（修改它改變 Bot 人格）
├── .env.example
├── requirements.txt
├── src/
│   ├── bot/              ← Bot + Planner
│   ├── skills/           ← BaseSkill + Registry + 4 Skills
│   ├── wiki/             ← WikiEngine（query/ingest/lint）
│   ├── llm/              ← Gemini Chat（注入 SOUL）
│   └── server/           ← FastAPI health API
├── knowledge/            ← Wiki 知識庫
│   ├── raw/             ← 原始文件
│   └── wiki/            ← 結構化知識
└── tests/
    └── smoke_test.py
```

## 想升級為團隊？

```bash
cd ../b-agent-team
```

---

*課程 A 的完整產出。一個 Agent，完整能力。*
