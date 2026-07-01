---
title: "LLM Wiki 建置教學 — 6 步驟從零到自演化知識庫"
type: guide
created: 2026-06-23
updated: 2026-06-23
author: paddyyang
language: zh-TW
---

# LLM Wiki 建置教學 — 6 步驟從零到自演化知識庫

使用 Ark Skills 建立 AI 可讀寫的知識庫引擎，實現 RAG 問答 + 知識圖譜 + 自動萃取。

**五層架構定位**：L5 Knowledge & Skill Evolution（知識演化層）

**操作位置圖示：**
- 📝 = 在 **AI IDE 聊天框**（Kiro CLI）輸入
- 💻 = 在**終端機**執行指令

---

## 專案定位

**LLM Wiki — 讓 AI 擁有長期記憶的知識引擎**

核心能力：
- RAG 問答（搜尋知識庫 → 注入 LLM → 有依據的回答）
- 自動萃取（raw/ 原始文件 → wiki/ 結構化知識）
- 知識圖譜（`[[wikilink]]` 雙向連結 → 節點/邊/hub/orphan 分析）
- 品質治理（lint + schema 驗證 + append-only log）
- 自演化循環（Agent 完成任務 → Reflection → skill.md → Wiki → 全域可用）

---

## 前置條件

- Python 3.12+
- Kiro CLI 2.7+
- Gemini API Key（RAG 問答需要）
- `.kiro/skills/` 已 clone

---

## 建置步驟總覽

| # | Skill | 產出內容 | 角色 |
|---|-------|---------|------|
| 0 | — | 概念理解 | 為什麼 AI 需要外部記憶 |
| 1 | ark-webapp-generator | FastAPI + Skill 骨架 | 基底專案 |
| 2 | ark-wiki-engine | 8 個 Wiki Skill + API + UI | 知識引擎核心 |
| 3 | — | venv + .env + 啟動 | 環境設定 |
| 4 | — | raw/ → wiki/ | 匯入知識 |
| 5 | — | Chat RAG 問答 | 驗證核心功能 |

---

## Step 0：概念 — 為什麼 AI 需要外部記憶

### LLM 的三大限制

| 限制 | 說明 | Wiki 解法 |
|------|------|----------|
| 知識截止 | 訓練資料有截止日 | 隨時更新的外部知識庫 |
| 幻覺 | 沒把握也會自信回答 | RAG 回答附帶來源引用 |
| 遺忘 | 無法記住對話以外的資訊 | 持久化知識 + 全文搜尋 |

### 三層模式（Andrej Karpathy LLM Wiki 理念）

```
knowledge/
├── raw/          → 唯讀原始資料（人類丟進來，AI 只讀不改）
├── wiki/         → 結構化知識（AI 維護，人類可審閱）
│   ├── overview.md
│   └── {category}/
├── schema.md     → 規則定義（控制 AI 行為邊界）
├── index.md      → 索引目錄
└── log.md        → 操作日誌（append-only，審計軌跡）
```

### 設計原則

| 原則 | 說明 |
|------|------|
| 來源與衍生分離 | raw/ 保留原始，wiki/ 是 AI 萃取版本 |
| Schema 約束 | AI 只能用 schema 定義的 type/status |
| Append-only log | log.md 只追加不刪改 |
| 雙向連結 | `[[page_name]]` 語法建構知識圖譜 |
| 矛盾標記 | AI 不自行解決矛盾，只標記待釐清 |

---

## Step 1：建立 Web 專案基底

> 如果你已有 Workshop 01 的 `my-bot`，可跳過此步驟。

📝 在 Kiro CLI 輸入：

```
建立 ai-bot Web 專案，專案名稱 my-wiki-bot
```

觸發 `ark-webapp-generator`，產出：

```
my-wiki-bot/
├── src/
│   ├── skills/          # Skill 插件系統
│   │   ├── base.py
│   │   ├── registry.py
│   │   └── internal/
│   └── server/          # FastAPI
│       ├── main.py
│       └── api/
├── requirements.txt
└── .env.example
```

---

## Step 2：加入 Wiki 知識庫系統

📝 在 Kiro CLI 輸入：

```
加入 Wiki 知識庫系統
```

觸發 `ark-wiki-engine`，產出：

### 8 個 Wiki Runtime Skills

| Skill | skill_id | 功能 | 使用場景 |
|-------|----------|------|---------|
| WikiQuery | `wiki_query` | 全文搜尋 → 排序回傳 | 問問題 |
| WikiIngest | `wiki_ingest` | raw/ → 萃取 → 建立 wiki 頁面 | 匯入新知識 |
| WikiLint | `wiki_lint` | 檢查 frontmatter、孤立頁面、斷連結 | 品質維護 |
| WikiSchema | `wiki_schema` | 驗證 type/status 合法值 | 格式一致 |
| WikiGraph | `wiki_graph` | 分析 `[[wikilink]]` 圖譜 | 知識結構 |
| WikiHybridSearch | `wiki_hybrid_search` | BM25 + 全文 + RRF 融合 | 進階搜尋 |
| WikiRagBridge | `wiki_rag_bridge` | 自動注入 Wiki context 到 LLM | RAG 問答 |
| WikiTemplate | `wiki_template` | 產生標準化頁面模板 | 建立新知識 |

### 知識庫目錄

```
knowledge/my-wiki-bot/
├── raw/              ← 唯讀（你丟檔案到這裡）
├── wiki/             ← AI 維護（結構化知識）
│   └── overview.md
├── schema.md         ← 規則定義
├── index.md          ← 索引
└── log.md            ← 操作日誌
```

### API + UI

```
src/server/api/wiki.py      ← POST /api/v1/wiki/query | ingest | lint
src/server/api/files.py     ← GET /api/files
templates/index.html        ← 💬 Chat + 📚 Wiki 雙分頁
```

---

## Step 3：環境設定與啟動

💻 建立環境：

```bash
cd my-wiki-bot
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# 編輯 .env，填入 GEMINI_API_KEY
```

💻 啟動：

```bash
uvicorn src.server.main:app --reload --port 8000
```

✅ **驗證**：瀏覽器開啟 `http://localhost:8000` → 看到 💬 Chat + 📚 Wiki 雙分頁。

---

## Step 4：匯入知識（Ingest）

### 4.1 準備原始文件

💻 複製範例到 raw/：

```bash
cp ai-workshop/05-llm-wiki-workshop/sample-docs/*.md knowledge/my-wiki-bot/raw/
```

範例文件包含：
- `python-async-guide.md` — 概念類（asyncio 教學）
- `agent-design-notes.md` — 系統類（五層架構，含 `[[wikilink]]`）
- `common-errors.md` — 實用類（錯誤排查）

### 4.1b 匯入你的真實知識（選配，做過 04 的人）

> 💡 如果你在 Workshop 04 完成了 Spec-Driven 開發，把你的產出也匯入 Wiki。
> 這就是「04 產出 → 05 沉澱」的自演化循環。

💻 匯入 04 產出的 Spec：

```bash
# 如果你在 my-team 做了 04 的拷問 + Spec
cp my-team/docs/specs/news-scraper-spec.md knowledge/my-wiki-bot/raw/

# 匯入你寫的 SKILL.md
cp my-team/.kiro/skills/my-daily-news/SKILL.md knowledge/my-wiki-bot/raw/daily-news-skill.md
```

💻 匯入歷史日報（讓 Wiki 累積產業知識）：

```bash
# 如果 market-agent 有產出過日報
cp my-team/agents/market-agent/output/*.md knowledge/my-wiki-bot/raw/
```

**匯入後的效果：**
- 你可以問 Wiki「news_scraper 的失敗重試策略是什麼？」→ 引用你自己的 Spec 回答
- 你可以問「上週 AI 產業有什麼重大事件？」→ 引用歷史日報回答
- 這就是 L5 的核心價值：**一次學會，永久可查**

> ⚠️ 沒做過 04？沒關係，用 4.1 的 sample-docs 即可完成本堂所有操作。

### 4.2 觸發 ingest

📝 在 Chat 輸入：

```
匯入 raw 資料夾的文件到 Wiki
```

或 💻 API 方式：

```bash
curl -X POST http://localhost:8000/api/v1/wiki/ingest \
  -H "Content-Type: application/json" \
  -d '{"source_dir": "raw"}'
```

### 4.3 驗證

- `wiki/` 下出現新頁面 ✅
- `index.md` 已更新 ✅
- `log.md` 有操作記錄 ✅
- Web UI 📚 Wiki 分頁看到檔案樹 ✅

### Frontmatter 規範（v3.0）

每個 wiki 頁面必須有：

```yaml
---
title: "頁面標題"
type: concept | entity | source | synthesis | comparison | overview | system
tags: [tag1, tag2]
sources: [raw/來源檔案]
related: [相關頁面檔名]
created: YYYY-MM-DD
updated: YYYY-MM-DD
status: seedling | developing | mature
---
```

| 欄位 | 必要 | 說明 |
|------|------|------|
| title | ✅ | 頁面標題 |
| type | ✅ | 頁面類型（7 種） |
| tags | ✅ | 分類標籤 |
| sources | 建議 | 來源 raw 檔案 |
| related | 建議 | 相關頁面（用於圖譜） |
| created | ✅ | 建立日期 |
| updated | ✅ | 最後更新日期 |
| status | 建議 | seedling → developing → mature |

### 雙向連結

使用 `[[page_name]]` 語法（不含 .md、不含路徑）：

```markdown
參考 [[python-async-guide]] 了解非同步用法。
```

---

## Step 5：RAG 問答

### 流程

```
使用者問題 → wiki_query 搜尋 → wiki_rag_bridge 注入 → Gemini 回答 → 附來源標註
```

### 測試

📝 在 Chat 輸入：

| 你問 | 期望回答 |
|------|---------|
| 什麼是 asyncio？ | 引用 python-async-guide 內容 |
| AI 五層架構是什麼？ | 引用 agent-design-notes 內容 |
| Bot 沒回應怎麼辦？ | 引用 common-errors 排查表 |

### 回答格式

```
[AI 根據 Wiki 內容產出的回答]
---
📚 參考頁面：[[python-async-guide]]、[[agent-design-notes]]
```

### 運作原理

```python
# wiki_rag_bridge 核心邏輯
async def _get_wiki_context(query: str) -> str:
    result = await registry.invoke("wiki_query", {"query": query, "top_k": 3})
    snippets = [f"[{r['title']}] {r['summary']}" for r in result.data["results"]]
    return "\n".join(snippets)
# 注入 LLM system prompt → AI 根據 context 回答
```

---

## Step 6：進階操作

### Wiki Lint — 品質健康檢查

📝 輸入：

```
wiki 健康檢查
```

回報：
- ⚠️ 缺失 frontmatter 必要欄位的頁面
- 🔗 斷裂的 `[[wikilink]]`（引用不存在的頁面）
- 🏝️ 孤立頁面（沒被任何頁面引用）

### Wiki Graph — 知識圖譜

📝 輸入：

```
分析知識圖譜
```

回報：
- **節點數**：知識頁面數量
- **邊數**：wikilink 連結數量
- **Hub 頁面**：被最多頁面引用的核心知識
- **Orphan 頁面**：需要補充連結的孤立知識

### Hybrid Search — 進階搜尋

📝 輸入：

```
搜尋：asyncio 超時處理
```

BM25 關鍵字 + 全文搜尋 + RRF（Reciprocal Rank Fusion）分數融合。

### Wiki Template — 建立新知識

📝 輸入：

```
建立新知識頁面：Docker 容器化部署，類型 concept
```

自動套用模板、填入 frontmatter、更新 index.md。

---

## 操作路由表

Chat 收到訊息後的 Wiki 操作判斷：

| 意圖 | 觸發詞 | 執行 |
|------|--------|------|
| Query | 一般提問 | wiki_query → RAG 回答（附來源） |
| Ingest | 「匯入」、「ingest」 | wiki_ingest → 更新 index + log |
| Lint | 「lint」、「健康檢查」 | wiki_lint → 品質報告 |
| Update | 「存下來」、「記錄」 | 讀取 → 整合 → 更新 updated |

---

## 進階主題

### 自演化循環（L5 核心價值）

```
Agent 完成任務
    ↓ Reflection 提煉
撰寫 skill.md
    ↓ Wiki ingest
全域知識庫更新
    ↓ 其他 Agent 可搜尋引用
組織智慧累積
```

這對應五層架構中 Layer 5 的核心創新：**一個 Agent 學會的，全體受益**。

### 與 Workshop 02 的串接

Workshop 02 驗證通過的 Skill（Score ≥ 90）→ ingest 到 Wiki → 成為可搜尋的組織資產。

```
02: grill → spec → skill → validate(≥90)
                                 ↓
03: wiki ingest → 全域可搜尋
```

### 多專案知識庫

每個專案獨立目錄，跨專案引用：

```
knowledge/
├── project-a/     # 專案 A 的知識
├── project-b/     # 專案 B 的知識
└── shared/        # 共享知識
```

跨專案引用：`../shared/index.md`

### Schema 規則細節

`schema.md` 定義：
- 合法的 `type` 值（7 種）
- 合法的 `status` 值（3 種）
- 必要欄位清單
- 命名規範（kebab-case 檔名）
- 禁止事項（不可刪 log、不可改 raw）

---

## 常見問題

| 問題 | 原因 | 解法 |
|------|------|------|
| RAG 回答沒引用 Wiki | wiki/ 沒頁面 | 確認已執行 ingest |
| ingest 後 wiki/ 是空的 | raw/ 沒檔案 | 複製 sample-docs/ |
| 搜不到頁面 | index.md 沒更新 | 重新 ingest |
| No module named 'xxx' | 不在 venv | activate + pip install |
| Gemini 沒引用來源 | API Key 未設 | 確認 .env 有值 |
| lint 回報大量問題 | 頁面缺 frontmatter | 用 wiki_template 重建 |
| graph 顯示很多 orphan | 沒加 wikilink | 在頁面間加 [[]] 連結 |

---

## 下一步

完成本課後，你的 Agent 具備了完整個體能力（說話+做事+記住）。下一堂（04）將從一個人變成一個團隊。

- 把自己的技術筆記丟進 `raw/`，建立個人知識庫
- 修改 `schema.md` 加入自訂 type
- 搭配 Telegram Bot 在手機上查 Wiki
- 設定排程自動 lint（搭配 Workshop 04/05 的排程引擎）
- 探索 hybrid_search 的 RRF 權重調整

---

## 使用的 Skill 對照表

| Skill | 觸發詞 | 產出 |
|-------|--------|------|
| `ark-webapp-generator` | 「建立 Web 專案」 | FastAPI + Skill 骨架 |
| `ark-wiki-engine` | 「加入 Wiki 知識庫」 | 8 個 Wiki Skill + API + UI |

---

*作者：paddyyang ｜ 更新：2026-06-23*
