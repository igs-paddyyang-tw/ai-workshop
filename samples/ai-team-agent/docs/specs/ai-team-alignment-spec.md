---
title: "ai-team-agent 借鑑 minecraft 優化規格"
status: draft
created: 2026-07-27
type: spec
language: zh-TW
related_req: docs/reqs/ai-team-alignment-reqs.md
---

# ai-team-agent 借鑑 minecraft 優化規格

## 1. 摘要

將 minecraft-team-agent（生產版 v3.1.0）的四項架構優化移植到 ai-team-agent 教學範本，使範本更貼近生產實踐，同時保持課程可讀性。

## 2. 問題陳述

| 問題 | 影響 |
|------|------|
| 任務狀態只在記憶體 | 服務重啟後任務看板消失 |
| 技能靠目錄暗示，無明確宣告 | 無法程式化讀取 agent 能力 |
| 每 agent 8 個 steering 檔 | ~4000 字 context，存在冗餘 |
| admin-agent 職責混亂 | 路由+維運兩個大職責，context 混淆 |

## 3. 目標

- state/tasks 持久化目錄存在（可擴充實作）
- 每 agent 有明確的 skills.json + 根目錄有 skill-mapping.yaml
- 每 agent steering 常駐載入 ≤ 4 檔
- mc-agent 作為獨立路由入口

## 4. 非目標

- 不改 src/ 程式碼（只改設定/目錄/steering）
- 不實作 state 的讀寫邏輯（僅建立目錄結構）
- 不改變 MCP stdio 通訊機制
- 不破壞現有 smoke_test 通過率

## 5. 功能需求

### FR-1：state/tasks 目錄

| ID | 需求 | 優先級 |
|----|------|--------|
| FR-1.1 | 建立 `state/` 目錄含子結構（heartbeat/、board.json 初始化） | P0 |
| FR-1.2 | 建立 `tasks/items/` 目錄 | P0 |
| FR-1.3 | start.py 自檢加入 state/ + tasks/ 驗證（不存在自動建立） | P1 |

### FR-2：skills.json + skill-mapping.yaml

| ID | 需求 | 優先級 |
|----|------|--------|
| FR-2.1 | 新增 `config/skill-mapping.yaml`（8 角色的技能映射） | P0 |
| FR-2.2 | 每個 agent 新增 `.kiro/settings/skills.json`（依角色從 mapping 生成） | P0 |
| FR-2.3 | skills.json 格式：`{"role": "...", "skills": [...]}` | P0 |

### FR-3：Steering 精簡

| ID | 需求 | 優先級 |
|----|------|--------|
| FR-3.1 | AGENTS.md 內容合併進各 agent BRAIN.md（MCP 工具表格） | P1 |
| FR-3.2 | USER.md 內容合併進各 agent SOUL.md（使用者資訊段） | P1 |
| FR-3.3 | GUARDRAILS.md（若存在）合併進 BRAIN.md | P1 |
| FR-3.4 | KIRO.md 保留獨立（fileMatch，不佔常駐 context） | P1 |
| FR-3.5 | 根 .kiro/steering/ 同步精簡（移除 AGENTS.md、USER.md） | P1 |
| FR-3.6 | 每 agent 常駐 steering 檔案數 ≤ 4（SOUL/BRAIN/MEMORY/TEAM） | P1 |

### FR-4：TEAM.md 全員統一 + team.yaml 預設 8 agents

| ID | 需求 | 優先級 |
|----|------|--------|
| FR-4.1 | 更新所有 8 個 agent 的 TEAM.md，統一列出完整 8 人清單 | P0 |
| FR-4.2 | 修正 TEAM.md 中錯誤的 instance 名稱（`dev-agent` → `coder-agent`） | P0 |
| FR-4.3 | 每個 agent TEAM.md 包含「你的身份」明確標示 | P0 |
| FR-4.4 | team.yaml 改為預設完整 8 agents（workers 設 `persistent: false`） | P0 |
| FR-4.5 | team-ops.yaml / team-dev.yaml 格式對齊新版 team.yaml | P1 |

## 6. 非功能需求

| NFR | 指標 |
|-----|------|
| 教學可讀性 | steering 檔案每節有清楚的中文標題 |
| smoke_test | 全程通過（含新增 mc-agent 結構驗證） |
| 啟動時間 | 新增自檢不超過 200ms |
| 相容性 | 舊的 2 team.yaml 範本（ops/dev）可繼續使用 |

## 7. 成功指標

| 指標 | 目標 |
|------|------|
| state/ + tasks/ 目錄 | 存在 |
| skills.json 覆蓋率 | 8/8 agent |
| skill-mapping.yaml | 存在且包含 8 角色 |
| 每 agent 常駐 steering | ≤ 5 檔（KIRO 保留 fileMatch） |
| team.yaml 預設 8 agents | ✅ admin+pm 常駐，6 workers 動態 |
| 每 agent TEAM.md 完整 8 人清單 | ✅ |
| smoke_test | 全 pass |

## 8. 開放問題

| # | 問題 | 決策 |
|---|------|------|
| Q1 | KIRO.md 保留獨立還是合併 BRAIN？ | 保留獨立（fileMatch 不佔常駐 context，有助教學分離關注點） |
| Q2 | mc-agent 加入後 team.yaml 預設配置是 9 agents 還是可選配？ | 預設 9 agents，舊 ops/dev yaml 繼續保持 5 agents 供簡化教學 |
| Q3 | admin-agent 改名為 ad-agent（對齊 minecraft）？ | 不改，保持教學一致性 |
| Q4 | state/ 目錄要實作讀寫邏輯嗎？ | 本期只建目錄結構，讀寫邏輯列 backlog |
