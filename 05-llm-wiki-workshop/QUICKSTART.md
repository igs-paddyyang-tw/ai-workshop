# 🚀 LLM Wiki Workshop — 快速上手指南

> 50 分鐘讓你的 AI 擁有長期記憶 — RAG 問答 + 知識圖譜 + 自動萃取。

**作者：** paddyyang
**更新：** 2026-06-23

---

## 🎯 上課目標（50 分鐘）

| 時間 | 動作 | 你做什麼 | AI 做什麼 |
|------|------|---------|-----------|
| 0-5 min | 概念講解 | 理解 RAG = 搜尋 + 注入 + 生成 | — |
| 5-15 min | 觸發建構 | 在 Kiro 聊天框輸入觸發詞 | `ark-wiki-engine` 產出 8 Skill + API + UI |
| 15-20 min | 環境設定 | venv + pip + 填 .env | — |
| 20-30 min | 匯入知識 | 把 sample-docs/ 丟進 raw/ → 觸發 ingest | wiki_ingest 萃取 → 建立 wiki 頁面 |
| 30-40 min | RAG 問答 | 在 Chat 問問題 → AI 引用 Wiki 回答 | wiki_rag_bridge 注入 context |
| 40-50 min | 進階操作 | lint + graph + hybrid_search | 回報品質 + 圖譜分析 |

### 完成度分級

```
🏆 快速組（40 min 內全完成）
   → RAG 問答有來源標註 + Wiki lint 通過 + graph 分析

✅ 標準組（大多數人）
   → ingest 成功 + Chat 能引用 Wiki 回答

🎯 保底組（至少完成這個）
   → Wiki 目錄結構正確 + 至少 1 篇知識頁面產出
```

---

## 🧠 核心概念：為什麼 AI 需要 Wiki？

```
LLM 的問題：                    Wiki 的解法：
❌ 知識有截止日期               ✅ 隨時更新的外部知識庫
❌ 會產生幻覺                   ✅ RAG 回答附帶來源引用
❌ 無法記住對話以外的資訊        ✅ 持久化知識 + 全文搜尋
```

### RAG 流程（本 Workshop 核心）

```
使用者：「什麼是 asyncio？」
    │
    ▼
┌──────────────┐
│ wiki_query   │ ← FTS5 全文搜尋知識庫
└──────┬───────┘
       │ 找到 python-async-guide.md
       ▼
┌──────────────────┐
│ wiki_rag_bridge  │ ← 將相關片段注入 LLM context
└──────┬───────────┘
       ▼
┌──────────────┐
│ Gemini LLM   │ ← 根據 context 產出有依據的回答
└──────┬───────┘
       ▼
Bot 回答 + 📚 參考頁面：[[python-async-guide]]
```

---

## 你需要準備的東西

| 項目 | 說明 |
|------|------|
| Python 3.12+ | https://python.org |
| Kiro CLI 2.7+ | `kiro-cli --version` |
| Git | https://git-scm.com |
| Gemini API Key | https://aistudio.google.com/apikeys（免費，RAG 問答需要） |

---

## Step 0：環境準備

```bash
kiro-cli --version    # 需要 2.7+
python3 --version     # 需要 3.12+

# 取得 Skills（如果還沒有）
git clone https://github.com/igs-paddyyang-tw/ark-agent-skills .kiro/skills/
```

---

## Step 1：建立 Web 專案基底

> 如果你已有 Workshop 01 的 `my-bot` 專案，可跳過此步驟直接到 Step 2。

在 Kiro CLI 聊天框輸入：

```
建立 ai-bot Web 專案，專案名稱 my-wiki-bot
```

AI 會觸發 `ark-webapp-generator`，產出 FastAPI + Skill 系統骨架。

### 產出結構（確認有這些）

```
my-wiki-bot/
├── src/
│   ├── skills/
│   │   ├── base.py          ← Skill 基礎類別
│   │   ├── registry.py      ← 自動註冊
│   │   └── internal/        ← 業務 Skill
│   └── server/
│       ├── main.py          ← FastAPI 入口
│       └── api/             ← API 路由
├── requirements.txt
└── .env.example
```

---

## Step 2：加入 Wiki 知識庫系統（核心步驟）

在 Kiro CLI 聊天框輸入：

```
加入 Wiki 知識庫系統
```

AI 觸發 `ark-wiki-engine`，產出：

### 產出的 8 個 Wiki Skill

| Skill | 功能 | 你何時用到 |
|-------|------|-----------|
| `wiki_query` | 全文搜尋知識庫 | 問問題時 |
| `wiki_ingest` | raw/ → wiki/ 自動萃取 | 匯入新知識 |
| `wiki_lint` | 檢查頁面品質 | 維護知識庫 |
| `wiki_schema` | 驗證 frontmatter 規範 | 確保格式一致 |
| `wiki_graph` | 知識圖譜分析 | 看知識連結 |
| `wiki_hybrid_search` | BM25 + 全文 + RRF 融合 | 進階搜尋 |
| `wiki_rag_bridge` | 自動注入 Wiki context 到 LLM | RAG 問答 |
| `wiki_template` | 產生標準化頁面 | 建立新知識 |

### 產出的知識庫結構

```
knowledge/my-wiki-bot/
├── raw/              ← 唯讀原始資料（你丟檔案到這裡）
├── wiki/             ← AI 維護的結構化知識
│   └── overview.md   ← 專案總覽
├── schema.md         ← 規則定義
├── index.md          ← 索引目錄
└── log.md            ← 操作日誌（append-only）
```

### 產出的 API + UI

```
src/server/api/wiki.py      ← POST /api/v1/wiki/query | ingest | lint
src/server/api/files.py     ← GET /api/files（Wiki 瀏覽）
templates/index.html        ← 💬 Chat + 📚 Wiki 雙分頁
```

---

## Step 3：設定環境與啟動

```bash
cd my-wiki-bot
python3 -m venv .venv
source .venv/bin/activate    # Linux/Mac
pip install -r requirements.txt

cp .env.example .env
# 編輯 .env，填入 GEMINI_API_KEY
```

啟動：
```bash
uvicorn src.server.main:app --reload --port 8000
```

瀏覽器開啟 `http://localhost:8000` → 看到 Chat + Wiki 雙分頁。

---

## Step 4：匯入知識（Ingest）

### 4.1 複製範例文件到 raw/

```bash
cp ai-workshop/05-llm-wiki-workshop/sample-docs/*.md knowledge/my-wiki-bot/raw/
```

### 4.2 觸發 ingest

在 Chat 輸入框（或 Kiro CLI）輸入：

```
匯入 raw 資料夾的文件到 Wiki
```

或透過 API：
```bash
curl -X POST http://localhost:8000/api/v1/wiki/ingest \
  -H "Content-Type: application/json" \
  -d '{"source_dir": "raw"}'
```

### 4.3 驗證結果

- `knowledge/my-wiki-bot/wiki/` 下出現新頁面 ✅
- `index.md` 已更新 ✅
- `log.md` 有操作記錄 ✅

在 Web UI 切換到 📚 Wiki 分頁，應該看到檔案樹。

---

## Step 5：RAG 問答實測（🎯 Wow Moment）

在 Chat 輸入：

| 📱 你問 | 期望回答 |
|---------|---------|
| `什麼是 asyncio？` | 引用 python-async-guide 的內容回答 |
| `Agent 系統的四層架構是什麼？` | 引用 agent-design-notes 回答 |
| `Bot 沒回應怎麼辦？` | 引用 common-errors 排查表 |

### 回答格式

```
[AI 根據 Wiki 內容產出的回答]
---
📚 參考頁面：[[python-async-guide]]、[[agent-design-notes]]
```

> 💡 **這就是 RAG** — AI 不再憑空回答，而是引用你的知識庫作為依據。

---

## Step 6：進階操作

### 6.1 Wiki Lint — 知識庫健康檢查

```
wiki 健康檢查
```

回報：
- ⚠️ 缺失 frontmatter 欄位的頁面
- 🔗 斷裂的 `[[wikilink]]`
- 🏝️ 孤立頁面（沒有被任何頁面引用）

### 6.2 Wiki Graph — 知識圖譜

```
分析知識圖譜
```

回報：
- 節點數（知識頁面數量）
- 邊數（wikilink 連結數量）
- Hub 頁面（被最多頁面引用的核心知識）
- Orphan 頁面（需要補充連結的孤立知識）

### 6.3 Hybrid Search — 進階搜尋

```
搜尋：asyncio 超時處理
```

使用 BM25 關鍵字 + 全文搜尋 + RRF 分數融合，比單純關鍵字更精準。

---

## 🧠 教學焦點：Wiki 三層模式

```
knowledge/
├── raw/          → 唯讀原始資料（人類丟進來，AI 只讀不改）
├── wiki/         → 結構化知識（AI 維護，人類可審閱）
└── schema.md     → 規則定義（控制 AI 行為邊界）
```

### 設計哲學

| 原則 | 說明 |
|------|------|
| 來源與衍生分離 | raw/ 保留原始文件，wiki/ 是 AI 萃取的版本 |
| Schema 約束 | AI 只能用 schema 定義的 type/status |
| Append-only log | log.md 只追加，不可刪改（審計軌跡） |
| 雙向連結 | `[[page]]` 語法，自動建構知識圖譜 |

### Frontmatter 規範

```yaml
---
title: "頁面標題"
type: concept | entity | source | synthesis | system
tags: [tag1, tag2]
related: [other-page]
created: 2026-06-23
updated: 2026-06-23
status: seedling | developing | mature
---
```

---

## ⚠️ 常見問題

| 錯誤 | 原因 | 解法 |
|------|------|------|
| RAG 回答沒引用 Wiki | 沒有 ingest | 確認 wiki/ 下有頁面 |
| ingest 後 wiki/ 是空的 | raw/ 沒檔案 | 複製 sample-docs/ 到 raw/ |
| 搜不到明明存在的頁面 | index.md 沒更新 | 重新觸發 ingest |
| `No module named 'xxx'` | 沒在 venv 中 | `source .venv/bin/activate` + `pip install -r requirements.txt` |
| Gemini 回答但沒引用來源 | GEMINI_API_KEY 未設定 | 確認 .env 有值 |

---

## 回家自我練習

- 把自己的技術筆記丟進 `raw/`，建立個人知識庫
- 修改 `schema.md` 加入自訂 type
- 在 `wiki_rag_bridge` 中調整 top_k 數量觀察回答品質
- 搭配 Workshop 01 的 Bot，在 Telegram 中直接問 Wiki

---

## 教材包檔案說明

```
05-llm-wiki-workshop/
├── QUICKSTART.md              ← 本文件（50 分鐘快速版）
├── quickstart.html            ← HTML 版首頁
└── sample-docs/               ← 餵入用的範例知識文件
    ├── python-async-guide.md  ← 概念類（asyncio 教學）
    ├── agent-design-notes.md  ← 系統類（架構設計，含 wikilink）
    └── common-errors.md       ← 實用類（錯誤排查）
```

---

## 本 Workshop 使用的 Skill

| Skill | 觸發詞 | 產出 |
|-------|--------|------|
| `ark-webapp-generator` | 「建立 Web 專案」 | FastAPI + Skill 骨架 |
| `ark-wiki-engine` | 「加入 Wiki 知識庫」 | 8 個 Wiki Skill + API + UI |

---

*作者：paddyyang ｜ 更新：2026-06-23*
