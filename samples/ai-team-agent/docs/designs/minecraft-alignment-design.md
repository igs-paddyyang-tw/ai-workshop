---
title: "ai-team-agent 借鑑 minecraft 優化設計"
status: draft
created: 2026-07-27
type: design
language: zh-TW
related_spec: docs/specs/minecraft-alignment-spec.md
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

## 5. ADR-4：mc-agent 路由設計

**決策：** 新增 mc-agent 作為獨立路由層（manager），不改 src/ 程式碼。

**架構圖：**

```
使用者 TG 私訊
  │
  ▼
mc-agent（manager）
  ├─ 意圖：維運/系統/部署
  │    └─→ send_to_instance("admin-agent", "使用者訊息：{原文}")
  │              └─→ 執行 → send_to_instance("mc-agent", "[回報] 結果")
  │                              └─→ mc-agent reply 使用者
  │
  └─ 意圖：開發/功能/數據/報告
       └─→ send_to_instance("pm-agent", "使用者訊息：{原文}")
                 └─→ 派工 workers → send_to_instance("mc-agent", "[回報] 結果")
                                         └─→ mc-agent reply 使用者

例外：使用者 @mention worker → worker 直接 reply（不繞路 mc-agent）
```

**mc-agent .kiro/ 結構：**

```
agents/mc-agent/
├── .kiro/
│   ├── steering/
│   │   ├── SOUL.md   ← 路由身份 + 精簡 persona
│   │   ├── BRAIN.md  ← 意圖分流邏輯 + 等待回報規則
│   │   ├── TEAM.md   ← 9 人清單 + 指揮鏈
│   │   └── MEMORY.md ← 空白範本（系統自更新）
│   └── settings/
│       ├── mcp.json  ← --role manager
│       └── skills.json ← manager 角色技能
├── memory/
│   ├── daily/
│   ├── memory.md
│   └── recent.md
├── knowledge/
│   ├── raw/
│   └── wiki/
└── output/
    ├── reports/
    ├── skills/
    ├── exports/
    └── drafts/
```

**team.yaml 新增（manager agent）：**

```yaml
mc-agent:
  working_directory: agents/mc-agent
  description: "👑 Manager — 訊息路由、任務調度、團隊管理"
  role: manager
  persistent: true
  private_chat: 937896656   # 使用者 chat_id
```

**BRAIN.md 意圖分流規則（mc-agent 專屬）：**

```
維運關鍵字：部署、服務、監控、重啟、成本、維運、錯誤、崩潰
→ send_to_instance("admin-agent", "使用者訊息：{原文}")
→ 等待 [回報]，不主動 reply

開發關鍵字：需求、功能、開發、實作、測試、設計、規劃
→ send_to_instance("pm-agent", "使用者訊息：{原文}")
→ 等待 [回報]，不主動 reply

資料/報告關鍵字：市場、數據、分析、報告、圖表
→ send_to_instance("pm-agent", "使用者訊息：{原文}，請調度合適 worker")
→ 等待 [回報]

其他（簡單問答）→ 直接 reply
```

**admin-agent 回報協議（調整）：**

```
來自 mc-agent 的任務 → 執行 → send_to_instance("mc-agent", "[回報] 結果")
來自 @mention → 執行 → 直接 reply
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
