# Workshop Map — 程式碼 ↔ 課程對照

> 每堂課要看哪些檔案、學什麼。

## 總覽

| Workshop | 目錄 | 核心檔案 | 學什麼 |
|----------|------|---------|--------|
| 01 Agent 初始 | `src/gateway/` | `handlers.py`, `bot.py` | 系統提詞 + 意圖路由 |
| 02 Skills 開發 | `src/skills/` | `base.py`, `registry.py`, `internal/` | Spec-Driven + Skill 架構 |
| 03 LLM Wiki | `src/wiki/` + `knowledge/` | `engine.py` | RAG + ingest + lint |
| 04 Agent Team | `src/coordinator/` + `team.yaml` | `task_graph.py`, `discovery.py` | 並行派工 + 能力匹配 |
| 05 平台管理 | `src/server/` | `main.py`, `api/admin.py`, `board.html` | 21 端點 + Dashboard |

---

## 01 — Agent 初始：它能「說話」

**重點檔案：**
- `src/gateway/handlers.py` — 看 `handle_message()` 的意圖路由邏輯
- `src/gateway/bot.py` — Bot 的建立與指令註冊

**觀察重點：**
```python
# handlers.py 第 100 行附近
if any(kw in text for kw in ["新聞", "news", "今天"]):
    # → 關鍵字路由到 NewsSkill
elif any(kw in text for kw in ["wiki", "知識庫"]):
    # → 路由到 WikiEngine
else:
    # → Gemini 對話 fallback
```

> 💡 這就是所有 AI Agent 的核心 — 理解意圖、路由到對的能力。

---

## 02 — Skills 開發：它能「做事」

**重點檔案：**
- `src/skills/base.py` — BaseSkill 介面（所有 Skill 的契約）
- `src/skills/registry.py` — auto_discover + invoke
- `src/skills/internal/news.py` — 完整 Skill 實作範例

**觀察重點：**
```python
# base.py — 每個 Skill 都要實作這個
class BaseSkill(ABC):
    skill_id: str
    async def execute(self, params: dict) -> SkillResult: ...

# registry.py — 自動掃描所有 Skill
registry.auto_discover("src.skills.internal")
result = await registry.invoke("news", {"max_items": 5})
```

**練習：** 在 `src/skills/internal/` 新增一個自己的 Skill。

---

## 03 — LLM Wiki：它能「記住」

**重點檔案：**
- `src/wiki/engine.py` — WikiEngine（query / ingest / lint）
- `knowledge/raw/` — 原始文件（人類丟進來）
- `knowledge/schema.md` — 規則定義

**觀察重點：**
```python
# engine.py — RAG 問答流程
async def query(q, use_rag=True):
    results = self._fulltext_search(q)      # 1. 搜尋 wiki/
    answer = await self._rag_answer(q, results)  # 2. Gemini 合成答案
    return {"results": results, "answer": answer}
```

**練習：** 把自己的技術筆記丟進 `knowledge/raw/`，然後 `curl -X POST .../wiki/ingest`。

---

## 04 — Agent Team：它們能「合作」

**重點檔案：**
- `src/coordinator/task_graph.py` — 任務依賴圖（DAG）
- `src/coordinator/discovery.py` — Agent 能力匹配
- `team.yaml` — 團隊配置

**觀察重點：**
```python
# task_graph.py — 判斷哪些任務可並行
ready = graph.resolve_dependencies()  # → ["fetch"]（只有無依賴的先執行）

# discovery.py — 自動選人
result = discovery.match_agent(["python", "web-scraping"])
# → MatchResult(agent_id="backend", score=0.67)
```

**練習：** 用自然語言「抓新聞 market」派工，然後 `/tasks` 看狀態。

---

## 05 — 平台管理：你能「管理」

**重點檔案：**
- `src/server/main.py` — 21+ REST 端點
- `src/server/api/admin.py` — Admin 統計
- `src/server/templates/board.html` — Kanban Dashboard

**觀察重點：**
```bash
# 試試這些 API
curl http://localhost:8000/api/v1/health
curl http://localhost:8000/api/v1/agents
curl http://localhost:8000/api/v1/skills
curl http://localhost:8000/api/admin/dashboard/stats
```

**練習：** 瀏覽器開 http://localhost:8000/dashboard 看 Dashboard。

---

## 科技日報：貫穿五堂課的體驗

```bash
# 01: Bot 觸發新聞
# Telegram 輸入「今天新聞」→ NewsSkill 抓 HN

# 02: 看 Skill 怎麼寫的
cat src/skills/internal/news.py

# 03: 日報結果存進 Wiki
curl -X POST http://localhost:8000/api/v1/wiki/ingest

# 04: 用自然語言派工
抓取科技新聞 market

# 05: 看統計
curl http://localhost:8000/api/admin/dashboard/stats
```
