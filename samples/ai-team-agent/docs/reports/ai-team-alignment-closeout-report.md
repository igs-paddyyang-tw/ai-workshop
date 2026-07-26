---
title: "ai-team-agent 對齊優化結案報告"
type: report
created: 2026-07-27
completed: 2026-07-29
scope: ai-team-agent
tags: [closeout, alignment, quality, drift]
---

# ai-team-agent 對齊優化結案報告

> **期間：** 2026-07-27 ～ 2026-07-29
> **目標：** 借鑑 minecraft-team-agent 生產版優化，提升 ai-team-agent 品質，並通過 Spec Drift 驗證

---

## 執行摘要

本次共完成 5 個里程碑、3 輪 Drift 驗證，Drift Score 從 **62 → 97/100**，smoke_test 從 **12 → 17 passed**，ai-workshop 共推送 **14 commits**。

---

## Drift Score 進展

| 輪次 | API 端點 | Schema | 依賴規則 | 測試覆蓋 | 總分 |
|------|---------|--------|---------|---------|------|
| Round 1（基線） | 75 | 72 | 40 | 63 | 62 |
| Round 2（修復後） | 90 | 88 | 80 | 84 | 85.5 |
| Round 3（最終） | 100 | 100 | 100 | 95 | **~97** ✅ |

---

## 完成里程碑

### M1 — state/tasks 持久化目錄

- `state/` + `state/heartbeat/` + `state/board.json` 初始化
- `tasks/items/` 目錄建立
- smoke_test: `test_state_and_tasks_dirs` 驗證

### M2 — skills.json + skill-mapping.yaml

- `config/skill-mapping.yaml`：8 角色 + shared 技能映射
- 8 個 agent 各有 `.kiro/settings/skills.json`
- smoke_test: `test_skills_json_exists` + `test_skill_mapping_yaml_exists`

### M3 — Steering 精簡（8 檔 → 5 檔）

- 合併：AGENTS.md → BRAIN、USER.md → SOUL、GUARDRAILS.md → BRAIN
- 保留：KIRO.md（fileMatch，不佔常駐 context）
- 新增：根 + 8 agent 各有 BRAIN.md（品質護欄 + MCP 工具段）
- smoke_test: `test_steering_4_files` + `test_brain_inclusion_always` + `test_kiro_fileMatch`

### M4 — TEAM.md 全員統一 + team.yaml 8 agents

- 8 個 agent TEAM.md 統一列出完整 8 人清單，修正錯誤 instance 名稱
- team.yaml 升級為預設 8 agents（admin+pm 常駐，6 workers 動態）
- team-ops.yaml / team-dev.yaml 格式對齊
- smoke_test: `test_team_yaml_8_agents` + `test_team_yaml_variants` + `test_team_md_8_members`

### M5 — 業務 Wiki + Drift 修復

**B 級 agent wiki 補充（6 頁）：**

| Agent | 新增 wiki | 內容 |
|-------|---------|------|
| data-agent | game-kpi-metrics | DAU/MAU/ARPU/留存率/RTP 等遊戲指標 |
| data-agent | game-data-analysis-workflow | 分析流程 + Cohort/漏斗/趨勢方法 |
| market-agent | game-competitor-analysis | 競品分析框架 + 主要競品清單 |
| market-agent | game-news-monitoring | 新聞監控 SOP + 輿情評分規則 |
| report-agent | game-report-templates | 日報/週報/競品報告模板規範 |
| report-agent | game-daily-news-report | 遊戲競品日報（非科技日報）產出流程 |

**Drift 修復（3 輪）：**

| 問題 | 修復方式 |
|------|---------|
| `router.py` 直接 import `coordinator.services.*` | 移除，改由 bootstrap 外部注入 |
| `memory_commands.py` 直接 import `runtime.tier` | 改從 `bot_data["tier_status"]` 讀取（bootstrap 注入）|
| `GET /api/agents/{id}/health` 缺口 | 新增 endpoint + `AgentHealthResponse` model |
| `AgentResponse` 缺 mode/uptime/memory 欄位 | 補齊 4 個 runtime 欄位 |
| `PATCH /{id}/persistent` 缺口 | 新增 endpoint + `PersistentToggleRequest` model |
| `POST /{id}/rotate` 缺口 | 新增 endpoint |
| design §6 SessionPoolState/PreWarmPool 規格漂移 | 標記為未採用，折疊保留脈絡 |
| FR-2/FR-4 AC 無測試 | 新增 5 個 smoke_test |

---

## 最終狀態

| 面向 | 狀態 |
|------|------|
| smoke_test | ✅ 17 passed（TestTier0Structure） |
| team.yaml | ✅ 8 agents，admin+pm 常駐，6 workers 動態 |
| Steering（每 agent） | ✅ 5 檔（SOUL/BRAIN/MEMORY/TEAM/KIRO） |
| TEAM.md | ✅ 完整 8 人清單，指揮鏈正確 |
| skills.json | ✅ 8/8 agent |
| skill-mapping.yaml | ✅ 8 角色 + shared |
| state/ + tasks/ | ✅ |
| memory/daily/ | ✅ 8/8 |
| output/ 四區 | ✅ 根 + 8 agent |
| hooks | ✅ check-new-imports |
| wiki（A 級 5 agents） | ✅ 5-7 頁/agent |
| wiki（B 級 3 agents） | ✅ 4 頁/agent（遊戲業務場景） |
| API 端點 | ✅ 100/100（無缺口）|
| Schema | ✅ 100/100（25/25 模型）|
| 依賴規則 | ✅ 100/100（0 違規）|
| 測試覆蓋 | ✅ 95/100（18/19 AC）|

---

## git commits（本次共 14 commits）

```
9dffbe1 docs: mark §6 Session Pool as deprecated
2076710 fix: PersistentToggleRequest model
be411bb fix: resolve remaining drift (17 tests)
4930549 fix: spec drift round 1 (3 dep violations + API + schema)
625a2b8 feat: complete alignment (wiki/smoke/docs)
37996c0 fix: align team-ops/dev yaml
8c6e4c9 feat: 8-agent team + steering/skills/state
f74e0b7 docs: add alignment reqs/spec/design/plan
8c72fd4 docs: update README
08c5953 test: add BRAIN/steering structure tests
809448e feat: driving engineering alignment
df94284 fix: ai-team-agent requirements pin
...
```

---

## 殘餘 Backlog（不影響 Ship）

| 項目 | 說明 |
|------|------|
| FR-1.3 start.py 自檢 state/tasks | 整合測試，無影響 |
| persistent-process FR-3/4/5 整合測試 | 生產細節，教學範本不需要 |
| costs API 路徑重疊 | `/api/costs/today` vs `/api/admin/costs`，功能重複但不影響使用 |

---

*結案人：Kiro Agent / 2026-07-29*
