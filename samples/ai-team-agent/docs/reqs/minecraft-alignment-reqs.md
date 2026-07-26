# 需求文件：ai-team-agent 借鑑 minecraft-team-agent 優化

> 參考來源：`projects/minecraft-team-agent`（生產版，v3.1.0，152 tests pass）
> 目標路徑：`projects/ai-workshop/samples/ai-team-agent`（教學範本）

---

## 背景

minecraft-team-agent 是 ai-team-agent 的生產化升級版，兩者架構相同但前者有四項明顯優化，分析後決定借鑑：

1. **mc-agent 分離入口** — 獨立路由層，分離「管」與「做」
2. **Steering 精簡（8 檔 → 4 檔）** — 合併冗餘，節省 ~40% context
3. **per-agent skills.json** — 技能宣告明確化 + skill-mapping.yaml
4. **state/tasks 持久化目錄** — 服務重啟後可恢復任務狀態

---

## 借鑑項目說明

### REQ-1：state/tasks 持久化目錄

**問題：** 任務狀態只在記憶體（TaskLifecycle），服務重啟後任務看板消失。

**參考：** minecraft `state/` + `tasks/` 目錄結構：
```
state/
├── events.jsonl        ← EventBus 事件流（append-only）
├── messages.jsonl      ← 訊息歷史
├── heartbeat/          ← agent 心跳
├── platform.pid        ← 進程 PID
├── startup.log
└── board.json          ← 任務看板（主要）
tasks/
└── items/              ← 每個任務一個 JSON
```

**解法：** 建立對應目錄結構，start.py 自檢加入 state/ 驗證。

**驗收：** state/ + tasks/items/ 存在，board.json 格式正確。

---

### REQ-2：per-agent skills.json + skill-mapping.yaml

**問題：** agent 的技能靠 `.kiro/skills/` 目錄清單暗示，沒有明確的 JSON 宣告，無法程式化讀取。

**參考：** minecraft 每個 agent 的 `.kiro/settings/skills.json`：
```json
{
  "role": "admin",
  "skills": ["ark-env-doctor", "ark-docker-deploy", "ark-dashboard-health", "ark-security-audit"]
}
```

搭配 `config/skill-mapping.yaml`（角色→技能映射表，作為 skills.json 的產生依據）。

**解法：**
- 新增 `config/skill-mapping.yaml`（角色→技能映射）
- 每個 agent 新增 `.kiro/settings/skills.json`（依其角色從 mapping 生成）

**驗收：** 8 agent 都有 skills.json，`config/skill-mapping.yaml` 存在且格式正確。

---

### REQ-3：Steering 精簡（8 檔 → 4 檔）

**問題：** 每個 agent 有 8 個 steering 檔（SOUL/BRAIN/MEMORY/TEAM/AGENTS/GUARDRAILS/KIRO/USER），載入 context 約 4000+ 字，存在冗餘。

**參考：** minecraft 4 檔制（SOUL/BRAIN/TEAM/MEMORY），合併策略：

| 被合併檔案 | 合併目標 | 方式 |
|-----------|---------|------|
| AGENTS.md | BRAIN.md | MCP 工具表格移入 BRAIN 第一節 |
| KIRO.md | BRAIN.md | Python 程式碼規範移入 BRAIN 最後一節（或保留 fileMatch） |
| GUARDRAILS.md | BRAIN.md | 品質護欄已在 BRAIN，若有獨立檔案則合併 |
| USER.md | SOUL.md | 使用者資訊移入 SOUL 最後段 |

**注意：** KIRO.md 有 `inclusion: fileMatch`，可保留獨立（不佔常駐 context）。

**驗收：** 每個 agent steering 常駐載入 ≤ 4 檔（KIRO.md 可作 fileMatch 例外）。

---

### REQ-4：~~mc-agent 分離入口~~ — 已移除

**決策（2026-07-27 修正）：** mc-agent 是 minecraft-team-agent 的業務特化設計（遊戲開發平台需要專責路由層），**不適合移植**到 ai-team-agent 教學範本。

原因：
- ai-team-agent 用途是「遊戲開發平台」教學，admin-agent 作為預設入口已符合課程場景
- 第四堂課學員手動新增的 agent 是 designer-agent，不是 mc-agent
- 增加 mc-agent 對學員來說是不必要的認知負擔

---

### REQ-4（替代）：TEAM.md 全員統一 + team.yaml 預設 8 agents

**問題：** 各 agent 的 TEAM.md 只列 4-5 人，且 instance 名稱錯誤（`dev-agent` 應為 `coder-agent`），指揮鏈不一致。

**解法：**
- 更新所有 8 個 agent 的 TEAM.md，統一列出完整 8 人清單
- 每個 agent TEAM.md 有「你的身份」清楚標示
- team.yaml 改為預設完整 8 agents（workers 設 `persistent: false`）

**驗收：** 8 個 TEAM.md 全部包含 8 人清單，agent instance 名稱正確。

---

## 優先級與依賴

| # | 項目 | 優先級 | 依賴 | 預估時間 |
|---|------|--------|------|---------|
| REQ-1 | state/tasks 持久化 | P0 | 無 | 30min |
| REQ-2 | skills.json + skill-mapping | P0 | 無 | 45min |
| REQ-3 | Steering 精簡 8→5 | P1 | 無 | 1.5h |
| REQ-4 | TEAM.md 全員統一 + team.yaml 8 agents | P0 | 無 | 30min |

## 約束

- 不改變 MCP stdio 通訊機制（mcp_stdio.py 不動）
- 不改變 src/ 程式碼架構
- smoke_test 全程通過
- 相容現有 kiro-cli 常駐進程架構
- 作為教學範本，保持可讀性 > 最佳化

## 參考

- minecraft-team-agent：`/Users/paddy/ai-agent/projects/minecraft-team-agent/`
- ai-team-agent：`/Users/paddy/ai-agent/projects/ai-workshop/samples/ai-team-agent/`
- 對齊方向：minecraft（生產版）→ ai-team-agent（借鑑）
