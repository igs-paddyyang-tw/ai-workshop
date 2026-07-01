# AI Workshop

> 漸進式 AI Agent 開發教學：說話 → 做事 → 記住 → 合作 → 管理
> 對應 [AI 企業級五層架構](../docs/designs/five-layer-architecture-design.md)，逐步建置自演化 AI 生態系。

## 教學理念

### 能力遞增路線

```
01 它能「說話」    （有人格的對話）
02 它能「做事」    （有技能的執行）
03 它能「記住」    （有記憶的學習）
04 它們能「合作」  （有團隊的分工）
05 你能「管理」    （有平台的掌控）
```

### 兩條路到同一目的地

```
路徑 A（教學路徑）：理解每一層
  01 → 02 → 03 → 04 → 05（5×50 min，逐步理解）

路徑 B（快速路徑）：一鍵產出
  build_team.py + build_kiro.py --clone-skills（5 min，直接跑）
```

兩條路最終產出一模一樣的系統。Workshop 教你**為什麼**這樣設計，而非只教你**怎麼用**。

### 核心公式

```
ark-agent-team-builder（骨架 + Phase 1-4）
  + ark-kiro-init（.kiro 配置 + Skills 預裝 + 知識庫）
  ═══════════════════════════════════════════════
  = 完整 AI Agent Team 平台（自演化、自我成長）
```

### 每堂課讓你學會什麼

| Workshop | 你學會了... | 對應五層 |
|----------|-----------|---------|
| 01 Agent 初始 | 一個 Agent 怎麼「思考」和「說話」（系統提詞 + 意圖路由） | L4 |
| 02 Skills | 能力怎麼「開發」（Spec-Driven + 拷問 + 驗證） | L4→L5 |
| 03 Wiki | 知識怎麼「成長」（RAG + ingest + 自演化） | L5 |
| 04 Agent Team | 多個 Agent 怎麼「協作」（團隊派工 + 並行 + 隔離） | L1-L5 全部 |
| 05 平台管理 | 平台怎麼「運作」（API + Dashboard + 費用 + 監控） | L1+L2 |

---

## 學習路線：個體到群體

```
Workshop 01        Workshop 02        Workshop 03        Workshop 04        Workshop 05
┌──────────┐      ┌──────────┐      ┌──────────┐      ┌──────────┐      ┌──────────┐
│ 🤖 說話  │  →   │ 🛠️ 做事  │  →   │ 📚 記住  │  →   │ 👥 合作  │  →   │ ⚙️ 管理  │
│ 系統提詞 │      │ Skill 開發│      │ RAG 知識庫│      │ Agent Team│      │ Dashboard│
└──────────┘      └──────────┘      └──────────┘      └──────────┘      └──────────┘
  一個 Agent        教它新能力         給它長期記憶       變成一個團隊        管理 AI 艦隊
```

## Workshop 列表

| # | Workshop | 時長 | 核心 Skill | 學什麼 |
|---|----------|------|-----------|--------|
| 01 | [Agent 初始](01-agent-workshop/) | 50 min | `ark-agent-builder` | 系統提詞 + 意圖路由 + Bot 啟動 |
| 02 | [Skills 開發](02-skills-workshop/) | 50 min | `ark-grill-me` + `ark-superpowers` + `ark-code-spec-validator` | Spec-Driven 完整迴圈 |
| 03 | [LLM Wiki](03-llm-wiki-workshop/) | 50 min | `ark-wiki-engine` | RAG 問答 + 知識圖譜 + 自演化 |
| 04 | [Agent Team](04-agent-team-workshop/) | 50 min | `ark-agent-team-builder` + `ark-kiro-init` | 多 Agent 協作 + 完整平台產出 |
| 05 | [平台管理](05-platform-workshop/) | 50 min | （續用 04） | API + Dashboard + 費用 + 監控 |

### 🗞️ 貫穿案例：科技日報的五次升級

「科技日報」是貫穿五堂課的持續案例，同一個需求技術逐步升級：

| Workshop | 日報怎麼做 | 升級了什麼 | 瓶頸在哪 |
|----------|-----------|-----------|----------|
| 01 | Bot 觸發 NewsSkill → 抓 HN 首頁 | 從零到有，Bot 能回答新聞 | 只有一個技能，沒有規格 |
| 02 | Spec-Driven 重構 NewsSkill（多來源+重試） | 有品質驗證，Score ≥ 90 可信任 | 知識沒沉澱 |
| 03 | 日報結果 ingest → Wiki，可問趨勢 | 一次學會永久可查 | 一人做到死 |
| 04 | market 爬 + report 渲染 → TG 推送 | 分工並行，故障隔離 | 缺乏監控 |
| 05 | Dashboard 看成功率 + 費用 + 排程管理 | 全盤掌控 | — |

```
01 觸發新聞      02 品質重構       03 知識沉澱       04 團隊分工       05 全盤管理
┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐
│ 一個Bot │ →  │ Spec 驗證│ →  │ Wiki 累積│ →  │ 5人並行 │ →  │ Dashboard│
│ 能抓新聞│    │ Score≥90 │    │ 永久可查 │    │ 故障隔離 │    │ 費用監控 │
└─────────┘    └─────────┘    └─────────┘    └─────────┘    └─────────┘
```

> 💡 每堂課都能獨立運行（可跳堂），但連續上完會看到「同一個需求被逐步升級」的完整旅程。

## 前置條件

- Python 3.12+
- Git
- Telegram 帳號 + Bot Token
- Gemini API Key（Workshop 01, 03）
- Kiro CLI 2.7+（Workshop 04+）
- Node.js 20+（僅 Workshop 05）

## 快速開始

```bash
# 取得 Skills
git clone https://github.com/igs-paddyyang-tw/ark-agent-skills .kiro/skills/

# 教學路徑：選一個 Workshop 開始
cd 01-agent-workshop && cat QUICKSTART.md

# 快速路徑：一鍵產出完整平台
python3 .kiro/skills/ark-agent-team-builder/scripts/build_team.py my-team
python3 .kiro/skills/ark-kiro-init/scripts/build_kiro.py my-team/team.yaml my-team
python3 .kiro/skills/ark-kiro-init/scripts/build_kiro.py --clone-skills my-team
```

## 知識庫規則（所有 Workshop 共用）

```
所有知識先進 raw/ → 排程 LLM ingest → wiki/（唯一產出方式）
Agent 只寫自己的 knowledge/raw/
根目錄 knowledge/ 是共用知識庫
```

## 版本對應

| ai-workshop | ark-agent-team-builder | ark-kiro-init | 產出等同 |
|-------------|----------------------|---------------|---------|
| v2.0（新順序） | v2.1 | v2.1 | ai-team-agent v1.0.0 |
