---
title: "8 Agent 完整 .kiro/ 配置標準化"
type: onepager
status: executing
created: 2026-07-02
---

# 8 Agent 完整 .kiro/ 配置標準化

## 目標

每個 Agent 都有完整的 `.kiro/` 配置，可直接使用：

```
agents/{name}-agent/.kiro/
├── steering/
│   ├── SOUL.md          ← 角色人格（八段式）
│   ├── KIRO.md          ← 程式碼/行為規範
│   ├── memory.md        ← 記憶規則
│   └── USER.md          ← 使用者偏好
├── settings/
│   └── mcp.json         ← MCP 工具配置
├── prompts/
│   └── route-message.md ← 意圖路由提詞
└── agents/
    └── {name}-agent.json ← Agent 定義
```

加上：
- `skills/` — 該角色必要的工作流定義
- `knowledge/raw/` — 初始知識（含 llm-wiki 種子）
- `output/` — 產出範例

## 8 個 Agent 角色定義

| # | Agent | 職責 | 必要 Skills | 知識種子 |
|---|-------|------|------------|---------|
| 1 | 👑 admin | 管家 + 智能分流 + 目錄配置管理 | env-doctor, cost-tracker | 系統架構、配置說明 |
| 2 | 📋 pm | 專案經理 + 派工 | grill-me, superpowers, planning | 專案管理方法論 |
| 3 | 🧠 ai-dev | AI 工程師 | llm-tools, mcp-builder, skill-creator | Prompt 工程、LLM 整合 |
| 4 | 💻 coder | 全端開發 | webapp-generator, code-review, db-query | Python/FastAPI 慣例 |
| 5 | 🧪 qa | 品質保證 | test-runner, code-spec-validator, security-audit | 測試策略、品質標準 |
| 6 | 📊 data | 數據分析（內部） | db-query, chart-generator, kpi-calculator | 數據分析方法、KPI 定義 |
| 7 | 🗺️ market | 市場研究（外部） | web-scraper, news-daily, community-ops | 市場研究方法、資訊來源 |
| 8 | 📝 report | 報告產出（彙整） | report-template, html-dashboard, chart-generator | 報告格式、模板規範 |

## 放置位置

- **sample/a-agent/agents/**: 4 個（admin + news→market 改名 + code→coder + wiki→改用途）
- **ark-agent-builder/templates/agents/**: 8 個完整範例（使用者選用）

## 統一規格

每個 Agent 的 SOUL.md 八段式：
1. 身份（角色 + emoji + 一句話定位）
2. 人格（3-4 個特質）
3. 能力（5-6 項具體能力）
4. 邊界（不做什麼）
5. 工作流程（收到任務 → 執行 → 回報）
6. 輸出格式（回覆風格）
7. 成長規則（如何更新 knowledge）
8. 禁制（絕對不可做的事）
