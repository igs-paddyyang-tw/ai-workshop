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

### 為什麼架構相同

兩個產品的程式碼架構一模一樣（coordinator / runtime / gateway），差異只在：
- **放了什麼 Agent**（不同領域的 SOUL + Skill）
- **有沒有 team.yaml**（個體 vs 團隊）
- **有沒有 scheduler.yaml**（手動 vs 自動）
- **knowledge/ 裝了什麼**（不同領域的知識）

就像兩台同型號的機器，一台用來鍛造刀具，一台用來切割材料。機器相同，用途不同。

這確保：
1. 學員學一套架構，兩邊都會用
2. 專家系統蒸餾的 Agent 能力（agents/ 資料夾）可以直接搬到遊戲開發平台用
3. 遇到問題隨時回專家系統調整，不需要適配

### Loop Engineering — 標配五件套

兩個產品都預裝了 **Loop 五件套**（`.kiro/skills/`），形成從需求到交付的自動迴圈：

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
| ark-wiki-engine | 知識庫四層搜尋 + RAG 問答 | 「查知識」、`/wiki` |

> Skills 來源：[igs-paddyyang-tw/ark-agent-skills](https://github.com/igs-paddyyang-tw/ark-agent-skills)（57 個）

---

## 兩個獨立課程

| 課程 | 名稱 | 堂數 | 你學會 |
|------|------|------|--------|
| **[A](course-ai-bot/)** | AI Agent 開發入門 | 3 堂 | 說話 → 做事 → 記住 |
| **[B](course-ai-team-agent/)** | AI Agent Team 實戰 | 2 堂 | 合作 → 自己跑 |

## 五堂課能力遞進

| 堂 | 主題 | 一句話 | Skill | 帶走的能力 |
|---|------|--------|-------|-----------|
| 01 | 🗣️ Agent 初始 | 改 SOUL → Bot 行為變 | — | 為任何場景設計 AI 人格 |
| 02 | ⚡ Skills 開發 | 拷問 → Spec → 實作 → 驗證 | grill-me + superpowers + skill-creator + validator | Spec-Driven 開發方法 |
| 03 | 🧠 LLM Wiki | 加知識 → 回答有依據 | ark-wiki-engine | 建立知識庫 + 自演化 |
| 04 | 🤝 Agent Team | 一句話派工 → 自動分工 | ark-agent-team-builder + ark-kiro-init | 建立 AI 團隊 |
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
| A（01-03） | 🏗️ 駕馭工程 | 你是方向盤，AI 是引擎。你決定去哪。 | 專家系統平台 |
| B（04-05） | 🔄 迴圈工程 | 設計迴圈不是步驟。讓系統自己跑、自己學。 | 遊戲開發平台 |

課程 A 教你「鍛造刀具」— 把 Agent 調到好用。
課程 B 教你「架設生產線」— 讓好用的 Agent 自動跑。
從 A 到 B，Agent 的能力被蒸餾、搬運、複用。

## 快速開始

```bash
# 課程 A：個體 Agent
cd samples/ai-bot
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt && cp .env.example .env
# 填入 TELEGRAM_BOT_TOKEN + GEMINI_API_KEY
python start.py

# 課程 B：Agent Team
cd samples/ai-team-agent
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt && cp .env.example .env
# 填入 TELEGRAM_BOT_TOKEN + GEMINI_API_KEY
python start.py
```

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
├── samples/                        ← 完整可跑範例（帶走用）
│   ├── ai-bot/                     ← 🏗️ AI Agent 專家系統平台（駕馭工程）
│   └── ai-team-agent/             ← 🔄 AI Agent 遊戲開發平台（迴圈工程）
├── docs/                           ← 文件
│   ├── ai-workshop-guide.html      ← 分頁總覽（首頁+A+B+進階）
│   └── enterprise-5-layer-architecture.html
├── shared/                         ← 共用資源
└── instructor/                     ← 講師指南
```

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
