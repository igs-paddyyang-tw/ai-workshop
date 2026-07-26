---
title: "ai-team-agent 借鑑 minecraft 優化執行計畫"
status: completed
created: 2026-07-27
completed: 2026-07-27
type: plan
language: zh-TW
related_spec: docs/specs/minecraft-alignment-spec.md
related_design: docs/designs/minecraft-alignment-design.md
---

# ai-team-agent 借鑑 minecraft 優化執行計畫

## 1. 里程碑總覽

| M# | 名稱 | 預估 | 依賴 |
|----|------|------|------|
| M1 | state/tasks 持久化目錄 | 30min | — |
| M2 | skills.json + skill-mapping.yaml | 45min | — |
| M3 | Steering 精簡（8→4 檔） | 1.5h | — |
| M4 | mc-agent 分離入口 | 3h | M2, M3 |
| M5 | smoke_test 更新 + 驗證 | 30min | M1-M4 |

**總計：~6h**

---

## 2. M1：state/tasks 持久化目錄（30min）

### 任務分解

| # | 任務 | 產出檔案 | 估時 | AC |
|---|------|----------|------|-----|
| 1.1 | 建立 state/ 目錄結構 | `state/heartbeat/.gitkeep`、`state/.gitkeep` | 5min | 目錄存在 |
| 1.2 | 初始化 board.json 骨架 | `state/board.json` | 5min | 格式正確（`{"version":"1.0","tasks":[],"updated_at":null}`） |
| 1.3 | 建立 tasks/items/ 目錄 | `tasks/items/.gitkeep` | 5min | 目錄存在 |
| 1.4 | 更新 smoke_test 加入驗證 | `tests/smoke_test.py` | 15min | state/ + tasks/ 目錄存在測試通過 |

---

## 3. M2：skills.json + skill-mapping.yaml（45min）

### 任務分解

| # | 任務 | 產出檔案 | 估時 | AC |
|---|------|----------|------|-----|
| 2.1 | 建立 config/skill-mapping.yaml | `config/skill-mapping.yaml` | 15min | 含 8 角色 + shared |
| 2.2 | 建立 admin-agent skills.json | `agents/admin-agent/.kiro/settings/skills.json` | 5min | role=admin，含角色技能 + shared |
| 2.3 | 建立 pm-agent skills.json | `agents/pm-agent/.kiro/settings/skills.json` | 5min | role=leader |
| 2.4 | 建立 coder-agent skills.json | `agents/coder-agent/.kiro/settings/skills.json` | 3min | role=worker-coder |
| 2.5 | 建立 qa-agent skills.json | `agents/qa-agent/.kiro/settings/skills.json` | 3min | role=worker-qa |
| 2.6 | 建立 ai-dev-agent skills.json | `agents/ai-dev-agent/.kiro/settings/skills.json` | 3min | role=worker-ai-dev |
| 2.7 | 建立 data-agent skills.json | `agents/data-agent/.kiro/settings/skills.json` | 3min | role=worker-data |
| 2.8 | 建立 market-agent skills.json | `agents/market-agent/.kiro/settings/skills.json` | 3min | role=worker-market |
| 2.9 | 建立 report-agent skills.json | `agents/report-agent/.kiro/settings/skills.json` | 3min | role=worker-report |

---

## 4. M3：Steering 精簡（1.5h）

### 任務分解

| # | 任務 | 產出檔案 | 估時 | AC |
|---|------|----------|------|-----|
| 3.1 | 根 .kiro/steering/BRAIN.md 加入 MCP 工具段 | `.kiro/steering/BRAIN.md` | 15min | 含工具表格 |
| 3.2 | 刪除根 AGENTS.md | `.kiro/steering/AGENTS.md` | 2min | 檔案不存在 |
| 3.3 | 根 .kiro/steering/SOUL.md 加入使用者資訊 | `.kiro/steering/SOUL.md` | 5min | 含使用者偏好段 |
| 3.4 | 刪除根 USER.md | `.kiro/steering/USER.md` | 2min | 檔案不存在 |
| 3.5 | 每 agent BRAIN.md 加入工具表格（8 agent） | `agents/*/. kiro/steering/BRAIN.md` | 30min | 每個 BRAIN 有工具段 |
| 3.6 | 每 agent SOUL.md 加入使用者資訊（8 agent） | `agents/*/.kiro/steering/SOUL.md` | 20min | 每個 SOUL 有使用者資訊段 |
| 3.7 | 刪除各 agent 多餘 steering 檔 | `agents/*/.kiro/steering/AGENTS.md` 等 | 5min | 每 agent ≤ 4 常駐檔 |

---

## 5. M4：TEAM.md 全員統一 + team.yaml 8 agents（30min）✅ 已完成

### 任務分解

| # | 任務 | 產出檔案 | 狀態 | AC |
|---|------|----------|------|-----|
| 4.1 | 更新 8 個 agent TEAM.md（完整 8 人清單） | `agents/*/.kiro/steering/TEAM.md` | ✅ | 含完整 8 人表格 |
| 4.2 | 修正 instance 名稱（dev-agent → coder-agent） | — | ✅ | 名稱正確 |
| 4.3 | team.yaml 改為 8 agents（workers persistent: false） | `team.yaml` | ✅ | 8 agents 完整 |
| 4.4 | team-ops.yaml / team-dev.yaml 格式對齊 | `team-ops.yaml`, `team-dev.yaml` | ✅ | 格式一致 |

---

## 6. M5：smoke_test 更新 + 驗證（30min）

### 任務分解

| # | 任務 | 產出檔案 | 估時 | AC |
|---|------|----------|------|-----|
| 5.1 | 新增 state/tasks 驗證 | `tests/smoke_test.py` | 10min | test_state_dirs_exist pass |
| 5.2 | 新增 skills.json 驗證 | `tests/smoke_test.py` | 10min | test_skills_json_exists pass |
| 5.3 | 新增 mc-agent 結構驗證 | `tests/smoke_test.py` | 5min | test_mc_agent_steering pass |
| 5.4 | 全跑 smoke_test | — | 5min | 全 pass |

---

## 7. 執行順序

```
M1 + M2（並行，無依賴）
     ↓
M3（Steering 精簡，獨立）
     ↓
M4（mc-agent，依賴 M2 skills.json + M3 steering 模板）
     ↓
M5（驗證，依賴全部）
```

## 8. 風險與緩解

| 風險 | 機率 | 影響 | 緩解 |
|------|------|------|------|
| mc-agent 加入後使用者需更新 kiro-cli workspace | 中 | 低 | README 新增 mc-agent 說明段落 |
| 刪除 AGENTS.md 後某 agent 找不到工具說明 | 低 | 中 | 確認 BRAIN 已包含工具表格再刪除 |
| team.yaml 舊範本（ops/dev）不含 mc-agent | 低 | 低 | 舊範本維持不動，說明「精簡模式」 |
| Steering 合併後 context 格式混亂 | 低 | 中 | 每次合併後人工 review SOUL/BRAIN |

## 9. 回滾計畫

- M1-M3：git revert（純新增/修改，可安全回退）
- M4 mc-agent：git revert team.yaml + 刪除 agents/mc-agent/（風險最高但可恢復）
- 合併 steering 前：先 git commit 做 checkpoint

## 10. 完成標準

- [x] state/board.json 存在且格式正確 ✅
- [x] tasks/items/ 存在 ✅
- [x] 8 agent 都有 skills.json ✅
- [x] config/skill-mapping.yaml 存在 ✅
- [x] 每 agent 常駐 steering ≤ 5 檔（KIRO fileMatch）✅
- [x] team.yaml 預設 8 agents（admin+pm 常駐，6 workers 動態）✅
- [x] 8 個 TEAM.md 完整 8 人清單 ✅
- [x] smoke_test 全 pass ✅
- [x] git commit + push ✅
