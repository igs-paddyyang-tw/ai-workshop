# AI Workshop

> 漸進式 AI Agent 開發教學：Bot → Team → Platform → Skills → Wiki
> 對應 [AI 企業級五層架構](../docs/designs/five-layer-architecture-design.md)，逐步建置自演化 AI 生態系。

## 學習路線：五層架構逐步建置

```
Workshop 01        Workshop 02        Workshop 03        Workshop 04        Workshop 05
┌──────────┐      ┌──────────┐      ┌──────────┐      ┌──────────┐      ┌──────────┐
│ L4 單兵  │  →   │ L3 小隊  │  →   │ L1+L2    │  →   │ L4→L5    │  →   │ L5 知識  │
│ 執行器   │      │ 協作     │      │ 平台 OS  │      │ 技能宣告 │      │ 自演化   │
└──────────┘      └──────────┘      └──────────┘      └──────────┘      └──────────┘
  一個 Bot          一個團隊          一個平台          可攜帶能力        會成長記憶
```

## Workshop 列表

| # | Workshop | 時長 | 五層定位 | 學什麼 |
|---|----------|------|---------|--------|
| 01 | [AI Bot](01-ai-bot-workshop/) | 50 min | L4 執行層 | 單一 Agent 認知循環 + 意圖路由 |
| 02 | [Agent Team](02-agent-team-workshop/) | 50 min | L3 協作層 | 多 Agent 協作 + Leader-Worker |
| 03 | [Platform](03-platform-workshop/) | 50 min | L1+L2 入口/OS | API Gateway + 全域調度 + 四層架構 |
| 04 | [Skills](04-skills-workshop/) | 50 min | L4→L5 銜接 | Skill 宣告化 + AI 協作開發 |
| 05 | [LLM Wiki](05-llm-wiki-workshop/) | 50 min | L5 知識層 | RAG 問答 + 知識圖譜 + 自演化 |

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

# 選一個 Workshop 開始
cd 01-ai-bot-workshop && cat QUICKSTART.md
```
