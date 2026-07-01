# AI Workshop

> 漸進式 AI Agent 開發教學：Bot → Team → Platform → Skills → Wiki
> 對應 [AI 企業級五層架構](../docs/designs/five-layer-architecture-design.md)，逐步建置自演化 AI 生態系。

## 教學理念

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

### 每堂課讓你理解什麼

| Workshop | 你理解了... | 對應五層 |
|----------|-----------|---------|
| 01 | 一個 Agent 怎麼「思考」（意圖路由） | L4 |
| 02 | 多個 Agent 怎麼「協作」（一鍵產出完整平台） | L1-L5 全部 |
| 03 | 平台怎麼「運作」（API + 調度 + 四層架構） | L1+L2 |
| 04 | 能力怎麼「開發」（Spec-Driven + 拷問 + 驗證） | L4→L5 |
| 05 | 知識怎麼「成長」（RAG + ingest + 自演化） | L5 |

### 知識庫規則（所有 Workshop 共用）

```
所有知識先進 raw/ → 排程 LLM ingest → wiki/（唯一產出方式）
Agent 只寫自己的 knowledge/raw/
根目錄 knowledge/ 是共用知識庫
```

---

## 學習路線：五層架構逐步建置

```
Workshop 01        Workshop 02        Workshop 03        Workshop 04        Workshop 05
┌──────────┐      ┌──────────┐      ┌──────────┐      ┌──────────┐      ┌──────────┐
│ L4 單兵  │  →   │ L1-L5    │  →   │ L1+L2    │  →   │ L4→L5    │  →   │ L5 知識  │
│ 執行器   │      │ 全平台   │      │ 理解架構 │      │ 技能開發 │      │ 自演化   │
└──────────┘      └──────────┘      └──────────┘      └──────────┘      └──────────┘
  理解思考          建立團隊           理解運作           理解開發          理解成長
```

## Workshop 列表

| # | Workshop | 時長 | 核心 Skill | 學什麼 |
|---|----------|------|-----------|--------|
| 01 | [AI Bot](01-ai-bot-workshop/) | 50 min | `ark-ai-bot-builder` | 單一 Agent 認知循環 + 意圖路由 |
| 02 | [Agent Team](02-agent-team-workshop/) | 50 min | `ark-agent-team-builder` + `ark-kiro-init` | 多 Agent 協作 + 完整平台產出 |
| 03 | [Platform](03-platform-workshop/) | 50 min | （續用 02） | API + Web + A2A + 五層架構 |
| 04 | [Skills](04-skills-workshop/) | 50 min | `ark-grill-me` + `ark-superpowers` + `ark-code-spec-validator` | Spec-Driven 開發完整迴圈 |
| 05 | [LLM Wiki](05-llm-wiki-workshop/) | 50 min | `ark-wiki-engine` | RAG 問答 + 知識圖譜 + 自演化 |

### 🗞️ 貫穿案例：科技日報的五次升級

「科技日報」是貫穿五堂課的持續案例，同一個需求（每日產出科技新聞摘要），技術逐步升級：

| Workshop | 日報怎麼做 | 升級了什麼 | 瓶頸在哪 |
|----------|-----------|-----------|----------|
| 01 | 手寫爬蟲 + Gemini CLI → HTML | 從零到有 | 一人全做，序列阻塞 |
| 02 | market 爬 + report 渲染 → TG 推送 | 分工並行 | 爬蟲品質靠經驗 |
| 03 | `POST /api/v1/workflows/run` 觸發 | API 化，可整合外部系統 | 缺標準化規格 |
| 04 | Spec-Driven 重構 news_scraper Skill | 有 Spec、有驗證、可信任 | 學到的知識沒沉澱 |
| 05 | 日報結果 ingest → Wiki 趨勢知識庫 | 一次學會，永久可查 | — |

```
01 手動做        02 團隊分工       03 API 觸發       04 品質把關       05 知識沉澱
┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐
│ 一人全做 │ →  │ 分工並行 │ →  │ 標準 API │ →  │ Spec 驗證│ →  │ Wiki 累積│
│ 序列阻塞 │    │ 故障隔離 │    │ 可整合   │    │ Score≥90 │    │ 全域可查 │
└─────────┘    └─────────┘    └─────────┘    └─────────┘    └─────────┘
```

> 💡 每堂課都能獨立運行（可跳堂），但連續上完會看到「同一個需求被逐步升級」的完整旅程。

## 前置條件

- Python 3.12+
- Git
- Kiro CLI 2.7+（Workshop 02+）
- Telegram 帳號 + Bot Token
- Gemini API Key（Workshop 01, 05）
- Node.js 20+（僅 Workshop 03）

## 快速開始

```bash
# 取得 Skills
git clone https://github.com/igs-paddyyang-tw/ark-agent-skills .kiro/skills/

# 教學路徑：選一個 Workshop 開始
cd 01-ai-bot-workshop && cat QUICKSTART.md

# 快速路徑：一鍵產出完整平台
python3 .kiro/skills/ark-agent-team-builder/scripts/build_team.py my-team
python3 .kiro/skills/ark-kiro-init/scripts/build_kiro.py my-team/team.yaml my-team
python3 .kiro/skills/ark-kiro-init/scripts/build_kiro.py --clone-skills my-team
```

## 版本對應

| ai-workshop | ark-agent-team-builder | ark-kiro-init | 產出等同 |
|-------------|----------------------|---------------|---------|
| 目前 | v2.1 | v2.1 | ai-team-agent v1.0.0 |
