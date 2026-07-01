# AI Workshop — 完整範例專案

> 一個專案包含五堂課的所有功能，`python start.py` 一鍵啟動。

## 快速開始（5 分鐘）

```bash
cd ai-workshop/sample
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # 填入 Token（選填）
python start.py
```

## Tier 分級

```
Tier 0 — 零設定即可體驗：Skills + Wiki + API + Dashboard
Tier 1 — 填入 TELEGRAM_BOT_TOKEN → Bot 對話 + 派工 + 看板
Tier 2 — 填入 GEMINI_API_KEY → AI 對話 + RAG 問答
```

## 啟動後可體驗

| 功能 | Tier | 驗證方式 |
|------|------|---------|
| Health API | 0 | `curl http://localhost:8000/api/v1/health` |
| Skills 列表 | 0 | `curl http://localhost:8000/api/v1/skills` |
| Wiki ingest | 0 | `curl -X POST http://localhost:8000/api/v1/wiki/ingest` |
| Wiki lint | 0 | `curl http://localhost:8000/api/v1/wiki/lint` |
| Dashboard | 0 | 瀏覽器開 http://localhost:8000/board |
| 21 端點 CRUD | 0 | 見下方 API 清單 |
| Bot `/start` | 1 | Telegram 對 Bot 發訊 |
| Bot `/agents` | 1 | 看團隊成員 |
| Bot `/assign` | 1 | 派工 |
| Bot 新聞觸發 | 1 | 輸入「今天新聞」 |
| Gemini 對話 | 2 | 輸入任意文字 |
| RAG 問答 | 2 | `curl -X POST .../wiki/query -d '{"q":"asyncio"}'` |

## 專案結構 → Workshop 對照

```
sample/
├── start.py                ← 一鍵啟動（Tier 感知）
├── team.yaml               ← 5 Agent 配置（04）
├── .env.example
├── requirements.txt
├── src/
│   ├── gateway/            ← 01: Bot + 意圖路由
│   │   ├── bot.py          ← Bot Application 建立
│   │   └── handlers.py     ← 指令 + Planner 路由
│   ├── skills/             ← 02: Skill 系統
│   │   ├── base.py         ← BaseSkill 介面
│   │   ├── registry.py     ← SkillRegistry（auto_discover）
│   │   └── internal/       ← 4 個範例 Skill
│   ├── wiki/               ← 03: 知識庫引擎
│   │   └── engine.py       ← WikiEngine（query/ingest/lint）
│   ├── coordinator/        ← 04: 團隊協調
│   │   ├── task_graph.py   ← 任務依賴圖（DAG）
│   │   ├── discovery.py    ← Agent 能力匹配
│   │   └── task_manager.py ← 任務 CRUD
│   ├── server/             ← 05: 平台 API
│   │   ├── main.py         ← FastAPI 21+ 端點
│   │   ├── api/admin.py    ← Admin 端點
│   │   └── templates/      ← Dashboard HTML
│   └── llm/                ← Gemini Chat 共用
│       └── gemini_chat.py
├── knowledge/              ← Wiki 知識庫
│   ├── raw/                ← 原始文件（3 篇範例）
│   ├── wiki/               ← 結構化知識（ingest 產出）
│   ├── schema.md           ← 規則定義
│   └── index.md
├── tests/
│   └── smoke_test.py       ← Tier 分級測試
└── docs/
    └── workshop-map.md     ← 程式碼 ↔ 課程對照
```

## 測試

```bash
pytest tests/smoke_test.py -v
```

自動依 `.env` 有無 Token 跳過對應 Tier 測試。

---

*一個專案，五堂課的完整體驗。*
