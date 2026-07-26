---
title: "Spec vs Code Drift Report"
type: report
created: 2026-07-28
scope: ai-team-agent
tags: [drift, spec, quality]
---

# Spec vs Code Drift Report — ai-team-agent

> 分析時間：2026-07-28
> 目標專案：`samples/ai-team-agent/`
> 分析維度：API 端點 / Schema / 依賴規則 / 測試覆蓋

---

## 總覽

| 維度 | 得分 | 狀態 |
|------|------|------|
| API 端點 | 75 / 100 | ⚠️ 5 個文件端點未實作 |
| Schema | 72 / 100 | ⚠️ 部分模型未在 Spec 中記載 |
| 依賴規則 | 40 / 100 | ❌ 3 個跨層違規 |
| 測試覆蓋 | 63 / 100 | ⚠️ 5 個 AC 無對應測試 |
| **加權總分** | **62 / 100** | ⚠️ 需修復 |

---

## 維度 1：API 端點（75 / 100）

### 評分公式
`100 - (doc_有_code_無 × 5) = 100 - (5 × 5) = 75`

### Code 已實作的 Endpoints

**src/gateway/api/admin.py**
- `GET /dashboard/stats`
- `GET /dashboard/trends`
- `GET /dashboard/live`
- `GET /dashboard/timeline`
- `GET /sessions`
- `GET /sessions/{session_id}`
- `GET /sessions/{agent_id}` ← 路徑衝突（同 session_id）
- `GET /sessions/{agent_id}/{session_id}`
- `POST /sessions/{session_id}/intervene`
- `POST /sessions/{agent_id}/{session_id}/intervene`
- `POST /sessions/{session_id}/abort`
- `POST /sessions/{session_id}/restart`
- `GET /sessions/{session_id}/turns`
- `GET /costs`
- `GET /costs/budget`
- `GET /costs/export`
- `GET /costs/summary`
- `POST /costs/budget`
- `GET /audit`
- `GET /queue`
- `PATCH /queue/{issue_id}/priority`
- `POST /queue/batch`
- `GET /system/health`

**src/gateway/api/agents.py**
- `GET /api/agents`
- `POST /api/agents`
- `GET /api/agents/{agent_id}`
- `PATCH /api/agents/{agent_id}`
- `DELETE /api/agents/{agent_id}`
- `GET /api/agents/sessions`
- `POST /api/agents/spawn`
- `GET /api/agents/runtime/status`

**src/gateway/api/issues.py**
- `GET /api/issues`
- `POST /api/issues`
- `GET /api/issues/{issue_id}`
- `PATCH /api/issues/{issue_id}/assign`
- `PATCH /api/issues/{issue_id}/complete`
- `DELETE /api/issues/{issue_id}`

**src/gateway/api/board.py**
- `GET /api/board`
- `POST /api/tasks`
- `PATCH /api/tasks/{task_id}/unblock`
- `PATCH /api/tasks/{task_id}/retry`
- `GET /api/runtimes`

**src/gateway/api/chat.py**
- `POST /api/chat/reply`
- `POST /api/chat/notify`
- `GET /api/chat/traces`
- `POST /api/chat/send`

**src/gateway/api/costs.py**
- `GET /api/costs/today`
- `GET /api/costs/weekly`

**src/gateway/api/memory.py** (prefix: /api/v1/memory)
- `POST /api/v1/memory/recall`
- `GET /api/v1/memory/daily/{agent}`
- `POST /api/v1/memory/consolidate`

**src/gateway/api/wiki.py** (prefix: /api/v1/wiki)
- `GET /api/v1/wiki/search`
- `GET /api/v1/wiki/pages`
- `POST /api/v1/wiki/ingest`
- `GET /api/v1/wiki/graph-data`

**src/gateway/api/skills.py** (prefix: /api/v1/skills)
- `GET /api/v1/skills`
- `POST /api/v1/skills/invoke`
- `GET /api/v1/skills/stats`
- `GET /api/v1/skills/pending`
- `POST /api/v1/skills/approve`
- `POST /api/v1/skills/reject`

**src/gateway/api/schedules.py**
- `GET /api/schedules`
- `POST /api/schedules/{job_id}/pause`
- `POST /api/schedules/{job_id}/resume`
- `POST /api/schedules/{job_id}/trigger`

**src/gateway/api/ws.py**
- `WS /api/ws/events`

**router.py (直接掛載)**
- `GET /api/health`
- `GET /board`

### Doc 記載的 Endpoints（設計文件 + Spec 中提及）

**persistent-process-design.md 明確定義：**
- `GET /api/agents/{id}/health` — 查詢單一 agent 健康狀態
- `GET /api/agents` — 已實作（含 mode/uptime/memory_mb 欄位）

**ai-team-alignment-design.md 提及但非正式規格：**
- 未明確列出 endpoint 路徑

### 🔴 Doc 有 / Code 無（5個）

| Endpoint | 定義位置 | 說明 |
|----------|----------|------|
| `GET /api/agents/{id}/health` | persistent-process-design §11 | per-agent 健康詳情（pid/uptime/memory_mb/consecutive_failures） |
| `GET /api/agents/{agent_id}` 含 mode/uptime 欄位 | persistent-process-design §9 | 回應 schema 不完整，缺 mode、uptime_seconds、memory_mb |
| `PATCH /api/agents/{agent_id}/persistent` | persistent-process-design §5 FR-5 | 切換 persistent 模式（未實作） |
| `POST /api/agents/{agent_id}/rotate` | persistent-process-design §7 | session rotate（未實作） |
| `GET /api/agents/{agent_id}/session` | persistent-process-design §6 Session Rotate | 目前 session 資訊無法查詢 |

### 🟡 Code 有 / Doc 無（主要）

| Endpoint | 說明 |
|----------|------|
| `POST /api/chat/send` | Chat send（A2A），文件未記載 |
| `GET /api/v1/wiki/graph-data` | 知識圖譜 API，僅在 Web UI 頁面描述 |
| `GET /api/costs/today` / `weekly` | costs.py 獨立路由，admin.py 也有 /costs，結構重疊 |
| `POST /api/queue/batch` | batch action，文件未列 |

---

## 維度 2：Schema（72 / 100）

### 評分公式
`有比對到 / 總模型 × 100 = 18/25 × 100 ≈ 72`

### Code 中所有模型（BaseModel + dataclass）

**Gateway/API 層（BaseModel）：**

| 模型 | 位置 |
|------|------|
| `AgentCreate` | agents.py |
| `AgentUpdate` | agents.py |
| `IssueCreate` | issues.py |
| `IssueAssign` | issues.py |
| `IssueStatusUpdate` | issues.py |
| `CreateTaskBody` | board.py |
| `TransitionBody` | board.py |
| `ReplyPayload` | chat.py |
| `NotifyPayload` | chat.py |
| `SendPayload` | chat.py |
| `RecallRequest` | memory.py |
| `ConsolidateRequest` | memory.py |
| `IngestRequest` | wiki.py |
| `InvokeRequest` | skills.py |
| `ApproveRequest` | skills.py |

**Coordinator/Runtime 層（dataclass）：**

| 模型 | 位置 |
|------|------|
| `RecallResult` | coordinator/memory/recall.py |
| `TaskHandoff` | coordinator/a2a/protocol.py |
| `ProgressEvent` | coordinator/a2a/protocol.py |
| `Event` | coordinator/events/types.py |
| `InstanceState` | runtime/registry.py |
| `InstanceConfig` | runtime/config.py |
| `TierStatus` | runtime/tier.py |
| `ManagedProcess` | runtime/managed_process.py |
| `KiroBackend` | runtime/kiro_backend.py |
| `FailureRecord` | runtime/failure_memory.py |

**business/skills 層（dataclass/BaseModel）：**

| 模型 | 位置 |
|------|------|
| `SkillResult` | business/skills/base.py |
| `Task` | spec_executor/parser.py |
| `PlanSpec` | spec_executor/parser.py |
| `ACResult` | spec_executor/verifier.py |
| `TaskResult` | spec_executor/executor.py |
| `ExecutionContext` | spec_executor/executor.py |
| `Progress` | spec_executor/checkpoint.py |

**總計：25 個模型**

### Doc 中有記載的 Schema（設計文件）

**ai-team-alignment-spec.md / design.md：**
- `AgentCreate`、`AgentUpdate` ← ✅ 有實作（FR-4 agents CRUD 隱含）
- `IssueCreate`、`IssueAssign` ← ✅ 有實作（issues 管理）
- `board.json` schema（`{version, tasks, updated_at}`）← ✅ state/board.json

**persistent-process-spec.md / design.md：**
- `InstanceConfig`（persistent/idle_timeout/max_memory）← ✅ runtime/config.py
- `ManagedProcess`（name/proc/output_lines）← ✅ runtime/managed_process.py
- `TierStatus` ← ✅ runtime/tier.py
- `AgentCreate` 含 mode/uptime 欄位 ← ⚠️ 部分缺失

### 🔴 Doc 有 / Code 無（7個缺漏模型欄位/模型）

| 模型/欄位 | 定義位置 | 說明 |
|-----------|----------|------|
| `AgentResponse.mode` | persistent-process-design §9 | GET /api/agents 回應缺 mode 欄位 |
| `AgentResponse.uptime_seconds` | persistent-process-design §9 | 缺 uptime_seconds |
| `AgentResponse.memory_mb` | persistent-process-design §9 | 缺 memory_mb |
| `AgentResponse.tasks_completed` | persistent-process-design §9 | 缺 tasks_completed |
| `AgentHealthResponse` | persistent-process-design §11 | 整個 health 回應 schema 未實作 |
| `SessionPoolState` | persistent-process-design §6 | Session Pool 狀態模型不存在 |
| `PreWarmPool` | persistent-process-design §6 | Pre-warm 機制未實作 |

---

## 維度 3：依賴規則（40 / 100）

### 評分公式
`100 - (違規數 × 20) = 100 - (3 × 20) = 40`

### 架構層次定義（來自設計文件）

```
coordinator/   ← 核心業務邏輯（memory/wiki/a2a/events/db）
runtime/       ← 基礎設施（process/daemon/tier/registry）
gateway/       ← 入口層（api/telegram）
business/      ← 業務 Skills
```

**設計原則：**
- `gateway` 應僅依賴 `coordinator` 的抽象介面（EventBus、DB Models）
- `gateway` 不應直接依賴 `runtime` 細節模組（tier 偵測是基礎設施關注點）
- `coordinator` 不應依賴 `gateway`（單向依賴）

### 🔴 違規 Import（3個）

| 違規 | 位置 | 說明 | 嚴重度 |
|------|------|------|--------|
| `from runtime.tier import detect_tier` | `gateway/telegram/handlers/memory_commands.py:150` | gateway 直接呼叫 runtime 的 Tier 偵測邏輯，應透過 API 或 service 層抽象 | 中 |
| `from coordinator.services.cost_tracker import on_agent_output` | `gateway/api/router.py:24` | router（gateway 入口）直接訂閱 coordinator service 的具體事件處理函式，緊耦合 | 中 |
| `from coordinator.services.audit_logger import on_any_event` | `gateway/api/router.py:25` | 同上，audit_logger 屬 coordinator service 細節 | 中 |

### ✅ 合規的跨層依賴

- `gateway/api/*.py → coordinator.db.models`：可接受（DB 是共用基礎設施）
- `gateway/api/*.py → coordinator.events.types`：可接受（Event/EventType 是公共合約）
- `gateway/api/wiki.py → coordinator.wiki.engine`：可接受（engine 是 coordinator 的公開 API）
- `gateway/api/memory.py → coordinator.memory.recall`：可接受（recall 是公開服務函式）

---

## 維度 4：測試覆蓋（63 / 100）

### 評分公式
`有測試的 AC / 總 AC × 100 = 12/19 × 100 ≈ 63`

### 主要 Spec AC 清單（ai-team-alignment-spec.md）

**FR-1：state/tasks 目錄（3 個 AC）**

| AC | 描述 | 測試狀態 |
|----|------|----------|
| FR-1.1 | state/heartbeat/ + board.json 初始化存在 | ✅ smoke_test `test_project_files_exist` 間接驗證 |
| FR-1.2 | tasks/items/ 目錄存在 | ❌ 無直接測試 |
| FR-1.3 | start.py 自檢 state/tasks/ | ❌ 無測試 |

**FR-2：skills.json + skill-mapping.yaml（3 個 AC）**

| AC | 描述 | 測試狀態 |
|----|------|----------|
| FR-2.1 | config/skill-mapping.yaml 存在 | ❌ 無測試 |
| FR-2.2 | 每 agent .kiro/settings/skills.json 存在 | ❌ 無測試 |
| FR-2.3 | skills.json 格式正確 | ❌ 無測試 |

**FR-3：Steering 精簡（6 個 AC）**

| AC | 描述 | 測試狀態 |
|----|------|----------|
| FR-3.1 | AGENTS.md 合併進 BRAIN.md | ✅ `test_steering_4_files` + `test_brain_inclusion_always` |
| FR-3.2 | USER.md 合併進 SOUL.md | ✅ `test_steering_4_files` |
| FR-3.3 | GUARDRAILS.md 合併進 BRAIN.md | ✅ `test_steering_4_files` |
| FR-3.4 | KIRO.md 保留 fileMatch | ❌ 無驗證（smoke_test 未檢查 KIRO.md fileMatch 屬性） |
| FR-3.5 | 根 .kiro/steering/ 移除 AGENTS.md/USER.md | ❌ 無直接測試 |
| FR-3.6 | 每 agent 常駐 steering ≤ 4 檔 | ✅ `test_steering_4_files`（驗證剛好 4 檔） |

**FR-4：TEAM.md + team.yaml（5 個 AC）**

| AC | 描述 | 測試狀態 |
|----|------|----------|
| FR-4.1 | 8 agent TEAM.md 有完整 8 人清單 | ❌ 無測試 |
| FR-4.2 | TEAM.md 修正 dev-agent → coder-agent | ❌ 無測試 |
| FR-4.3 | 每 agent TEAM.md 有「你的身份」標示 | ❌ 無測試 |
| FR-4.4 | team.yaml 預設 8 agents，workers persistent: false | ✅ `test_team_yaml_8_agents` |
| FR-4.5 | team-ops.yaml / team-dev.yaml 格式對齊 | ✅ `test_team_yaml_variants` |

### ai-team-alignment-spec.md 外的 Spec（非功能需求 / persistent-process-spec）

**persistent-process-spec FR-1~5（8 個 AC）**

| AC | 描述 | 測試狀態 |
|----|------|----------|
| FR-1 常駐進程啟動/停止/重啟 | start_persistent / stop / restart | ✅ smoke_test `test_registry_importable` 部分覆蓋 |
| FR-2 stdin/stdout 通訊 | send_input + timeout | ❌ 無整合測試 |
| FR-3 健康檢查自動重啟 | Daemon health loop | ❌ 無測試 |
| FR-4 Graceful Shutdown | SIGTERM → /exit → kill | ❌ 無測試 |
| FR-5 混合模式（persistent true/false） | ProcessFactory | ❌ 無測試 |

### 測試統計

| 測試檔案 | 測試數 | 覆蓋重點 |
|----------|--------|----------|
| smoke_test.py | 33 | 結構/import/基本功能 |
| test_memory.py | 8 | Memory 子系統 |
| test_skills.py | 9 | Skills 框架 |
| test_wiki.py | 8 | WikiEngine 四層搜尋 |
| test_growth.py | 10 | GrowthDetector |
| **合計** | **68** | — |

---

## 主要問題總結

### 🔴 高優先

1. **API 端點缺漏**：`GET /api/agents/{id}/health` 在 persistent-process-design 有明確定義但未實作，導致監控無法使用
2. **依賴違規 - router.py**：`gateway/api/router.py` 直接 import `coordinator.services.*` 具體函式，耦合過深，應改用 EventBus 訂閱方式解耦
3. **AgentResponse Schema 不完整**：GET /api/agents 回應缺少 mode、uptime_seconds、memory_mb、tasks_completed 欄位

### 🟡 中優先

4. **gateway 直接依賴 runtime.tier**：`memory_commands.py` 呼叫 `runtime.tier.detect_tier`，應封裝為 coordinator service 或透過 config 注入
5. **FR-2 skills.json 無測試**：skill-mapping.yaml 和 per-agent skills.json 的存在與格式無任何驗證測試
6. **FR-4 TEAM.md 內容無測試**：content 驗證（8 人清單、你的身份標示）缺乏測試

### 🟢 低優先

7. **costs API 重疊**：`/api/costs/today` (costs.py) 與 `/api/admin/costs` (admin.py) 功能重疊，建議統一
8. **Code 有 / Doc 無的端點**：`/api/chat/send`、`/api/v1/wiki/graph-data` 未在文件中記載

---

## 建議修復方向

### 短期（1-2 天）

```
1. 實作 GET /api/agents/{id}/health endpoint
   - 回傳 pid / mode / uptime_s / memory_mb / tasks_total / consecutive_failures

2. 修正 gateway/api/router.py 依賴
   - 改為 EventBus 動態訂閱：bus.subscribe(EventType.AGENT_OUTPUT, on_agent_output)
   - 移除 top-level import coordinator.services.*

3. 補齊 AgentResponse schema
   - agents.py GET /{agent_id} 回應加入 mode / uptime_seconds / memory_mb
```

### 中期（3-5 天）

```
4. 解耦 memory_commands.py → runtime.tier
   - 在 bootstrap.py 初始化時將 tier 資訊注入 app.state
   - memory_commands 從 request.app.state 讀取，不直接 import runtime

5. 補充測試
   - test_alignment.py：驗證 FR-2 skills.json + skill-mapping.yaml
   - test_alignment.py：驗證 FR-4 TEAM.md 內容（8 人清單、你的身份）
   - test_persistent_process.py：FR-3 health check / FR-4 graceful shutdown

6. 統一 costs API 結構
   - 保留 /api/v1/costs 作為正式路徑，/api/admin/costs 改為 redirect
```

### 長期（backlog）

```
7. 實作 PreWarmPool + SessionPoolState（persistent-process-spec §6）
8. 補齊 persistent-process-spec FR-2/FR-4/FR-5 整合測試
9. 更新 persistent-process-design.md API 端點章節（新增 /chat/send 等）
```

---

## 評分細節

| 維度 | 計算方式 | 得分 |
|------|----------|------|
| API 端點 | `100 - (5 doc_無 × 5)` | **75** |
| Schema | `18/25 × 100` | **72** |
| 依賴 | `100 - (3 violations × 20)` | **40** |
| 測試覆蓋 | `12/19 AC × 100` | **63** |
| **加權平均** | `(75+72+40+63)/4` | **62.5** |

---

*此報告由 Kiro Drift Analysis 自動產出，供 admin-agent 監控與 coder-agent 修復參考。*
