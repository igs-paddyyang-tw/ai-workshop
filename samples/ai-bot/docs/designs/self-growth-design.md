---
title: "ai-bot 自我成長系統 設計文件"
type: design
version: "1.0"
status: proposed
language: zh-TW
author: "paddy"
created: 2026-07-09
updated: 2026-07-09
deciders: ["paddy"]
related_spec: "docs/specs/self-growth-spec.md"
---

# ai-bot 自我成長系統 — 設計文件

## 1. 概述（Overview）

本文件描述 ai-bot 自我成長系統的技術設計：讓 8 個 Agent 具備跨 session 記憶（情節 + 語意）、
統一檢索（FTS5）、Skill 自動推薦（Agent 偵測 → TG 審批 → 落地），
以及配套的 Steering 檔案重構。

## 2. 背景（Context）

- **相關 Spec**：`docs/specs/self-growth-spec.md`
- **現有系統**：8 Agent + 四層搜尋 Wiki + TG Bot + FastAPI，已可運作但無跨 session 記憶
- **技術債**：steering memory.md 僅 4 行、KIRO.md 職責混雜、無記憶目錄
- **約束**：零新依賴（Python + SQLite FTS5）、個人開發者單機

## 3. 架構決策（Architecture Decisions）

### ADR-001: 記憶儲存選型

**狀態**：accepted

**背景**：Agent 需要跨 session 的經驗儲存，選 DB 還是檔案？

| 選項 | 優點 | 缺點 |
|------|------|------|
| A: PostgreSQL | 強查詢、ACID | 新依賴、部署成本 |
| B: SQLite 全存 | 單檔、零依賴 | 不可 diff、不人讀 |
| C: **Markdown 檔案 + FTS5 索引** | 人可讀、可 diff、可 git、零依賴 | 大量檔案時 IO 略慢 |

**決策**：選 C — Markdown 為主體，SQLite FTS5 為索引層。

**後果**：
- 正面：人可直接編輯 memory.md、daily log 可 git blame
- 負面：索引需另行維護（新增/刪除時 rebuild）
- 風險：daily log 30 天後量大 → 用 gitignore + 歸檔緩解

---

### ADR-002: Skill 提案觸發方式

**狀態**：accepted

**背景**：Agent 學會新流程後如何沉澱為 Skill？

| 選項 | 優點 | 缺點 |
|------|------|------|
| A: 人手動 `/learn` | 品質高（人選擇性觸發） | 人會忘記、負擔重 |
| B: **Agent 自動偵測 + 推薦 → 人審批** | 人零負擔、不漏 | 推薦可能過多/品質低 |
| C: 全自動（無審批） | 最快落地 | 危險：垃圾 Skill 汙染能力庫 |

**決策**：選 B — Agent 偵測 + 推薦，人只按按鈕。

**後果**：
- 正面：人不需記指令，Agent 不漏有價值的流程
- 負面：初期推薦品質可能低 → 設門檻調節（核准率 < 30% 則提高觸發條件）
- 控制：審批負擔 ≤ 3 則/天，超過則調高 tool calls 門檻

---

### ADR-003: Steering 結構重構

**狀態**：accepted

**背景**：現有 steering 檔案職責混雜，缺乏記憶操作說明。

| 選項 | 優點 | 缺點 |
|------|------|------|
| A: 維持現狀 + 加 BRAIN.md + SAFETY.md | 增量改動小 | 6 檔/Agent，維護點多 |
| B: **精簡為 4 檔（SOUL + USER + BRAIN + GUARDRAILS）** | 職責清晰、context 省 | 需遷移現有檔案 |
| C: 全部合併成 1 個大 steering | 最少檔案 | 難維護、難 diff |

**決策**：選 B — 4 檔制，安全紅線併入 BRAIN.md。

**後果**：
- 正面：每個檔案回答一個問題，新增 Agent 時模板清晰
- 負面：需一次性遷移 8 Agent 的 KIRO.md → GUARDRAILS.md
- 風險：遷移期間可能遺漏 → start.py 啟動自檢確保必備檔存在

## 4. 系統架構（System Architecture）

### 4.1 高層架構圖

```
┌─────────────────────────────────────────────────────────┐
│                    ai-bot Process                         │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌──────────┐   ┌──────────┐   ┌──────────────────┐    │
│  │ TG Bot   │   │ FastAPI  │   │  Agent Process    │    │
│  │ (L1-L4)  │   │ Server   │   │  (×8 sessions)   │    │
│  └────┬─────┘   └────┬─────┘   └────────┬─────────┘    │
│       │               │                   │              │
│       └───────────────┼───────────────────┘              │
│                       │                                  │
│              ┌────────▼────────┐                         │
│              │   Coordinator    │                         │
│              └────────┬────────┘                         │
│                       │                                  │
│  ┌────────────────────┼────────────────────────┐        │
│  │                    │                         │        │
│  ▼                    ▼                         ▼        │
│ ┌──────────┐  ┌─────────────┐  ┌────────────────────┐  │
│ │ Memory   │  │ Skill       │  │ Wiki Engine        │  │
│ │ Manager  │  │ Manager     │  │ (現有四層搜尋)      │  │
│ └────┬─────┘  └──────┬──────┘  └─────────┬──────────┘  │
│      │               │                    │              │
│      └───────────────┼────────────────────┘              │
│                      │                                   │
│             ┌────────▼────────┐                          │
│             │  FTS5 Index     │                          │
│             │  (memory.db)    │                          │
│             └─────────────────┘                          │
└─────────────────────────────────────────────────────────┘

檔案系統：
agents/{name}-agent/
├── .kiro/steering/    ← SOUL + USER + BRAIN + GUARDRAILS
├── .kiro/skills/      ← 程序記憶（審批後落地）
├── memory/            ← 情節 + 語意記憶
│   ├── daily/         ← append-only
│   ├── memory.md      ← 蒸餾持久事實
│   └── recent.md      ← session context
└── knowledge/         ← 參考資料（現有）
```

### 4.2 數據流

#### 記憶寫入流

```
任務完成
  │
  ├─► daily_log.py ──► LLM 摘要 ──► memory/daily/YYYY-MM-DD.md (append)
  │                         │
  │                    失敗 fallback ──► task_id + 一行摘要
  │
  └─► skill_recommend.py ──► 評估觸發條件（tool calls ≥ 5）
                                │
                           命中 ├─► LLM 生成 SKILL.md 草稿
                                │         │
                                │    ┌────▼─────┐
                                │    │  pending/ │  (JSON 狀態追蹤)
                                │    └────┬─────┘
                                │         │
                                │    TG 推送審批卡片
                                │         │
                                │    ✅ → apply() → .kiro/skills/ + rebuild index
                                │    ❌ → archive + 記入 daily log
                                │
                           未命中 └─► 不動作
```

#### 記憶讀取流

```
Session 啟動
  │
  └─► prepare_context.py
         │
         ├─► 讀 memory/daily/今天.md + 昨天.md
         ├─► 合併（超 4000tk 時昨日摘要）
         └─► 寫入 memory/recent.md
              │
              └─► 載入為 Agent context 第 6 層

使用者提問
  │
  └─► Planner 判斷是否需 recall
         │
         └─► recall(agent, query, k=5)
                │
                └─► FTS5: bm25 × 時間衰減
                     │
                     └─► 回傳 ≤ 800 tokens 注入 context
```

### 4.3 API 設計

| 端點 | 方法 | 用途 | 請求/回應 |
|------|------|------|-----------|
| `/api/v1/memory/recall` | POST | 查詢記憶 | `{agent, query, k}` → `{results: [{source, date, body, score}]}` |
| `/api/v1/memory/daily` | GET | 取得 daily log | `?agent=&date=` → `{entries: [...]}` |
| `/api/v1/skills/list` | GET | 列出 skills | `?agent=` → `{skills: [{name, version, origin}]}` |
| `/api/v1/skills/pending` | GET | 待審清單 | → `{proposals: [{id, agent, gist, created}]}` |
| `/api/v1/skills/approve` | POST | 核准提案 | `{proposal_id}` → `{status, skill_path}` |
| `/api/v1/skills/reject` | POST | 駁回提案 | `{proposal_id, reason}` → `{status}` |
| `/api/v1/memory/consolidate` | POST | 手動蒸餾 | `{agent}` → `{diff, committed}` |

### 4.4 TG 指令設計

| 指令 | 功能 |
|------|------|
| `/recall <query>` | 查詢 memory FTS5 |
| `/skills` | 列出私有 skills（含 🤖 auto 標記） |
| `/skills pending` | 待審清單 |
| `/consolidate` | 手動觸發 daily → memory.md 蒸餾 |

## 5. 故障隔離與降級策略（Failure Isolation）

| 故障場景 | 影響範圍 | 降級行為 | 恢復方式 |
|----------|----------|----------|----------|
| LLM 不可用（Gemini down） | daily log 生成失敗 | fallback：task_id + 時間戳（純文字，不依賴 LLM） | LLM 恢復後自動恢復 |
| FTS5 索引損壞 | `/recall` 失效 | Wiki 四層搜尋仍可用；啟動時 rebuild 索引 | `python -m src.memory.rebuild_index` |
| memory/daily/ 磁碟滿 | 寫入失敗 | 告警 TG + 跳過寫入（不影響主回覆） | 手動清理 > 30 天 |
| Skill apply 失敗（IO） | 新 skill 未生效 | 保留 pending，TG 通知失敗原因 | 手動 retry 或修正後重新核准 |
| Skill 草稿品質差 | 審批通過率低 | 調高觸發門檻（tool calls 閾值 +2） | 優化 skill-draft prompt |

## 6. 安全性考量（Security）

| 層級 | 措施 |
|------|------|
| Prompt 層 | BRAIN.md 紅線：不寫 .kiro/、不寫 secrets |
| 程式層 | `ALLOWED_WRITE` 白名單：Agent 只能寫 `memory/**` + `pending/**` |
| 審批層 | `ADMIN_CHAT_IDS` 白名單：只有管理者能按 ✅/❌ |
| 版控層 | SKILL.md 落地後 auto git commit，可追溯、可回滾 |
| 索引層 | skills 只索引 name + description，本體不進 FTS5（防洩漏） |

## 7. 可觀測性（Observability）

| 類型 | 實現 |
|------|------|
| Metrics | `logs/memory-stats.json`：每 Agent 的 daily log 數量、memory.md 大小、recall 命中率 |
| Logging | `logs/memory.log`：每次寫入/recall/consolidate 的操作紀錄 |
| Alerting | TG 推送：FTS5 rebuild 失敗、磁碟 > 80%、Skill apply 失敗 |
| Dashboard | Web UI `/admin` 頁：新增「🧠 Memory」tab 顯示各 Agent 記憶統計 |

## 8. 技術棧選擇

| 用途 | 技術 | 理由 |
|------|------|------|
| 記憶儲存 | Markdown 檔案 | 人可讀、可 diff、可 git |
| 全文索引 | SQLite FTS5 | Python 內建、零依賴、已有四層搜尋基礎 |
| 中文分詞 | jieba（現有） | 已在 Wiki Engine 使用，共用 |
| 審批追蹤 | JSON 檔（`data/proposals.json`） | 個人場景夠用、git 可追蹤 |
| 蒸餾/摘要 | Gemini API（現有） | 已整合，無新依賴 |
| 通知 | python-telegram-bot（現有） | 已整合 |

## 9. 模組設計

### 9.1 新增模組

```
src/
├── memory/
│   ├── __init__.py
│   ├── daily_log.py          ← 任務結束寫 daily
│   ├── prepare_context.py    ← agentSpawn 產 recent.md
│   ├── consolidate.py        ← /consolidate 蒸餾
│   ├── recall.py             ← FTS5 查詢
│   ├── indexer.py            ← FTS5 索引建立/更新
│   └── rebuild_index.py      ← CLI: 完整重建索引
├── skills/
│   ├── __init__.py
│   ├── recommend.py          ← 觸發偵測 + 草稿生成
│   ├── manage.py             ← list / apply / reject
│   └── approval_handler.py   ← TG callback 處理
```

### 9.2 修改模組

| 模組 | 修改內容 |
|------|----------|
| `src/agent/process.py` | 任務結束後呼叫 `daily_log.write()` + `recommend.evaluate()` |
| `src/bot/handlers.py` | 新增 `/recall`、`/skills`、`/consolidate` handler |
| `src/bot/callbacks.py` | 新增 skill 審批 Inline Button callback |
| `src/server/routes.py` | 新增 `/api/v1/memory/*` + `/api/v1/skills/*` 端點 |
| `start.py` | 啟動自檢：驗證 steering 4 檔 + memory/ 目錄 |
