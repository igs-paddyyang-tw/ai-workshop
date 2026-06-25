# 🎓 講師指導手冊：Agent Team + Platform（Workshop 02-03）

> 教學重點：為什麼 Agent 需要 .kiro（系統提詞）+ Skills + LLM Wiki 才能真正運作。

---

## 課程定位

```
Workshop 02：建立團隊（動手做）→ 50 min
Workshop 03：理解平台（觀念講）→ 50 min
```

**核心訊息**：AI Agent 不是「跑一次就丟」的腳本，而是有身份、有能力、會成長的隊友。

---

## 教學大綱（建議流程）

### 第一段：Why（10 min）— 為什麼需要這三層

#### 開場問題

> 「如果你有一個 AI 助手，但它每次重開就忘記一切、不知道自己是誰、也不知道怎麼做事——你會怎麼辦？」

#### 三層解法圖

```
問題                    解法                     檔案
────────────────────────────────────────────────────────────
不知道自己是誰     →   .kiro/steering/SOUL.md   （身份+人格+規則）
不知道怎麼做事     →   .kiro/skills/            （能力模組，按需載入）
做完就忘記         →   knowledge/               （記憶+成長，持久化）
```

#### 類比

```
.kiro = Agent 的「身份證 + 工作手冊」
Skills = Agent 的「工具箱」
Knowledge = Agent 的「筆記本」
```

---

### 第二段：Demo 建團隊（25 min）— Workshop 02 核心

#### Step 1：一鍵產出（5 min）

```bash
python3 .kiro/skills/ark-agent-team-builder/scripts/build_team.py my-team
```

**講解重點**：
- 產出 117 個檔案，包含完整五層架構
- team.yaml = 團隊配置（5 人、角色、working_directory）

#### Step 2：配置 .kiro/（10 min）⭐ 重點講解

```bash
python3 .kiro/skills/ark-kiro-init/scripts/build_kiro.py my-team/team.yaml my-team
python3 .kiro/skills/ark-kiro-init/scripts/build_kiro.py --clone-skills my-team
```

**展示產出結構**：

```
agents/pm-agent/.kiro/
├── steering/
│   └── SOUL.md         ← 打開給學員看
├── skills/             ← ls 給學員看數量
└── settings/mcp.json
```

**打開 SOUL.md 講解三個新增段落**：

| 段落 | 功能 | 為什麼重要 |
|------|------|-----------|
| 🎭 人格與語氣 | 定義 Agent 怎麼「說話」 | 不再是冷冰冰的日誌 |
| 📚 自我成長 | 定義 Agent 怎麼「記住」 | 做完事會寫筆記 |
| 📂 知識庫層級 | 定義 Agent 去哪「找答案」 | 先找自己→再找共用 |

**展示 Skills 安裝**：

```bash
ls my-team/agents/pm-agent/.kiro/skills/
# → ark-superpowers ark-grill-me ark-wiki-engine ...
```

> 「每個角色裝不同工具。Leader 裝規劃工具、Coder 裝開發工具、QA 裝測試工具。」

#### Step 3：設定 + 啟動（10 min）

```bash
cd my-team && python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # 填 Token
python start.py
```

**在 Telegram 測試**：`/start` → `/board` → `/agents`

---

### 第三段：知識庫規則（10 min）— 為什麼 Wiki 是核心

#### 知識流動圖

```
Agent 完成任務
    ↓ 快速記錄
自己的 knowledge/raw/
    ↓ 每日排程 ingest
自己的 knowledge/wiki/（結構化知識）
    ↓ 排程分析「哪些是通用的」
根目錄 knowledge/raw/
    ↓ ingest
根目錄 knowledge/wiki/（全員可搜尋）
```

#### 核心規則（板書/投影）

```
1. 所有知識先進 raw/（快速寫入，不管格式）
2. wiki/ 只能由 LLM ingest 產出（確保品質）
3. Agent 讀取順序：自己的 → 共用的
4. Agent 只能寫自己的 knowledge/raw/
```

#### 為什麼這樣設計？

| 設計 | 理由 |
|------|------|
| raw → ingest → wiki | 原始筆記品質不穩定，LLM 萃取保證結構化 |
| 先讀自己 | 專業分工，每個 Agent 有自己的領域知識 |
| 禁止直接寫共用 | 避免垃圾知識污染全團隊 |

---

### 第四段：Platform 架構理解（5 min）— Workshop 03 預覽

```
┌─────────────────────────────────────────────┐
│ L1 Entry     │ Telegram + API + Web Board   │
├──────────────┼──────────────────────────────┤
│ L2 OS        │ TaskLifecycle + Scheduler    │
├──────────────┼──────────────────────────────┤
│ L3 Collab    │ A2A Router + TaskGraph       │
├──────────────┼──────────────────────────────┤
│ L4 Execution │ RuntimeRegistry (4 providers)│
├──────────────┼──────────────────────────────┤
│ L5 Knowledge │ Wiki Engine + raw→ingest     │
└──────────────┴──────────────────────────────┘
```

> 「02 建了它，03 教你理解它每一層在做什麼。」

---

## 講師備忘

### 必須提前準備

- [ ] Telegram Bot Token 已取得
- [ ] `.kiro/skills/` 已 clone
- [ ] Python 3.12+ 確認
- [ ] 網路可連（pip install 需要）

### 常見卡關點

| 問題 | 解法 |
|------|------|
| `No module named 'telegram'` | `source .venv/bin/activate` |
| Bot 沒回應 | 確認 .env Token 正確 |
| port 被佔 | `fuser -k 33333/tcp` |
| `Conflict: terminated by other getUpdates` | 只能跑一個 Bot instance |

### 如果時間不夠

| 優先 | 必做 | 可跳過 |
|------|------|--------|
| 高 | build_team.py + 講解 SOUL.md | 手動設定 Telegram |
| 中 | build_kiro.py --clone-skills | 實際啟動 Bot |
| 低 | 知識庫規則講解 | Workshop 03 API 部分 |

### 金句（可用於投影片）

> 「Agent 沒有 .kiro 就像員工沒有工作手冊——不知道自己該做什麼。」

> 「Skills 是 Agent 的超能力——按需載入，用完不佔記憶體。」

> 「knowledge/raw/ 是草稿紙，wiki/ 是教科書。草稿可以亂寫，教科書必須精煉。」

> 「一個 Agent 學會的，透過知識庫同步，全團隊受益。」

---

## 投影片建議順序

1. 問題：AI Agent 的三大痛點（遺忘/無能力/無身份）
2. 解法：.kiro + Skills + Knowledge 三層
3. Demo：build_team.py 一鍵產出
4. 展示：SOUL.md 打開看（🎭📚📂）
5. 展示：Skills 列表（依角色不同）
6. 規則：知識庫流動圖（raw → ingest → wiki）
7. 啟動：Telegram /start /board
8. 預告：03 教你理解五層架構每一層在做什麼

---

## 延伸問答

| Q | A |
|---|---|
| Skills 太多會不會很慢？ | 不會，只有觸發時才載入（三層漸進式） |
| Agent 可以自己學新 Skill 嗎？ | 可以，透過 04 Workshop 的 ark-skill-creator |
| 知識庫多大會有問題？ | SQLite FTS5 處理幾萬頁沒問題 |
| 可以讓 Agent 忘記某些知識嗎？ | 刪除 wiki/ 中的頁面 + 更新 index.md |
| 不同團隊的 Agent 可以共享知識嗎？ | 可以，根目錄 knowledge/ 就是共用的 |

---

*講師：paddyyang ｜ 更新：2026-06-25*
