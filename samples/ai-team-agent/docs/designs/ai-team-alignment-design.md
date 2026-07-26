---
title: "ai-team-agent 借鑑 minecraft 優化設計"
status: draft
created: 2026-07-27
type: design
language: zh-TW
related_spec: docs/specs/ai-team-alignment-spec.md
---

# ai-team-agent 借鑑 minecraft 優化設計

## 1. 概述

本設計文件定義四項優化的具體架構決策，確保教學範本正確借鑑生產版經驗，同時不破壞可讀性與現有機制。

---

## 2. ADR-1：state/tasks 目錄結構設計

**決策：** 建立目錄結構 + 初始化骨架檔案，暫不實作讀寫邏輯。

**理由：**
- 方案 A：只建目錄 → 讀者無法理解用途
- 方案 B（選此）：建目錄 + 初始化 JSON + 說明 → 教學價值高，讀者可自行擴充
- 方案 C：完整實作讀寫 → 超出本期範圍，增加教學複雜度

**目錄設計（對齊 minecraft）：**

```
state/
├── heartbeat/              ← agent 心跳 JSON（每 agent 一個）
│   └── .gitkeep
├── board.json              ← 任務看板初始骨架
└── .gitkeep

tasks/
└── items/
    └── .gitkeep
```

**board.json 初始骨架：**
```json
{
  "version": "1.0",
  "tasks": [],
  "updated_at": null
}
```

---

## 3. ADR-2：skills.json + skill-mapping.yaml 設計

**決策：** 採用 minecraft 的兩層設計（mapping → per-agent json）。

**理由：**
- 方案 A：只有 skills.json → 每個 agent 手動維護，容易不一致
- 方案 B（選此）：mapping.yaml 作為 source of truth → per-agent json 由 mapping 生成，易維護
- 方案 C：合併到 mcp.json → 職責混亂

**skill-mapping.yaml 設計：**

```yaml
roles:
  manager:        # mc-agent
    skills: [ark-project-planning, ark-internal-comms, ark-superpowers]

  admin:          # admin-agent
    skills: [ark-env-doctor, ark-docker-deploy, ark-dashboard-health, ark-security-audit]

  leader:         # pm-agent
    skills: [ark-superpowers, ark-project-planning, ark-planning-with-files, ark-grill-me, ark-spec-executor, ark-uml-generator]

  worker-ai-dev:  # ai-dev-agent
    skills: [ark-mcp-builder, ark-llm-tools, ark-browser-tool]

  worker-coder:   # coder-agent
    skills: [ark-webapp-generator, ark-frontend-design, ark-db-query]

  worker-qa:      # qa-agent
    skills: [ark-test-runner, ark-code-review, ark-security-audit]

  worker-data:    # data-agent
    skills: [ark-chart-generator, ark-etl-pipeline, ark-db-query]

  worker-market:  # market-agent
    skills: [ark-web-scraper, ark-news-daily, ark-landing-page]

  worker-report:  # report-agent
    skills: [ark-chart-generator, ark-news-daily, ark-report-template]

shared:
  skills: [ark-wiki-engine, ark-code-spec-validator, ark-doc-coauthoring]
```

**per-agent skills.json 格式（對齊 minecraft）：**

```json
{
  "role": "admin",
  "skills": [
    "ark-env-doctor",
    "ark-docker-deploy",
    "ark-dashboard-health",
    "ark-security-audit",
    "ark-wiki-engine",
    "ark-code-spec-validator",
    "ark-doc-coauthoring"
  ]
}
```

---

## 4. ADR-3：Steering 精簡策略

**決策：** 合併到 4 檔（SOUL/BRAIN/MEMORY/TEAM），KIRO.md 保留為 fileMatch。

**合併對應表：**

| 被合併 | 去處 | 在 BRAIN 的位置 |
|--------|------|----------------|
| AGENTS.md（MCP 工具規範） | BRAIN.md | 第一節「工具」 |
| USER.md（使用者偏好） | SOUL.md | 最後段「使用者資訊」 |
| GUARDRAILS.md（若存在） | BRAIN.md | 「護欄」節 |
| KIRO.md | 保留獨立（fileMatch） | — |

**執行策略：**
1. 先更新 BRAIN.md 加入 AGENTS 內容
2. 更新 SOUL.md 加入 USER 內容
3. 刪除 AGENTS.md / USER.md
4. KIRO.md 不動（inclusion: fileMatch，不佔常駐）

**根 .kiro/steering/ 同步：**
- 根 BRAIN 已有工具規範框架（本次略加 MCP 工具段）
- 刪除根 AGENTS.md + USER.md

---

## 5. ADR-4：TEAM.md 全員統一設計

**決策（2026-07-27 修正）：** 不加 mc-agent。改為統一 8 個 agent 的 TEAM.md 內容。

**原始問題：** 各 agent TEAM.md 只列 4-5 人，instance 名稱有誤（`dev-agent` 而非 `coder-agent`）。

**解法：** 更新全部 8 個 TEAM.md，統一使用完整 8 人清單，每個 agent 清楚標示「你的身份」。

**team.yaml 8 agents 設計：**

```yaml
# admin + pm：常駐（persistent: true，繼承 defaults）
# 6 workers：動態（persistent: false，需求觸發啟動）
instances:
  admin-agent: {role: admin}     # 常駐
  pm-agent:    {role: leader}    # 常駐
  coder-agent: {role: worker, persistent: false}
  qa-agent:    {role: worker, persistent: false}
  ai-dev-agent:{role: worker, persistent: false}
  market-agent:{role: worker, persistent: false}
  data-agent:  {role: worker, persistent: false}
  report-agent:{role: worker, persistent: false}
```

**指揮鏈（更新）：**
```
使用者 → admin（預設入口）→ pm-agent（分析+派工）→ worker（執行）→ pm-agent（驗收）→ reply
```

---

## 6. 影響分析

| 系統 | 影響 | 風險 |
|------|------|------|
| src/ 程式碼 | 無 | 無 |
| MCP stdio bridge | 無（mcp.json 只是設定） | 無 |
| smoke_test | 需新增 state/tasks/mc-agent 結構驗證 | 低 |
| team.yaml 舊範本（ops/dev） | 不含 mc-agent，維持 5 agents 模式 | 無 |
| TEAM.md 自動產生 | 需包含 mc-agent | 低 |

## 7. 故障降級

- mc-agent 無法啟動 → admin-agent 可臨時作為入口（退化模式）
- skills.json 不存在 → agent 正常運作，skills 靠目錄清單（原有行為）
- state/ 不存在 → 不影響功能，只是無持久化（原有行為）

## 8. 替代方案（未選）

| 方案 | 缺點 |
|------|------|
| admin-agent 加路由但不分離 | 職責仍混亂，context 無改善 |
| 只改 steering 不加 mc-agent | 路由邏輯還是在 admin，治標不治本 |
| 完整實作 state 讀寫 | 超出範本教學範疇，複雜度高 |
