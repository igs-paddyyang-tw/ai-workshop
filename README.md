# AI Workshop

> 五堂課建立自演化 AI 團隊。用 Kiro IDE vibe coding + Telegram 即時驗證。

---

## 教學目的

本 Workshop 的終極目標：**學員能獨立建立一條 AI Agent 供應鏈** — 從「打造專家」到「讓專家自動跑」。

### 兩個獨立產品

| | 🏗️ AI Agent 專家系統平台（ai-bot） | 🔄 AI Agent 遊戲開發平台（ai-team-agent） |
|---|---|---|
| **一句話** | 打造各領域 Agent 專家，累積可複用的能力資產 | 讓 Agent 團隊自動循環開發出一款遊戲 |
| **聚焦** | **駕馭能力** — SOUL / Skill / 知識庫的調整與精煉 | **迴圈工程** — 設計好迴圈讓系統自己跑、自己學 |
| **人工介入** | 深 — 人是方向盤，AI 是引擎 | 淺 — 系統主導，人監督 |
| **操作方式** | IDE（軟體人）+ TG（非軟體人）雙軌駕馭 | 設定好 team.yaml + scheduler.yaml 後自動運作 |
| **產出** | 成熟的 SOUL + Skill + 知識庫（能力資產） | 遊戲成品（程式碼 + 資源 + 報告） |

### 兩者的關係：供應鏈

```
┌─────────────────────────────────────────────────────────────────────────┐
│                                                                          │
│   🏗️ 專家系統平台（鍛造廠）          🔄 遊戲開發平台（生產線）           │
│                                                                          │
│   ┌──────────────────────┐           ┌──────────────────────┐          │
│   │ 駕馭 + 調整 + 蒸餾    │  ──────→  │ 消費 + 自動循環       │          │
│   │                      │   提供     │                      │          │
│   │ • 精煉 SOUL          │  成熟的   │ • Agent 團隊自轉      │          │
│   │ • 開發 Skill         │  能力資產  │ • 排程自動派工        │          │
│   │ • 累積知識庫         │           │ • 自動產出遊戲        │          │
│   │                      │  ←──────  │                      │          │
│   │ 重新磨刀             │   回報     │ 遇到問題回饋         │          │
│   └──────────────────────┘   問題     └──────────────────────┘          │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

**專家系統是上游** — 負責鍛造 Agent 的能力（SOUL 怎麼寫、Skill 怎麼設計、知識庫怎麼結構化）。這個過程需要人深度介入、反覆調整、不斷蒸餾。

**遊戲開發平台是下游** — 消費上游蒸餾好的能力資產，讓 Agent 團隊按照設定好的迴圈自動運作。遇到能力不足時，回上游的專家系統重新調整，再讓下游參考學習。

### 為什麼概念相通、架構遞進

兩個產品用**同一套人格資產**（SOUL / Skills / Knowledge / Memory），
但**分屬兩個套件**：

| | ai-bot | ai-team-agent |
|---|---|---|
| **套件** | `ark_bot_agent` | `ark_team_agent` |
| **是什麼** | 單一 bot 入口（TG polling + Web UI） | 多 agent 常駐 daemon（health port + 排程） |
| **你維護的** | `agents.yaml` + `bot.yaml` + SOUL | `team.yaml` + `scheduler.yaml` + SOUL |
| **驅動方式** | 模式路由（chat / agent / team） | 配置 + 排程驅動（`instances` / `group`） |
| **runtime 在哪** | wheel 裡 | wheel 裡 |

> 🔴 **兩邊的專案資料夾裡都沒有 runtime 程式碼。** 框架在套件裡，
> 你維護的是**設定與人格** —— 這是整個 workshop 的核心觀念。

這是刻意的遞進設計：
1. **Course A 學會定義一個 agent**（SOUL / Skills / Wiki / Memory）
2. **Course B 學會定義一個團隊**（誰在團隊、派工歸屬、何時自動做什麼）
3. **人格資產可搬運** — 在 ai-bot 鍛造好的 `agents/<name>/.kiro/steering/SOUL.md`
   可以直接搬到 ai-team-agent 使用（兩邊同形狀）

就像先學會定義一個角色，再學會編一個團隊。

### Loop Engineering — 標配五件套

兩個產品都預裝 **Loop 底座**（`.kiro/skills/`），形成從需求到交付的自動迴圈：

```
ark-grill-me → ark-superpowers → ark-spec-executor → ark-code-spec-validator
   拷問釐清        文件產出          自動執行            品質驗證
       ↑                                                    │
       └────────────── score < 70 時回到拷問 ───────────────┘
```

| Skill | 功能 | 觸發方式 |
|-------|------|----------|
| ark-grill-me | 需求不清時逐一提問，達成共識 | 「拷問」、「grill me」 |
| ark-superpowers | 產出 Spec / Design / Plan 標準化文件 | 「寫 spec」、「設計文件」 |
| ark-spec-executor | 讀取 Plan 自動執行 + AC 驗收 + 報告 | `/execute plan.md` |
| ark-code-spec-validator | 驗證 code 與 spec 一致性（Drift Report） | 「驗證 drift」 |
| ark-prompt-spec-validator | 驗證提詞 / AI 內文（SKILL.md、SOUL.md） | 「驗提詞」、「prompt lint」 |
| ark-wiki-engine | 知識庫四層搜尋 + RAG 問答 | 「查知識」、`/wiki` |
| ark-md-report / ark-html-report | 產報告（給 AI 看 / 給人看，成對） | 「產出報告」 |

> Skills 來源：[igs-paddyyang-tw/ark-agent-skills](https://github.com/igs-paddyyang-tw/ark-agent-skills)
> —— 共用庫現有 **50 個 active**（這行是手寫的，**數字以 `scripts/check_docs.py` 輸出為準**）。
> 課程 B 用 `scripts/sync_skills.py` 依角色矩陣分配，不是每個 agent 都裝全部。

---

## 兩個獨立課程

| 課程 | 名稱 | 堂數 | 你學會 |
|------|------|------|--------|
| **[A](course-ai-bot/)** | AI Agent 開發入門 | 3 堂 | 說話 → 做事 → 記住 |
| **[B](course-ai-team-agent/)** | AI Agent Team 實戰 | 2 堂 | 合作 → 自己跑 |

## 五堂課能力遞進

| 堂 | 主題 | 一句話 | Skill | 帶走的能力 |
|---|------|--------|-------|-----------|
| 01 | 🗣️ Agent 初始 | 改 SOUL → Bot 行為變 | ark-agent-bot-builder + ark-agent-init | 為任何場景設計 AI 人格 |
| 02 | ⚡ Skills 開發 | 拷問 → Spec → 實作 → 驗證 | grill-me + superpowers + skill-creator + validator | Spec-Driven 開發方法 |
| 03 | 🧠 LLM Wiki | 加知識 → 回答有依據 | ark-wiki-engine | 建立知識庫 + 自演化 |
| 04 | 🤝 Agent Team | 一句話派工 → 自動分工 | ark-agent-team-builder + ark-agent-init + sync_skills | 建立 AI 團隊 |
| 05 | 🏭 營運落地 | 排程 + 費控 = 自動運作 | — | 從 Demo 到正式上線 |

```
01 控制 AI 說什麼（SOUL）
 ↓
02 保證做得好（Spec-Driven）
 ↓
03 越用越聰明（RAG + 自演化）
 ↓
04 一群 AI 協作（Team）
 ↓
05 自動運作（排程 + 費控 + 監控）
```

## 教學方式

**你不需要寫程式。** 打字告訴 Kiro IDE 你要什麼 → 去 Telegram 驗證結果。

| 操作 | 圖示 | 做什麼 |
|------|------|--------|
| Kiro IDE | 📝 | 自然語言指示 AI 修改程式碼 |
| 終端 | 💻 | 啟動服務、curl API |
| Telegram | 📱 | 手動驗證效果（= 使用者視角） |

### 兩個工程思維 × 兩個產品

| 課程 | 思維 | 核心心法 | 對應產品 |
|------|------|---------|---------|
| A（01-03） | 🏗️ LLM-Driven（AI 判斷） | AI 決定怎麼做，你控制它能做什麼 | 專家系統平台 |
| B（04-05） | 🔄 Config-Driven（你設計迴圈） | 你定義流程和排程，系統按配置自轉 | 遊戲開發平台 |

Course A 教你「鍛造專家」— 用 SOUL / Skills / Wiki 定義 AI 的能力邊界，讓 Gemini ReAct 自行判斷如何完成任務。
Course B 教你「架設產線」— 用 team.yaml + scheduler.yaml 定義誰做什麼、何時做，系統按配置自動運作。

從 A 到 B 的升級路徑：
```
ai-bot（LLM 判斷派工）→ 把 agents/ 搬過去 → ai-team-agent（配置定義迴圈）
```

## 快速開始

### 🚀 一鍵（90 秒，產出當場能跑的專案）

```bash
# 課前下載兩個 wheel 放進本目錄：github.com/igs-paddyyang-tw/{ark_bot_agent,ark_team_agent}/releases

./create.sh bot  my-bot  --wheel ./ark_bot_agent-<版本>-py3-none-any.whl
./create.sh team my-team --wheel ./ark_team_agent-<版本>-py3-none-any.whl
```

它一次做完七件事 —— 這七件事裡只有最後一件對學習有價值：

| | 步驟 | |
|---|---|---|
| 1 | 產骨架（`knowledge/shared` · `memory` · `artifacts` 三個缺口都補齊） | 機械 |
| 2 | 建 venv + 裝 wheel（**自動帶 `[search,skills]`**） | 機械 |
| 3 | **驗 import 版號**（不看 pip 輸出） | 機械 |
| 4 | 驗 extras 真的裝到（缺了會靜默降級，不報錯） | 機械 |
| 5 | 依 preset 產出**每個 agent 的 SOUL.md** | 機械 |
| 6 | 跑上游 validator 驗交叉引用 | 機械 |
| 7 | 印「還差什麼才能跑」 | — |
| → | **填 token + 改 SOUL** | 🎯 這才是課程 |

### 三個 preset（`presets/*.yaml`）

| preset | 編制 | 給誰 |
|---|---|---|
| `general`（預設） | 通用開發團隊 6 角色 | 大多數專案 |
| `gamedev` | 遊戲開發團隊 8 角色 | 本 workshop 的貫穿案例 |
| `minimal` | 單一 agent | 想自己從零設計編制 |

```bash
./create.sh bot my-bot --preset gamedev
./create.sh bot my-bot --dry-run        # 先看它會做什麼
```

### 🎨 客製化只有三個地方

| 專案 | 改什麼 |
|---|---|
| bot | `agents.yaml`（有誰） · `bot.yaml`（怎麼跑） · `.kiro/steering/SOUL.md`（是誰） |
| team | `team.yaml`（誰在團隊 + 派工歸屬） · `scheduler.yaml`（何時） · 各 `SOUL.md` |

**其他都不用碰** —— runtime 在套件裡。

### 或者直接跑現成範例

```bash
cd samples/ai-bot          # ark_bot_agent 消費端
python3 -m venv .venv && source .venv/bin/activate
pip install './ark_bot_agent-<版本>-py3-none-any.whl[search,skills]'
cp .env.example .env       # 填你自己的 TELEGRAM_BOT_TOKEN
python start.py

cd samples/ai-team-agent   # ark_team_agent 消費端
python3 -m venv .venv && source .venv/bin/activate
pip install './ark_team_agent-<版本>-py3-none-any.whl'
python3 scripts/sync_skills.py
cp .env.example .env
python start.py            # ⏱️ 首次冷啟到能回私訊要 2–4 分鐘
```

驗證：
```bash
curl -s localhost:8000/health         # bot（ark_bot_agent 是 /health）
curl -s localhost:23050/api/health    # team（ark_team_agent 是 /api/health）
open http://localhost:28050           # team 看板（health_port + 5000）
```

> 🔴 **每人用自己的 Telegram Bot Token** —— 同一 token 兩處 polling 會隨機吃訊息且不報錯。

## 貫穿案例：遊戲競品分析

五堂課使用同一個業務情境，逐步升級：

| 堂 | 做什麼 |
|----|--------|
| 01 | 設計「遊戲分析師」的 SOUL |
| 02 | 開發新聞爬蟲 Skill（Spec-Driven） |
| 03 | 匯入 Ocean King / Super Ace 競品分析到 Wiki |
| 04 | market + designer + report 三 Agent 協作產出報告 |
| 05 | 排程每天自動產出科技日報 + 每週競品週報 → 產出自動累積成知識 |

## 目錄結構

```
ai-workshop/
├── README.md
├── course-ai-bot/                  ← 課程 A 教材
│   ├── QUICKSTART-01-agent.md      ← 第一堂（SOUL 設計）
│   ├── QUICKSTART-02-skills.md     ← 第二堂（Spec-Driven）
│   ├── QUICKSTART-03-wiki.md       ← 第三堂（RAG 知識庫）
│   ├── build-guide.md              ← 完整規格（課後參考）
│   └── sample-docs/                ← Wiki 範例素材
├── course-ai-team-agent/           ← 課程 B 教材
│   ├── QUICKSTART-04-team.md       ← 第四堂（團隊派工）
│   ├── QUICKSTART-05-platform.md   ← 第五堂（營運落地）
│   └── build-guide.md              ← 完整規格（課後參考）
├── samples/                        ← 完整可跑範例（帶走用，**都是套件消費端**）
│   ├── ai-bot/                     ← 🏗️ ark_bot_agent 消費端（設定 + 人格，無 runtime）
│   └── ai-team-agent/              ← 🔄 ark_team_agent 消費端（team.yaml 即架構）
├── docs/                           ← 文件
│   ├── quickstart-ai-bot.md        ← 課前自學：從零到第一次對話
│   ├── quickstart-llm-wiki.md      ← 知識庫的獨立使用
│   ├── teaching-philosophy.md      ← 教學理念
│   ├── specs / designs / plans     ← 本 repo 自己的工程文件
│   └── wiki/                       ← ADR + learnings
├── reports/                        ← HTML 總覽與課程簡報
├── create.sh                       ← 🚀 一鍵產出可跑的專案
├── presets/                        ← general / gamedev / minimal 編制範本
├── scripts/
│   ├── create_project.py           ← 一鍵的實作
│   └── check_docs.py               ← 🛡️ 教材守門（改教材後跑它）
├── shared/                         ← 共用資源
└── instructor/                     ← 講師指南
```

> 🛡️ **改完教材要跑守門**：`python3 scripts/check_docs.py`（看 rc，**不要接 pipe**
> —— pipe 會吃掉非 0 的 rc）。它會抓已移除的 skill 名、不存在的腳本、斷掉的路徑、
> 以及「sample 退回手搭架構」。

## 前置條件

| 工具 | 課程 A | 課程 B |
|------|--------|--------|
| Python 3.12+ | ✅ | ✅ |
| Telegram Bot Token | ✅ | ✅ |
| Gemini API Key | ✅ | ✅ |
| Kiro IDE | ✅ | ✅ |

## 學完能做什麼

| 堂 | 職場應用 |
|----|---------|
| 01 | 幫公司建一個有品牌風格的客服 / 助手 Bot |
| 02 | 用 Spec 管理 AI 功能開發（可交接、可審核、可驗證） |
| 03 | 建立公司知識庫，新人問 Agent 就有依據的答案 |
| 04 | AI 團隊自動處理日常（新聞 / 競品分析 / 報告） |
| 05 | 排程自動跑 + 費用控管 + 任務監控 = 正式上線 |

**完整學完 = 你有一條 AI Agent 供應鏈：**

```
專家系統（鍛造）→ 能力蒸餾 → 遊戲開發平台（生產）→ 回饋問題 → 專家系統（再鍛造）
```

---

*兩個課程完全獨立，可分開授課。帶走 `samples/` 就能直接用在業務。*
*兩個產品架構相同，能力資產互通，形成自演化的正向迴圈。*
