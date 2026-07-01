# AI Workshop — 範例專案

> 兩個獨立可跑的完整專案，對應兩個課程。

## 結構

```
sample/
├── a-agent/          ← 課程 A 產出（個體 Agent）
└── b-agent-team/     ← 課程 B 產出（Agent 團隊平台）
```

## 課程 A：個體 Agent

一個有靈魂的 AI Bot：SOUL + Skills + Wiki + Gemini 對話。

```bash
cd a-agent
pip install -r requirements.txt
cp .env.example .env
python start.py
```

| 能力 | 來自 |
|------|------|
| 有人格（SOUL.md） | 01 Agent 初始 |
| 有技能（4 Skills） | 02 Skills 開發 |
| 有記憶（Wiki RAG） | 03 LLM Wiki |

## 課程 B：Agent 團隊平台

5 Agent 並行的完整平台：CoreDaemon + A2A + Dashboard。

```bash
cd b-agent-team
pip install -r requirements.txt
cp .env.example .env
cp team-ops.yaml team.yaml    # 或 team-dev.yaml
python start.py
```

| 配置 | 成員 | 場景 |
|------|------|------|
| 營運團隊 | admin + pm + market + data + report | 市場+數據+報告 |
| 研發團隊 | admin + pm + ai-dev + coder + qa | 開發+測試 |

## 差異對比

| | a-agent | b-agent-team |
|---|---|---|
| Agent 數量 | 1 | 5 並行 |
| 執行方式 | 單進程 | CoreDaemon 多進程 |
| 知識庫 | 單一 | 每 Agent 獨立 + 共用 |
| 派工 | 無 | /assign + TaskGraph |
| 監控 | health API | Dashboard + 費用 + 審計 |
| 部署 | python start.py | Docker Compose |
| 帶走對象 | 課程 A 學員 | 課程 B 學員 |

---

*兩個資料夾完全獨立，各自可跑。*
