---
title: "AgentProcess 常駐化 — 執行計畫"
type: plan
status: completed
created: 2026-07-14
updated: 2026-07-14
language: zh-TW
related_spec: docs/specs/persistent-process-spec.md
related_design: docs/designs/persistent-process-design.md
---

# AgentProcess 常駐化 — 執行計畫（v2：基於 team-agent 搬遷）

## 1. 摘要

從 `D:\kiro-cli\projects\team-agent` 搬遷已驗證的常駐進程架構到 ai-team-agent，
取代現有 spawn-per-task 模式。PoC 已驗證 `--legacy-ui` 模式全項通過。

分 4 個 Phase 實施，預估總工期 7 天。

---

## 2. 里程碑總覽

```
Phase 1 ─── Phase 2 ─── Phase 3 ─── Phase 4
 核心搬遷     穩定性層     整合測試     文件收尾
 (3 天)       (2 天)       (1.5 天)    (0.5 天)
```

---

## 3. 檔案對應表（來源 → 目標）

| # | team-agent 來源 | ai-team-agent 目標 | 動作 |
|---|----------------|-------------------|------|
| 1 | `src/ark_team_agent/process.py` | `src/runtime/managed_process.py` | 新增（移植 ManagedProcess） |
| 2 | `src/ark_team_agent/backend.py` | `src/runtime/kiro_backend.py` | 新增（移植 build_command + ready/error detection） |
| 3 | `src/ark_team_agent/daemon.py` | `src/runtime/daemon.py` | 重寫（替換現有簡化版） |
| 4 | `src/ark_team_agent/heartbeat.py` | `src/runtime/heartbeat.py` | 新增（直接搬） |
| 5 | `src/ark_team_agent/failure_memory.py` | `src/runtime/failure_memory.py` | 新增（直接搬） |
| 6 | `src/ark_team_agent/message_overflow.py` | `src/runtime/message_overflow.py` | 新增（直接搬） |
| 7 | `src/ark_team_agent/config.py` | `src/runtime/config.py` | 擴充（合併新欄位） |
| 8 | — | `src/runtime/process.py` | 保留（作為 spawn 模式 fallback） |
| 9 | — | `src/bootstrap.py` | 修改（整合新 Daemon） |
| 10 | — | `src/gateway/mcp_stdio.py` | 微調（配合新啟動流程） |
| 11 | — | `team.yaml` | 修改（新增 persistent 設定） |

---

## 4. Phase 1：核心搬遷（3 天）

### 目標

搬遷 ManagedProcess + KiroBackend + Daemon 三大核心，讓 agent 能以常駐模式啟動。

### 任務清單

| # | 任務 | 驗收條件 | 依賴 |
|---|------|----------|------|
| 1.1 | 移植 `ManagedProcess` → `src/runtime/managed_process.py` | 類別可獨立 import，deque ring buffer + send_input + kill 正常 | — |
| 1.2 | 適配 Windows 差異 | `_parse_windows_cmd`、`CREATE_NEW_PROCESS_GROUP`、transport close 皆正確 | 1.1 |
| 1.3 | 移植 `KiroBackend` → `src/runtime/kiro_backend.py` | `build_command()` 產生正確命令；`is_ready()` / `detect_error()` 偵測正確 | — |
| 1.4 | 調整 `build_command` 適配本專案 | 正確找到 kiro-cli 路徑；加入 `--legacy-ui --require-mcp-startup` | 1.3 |
| 1.5 | 重寫 `src/runtime/daemon.py` (Daemon class) | `start_instance` / `stop_instance` / `send_message` / `_wait_for_ready` 可用 | 1.1, 1.3 |
| 1.6 | 實作 `InstanceState` + `InstanceStatus` 狀態機 | STOPPED→STARTING→RUNNING→CRASHED→PAUSED 轉換正確 | 1.5 |
| 1.7 | 實作 `_queue_worker` (per-instance) | 訊息依序送入 stdin，動態 delay | 1.5 |
| 1.8 | 擴充 `src/runtime/config.py` | 新增 `RestartPolicy`、`StartupConfig`、`auto_start`、`startup_timeout_ms` 欄位 | — |
| 1.9 | 修改 `team.yaml` | 加入 `startup.concurrency`、`startup.stagger_delay_ms`、per-instance `skip_resume` | 1.8 |
| 1.10 | 整合測試：啟動 1 agent → send 3 次 → /quit | Ready 偵測通過、3 次 send 皆有 stdout 輸出、graceful stop | 1.1-1.9 |

### 產出檔案

- `src/runtime/managed_process.py`（新增）
- `src/runtime/kiro_backend.py`（新增）
- `src/runtime/daemon.py`（重寫）
- `src/runtime/config.py`（擴充）
- `team.yaml`（修改）

### 回滾方式

刪除新增檔案，還原 `daemon.py` + `config.py` + `team.yaml` 到 git HEAD。
現有 `process.py` (AgentProcess) 完全保留不動。

---

## 5. Phase 2：穩定性層（2 天）

### 目標

加入 health loop、failure memory、message overflow、heartbeat，確保生產級穩定。

### 任務清單

| # | 任務 | 驗收條件 | 依賴 |
|---|------|----------|------|
| 2.1 | 移植 `heartbeat.py` → `src/runtime/heartbeat.py` | heartbeat_loop 每 30s 寫 timestamp；is_heartbeat_stale 判斷正確 | Phase 1 |
| 2.2 | 移植 `failure_memory.py` → `src/runtime/failure_memory.py` | record / clear / consecutive_count / summary 功能正常 | — |
| 2.3 | 移植 `message_overflow.py` → `src/runtime/message_overflow.py` | store / pending / mark_delivered / cleanup 功能正常（SQLite） | — |
| 2.4 | 實作 `_global_health_loop` (30 秒巡檢) | 崩潰偵測 → 自動重啟（指數退避）；超過 max_retries → cooldown | Phase 1 |
| 2.5 | 整合 FailureMemory 到 health loop | 偵測重複 error pattern；rate_limit 3 次 → soft-pause 90s | 2.2, 2.4 |
| 2.6 | 整合 MessageOverflow 到 queue worker | queue ≥ 5 → 持久化；空閒時 replay | 2.3, Phase 1 |
| 2.7 | 記憶體監控（psutil） | RSS > 800MB 警告；列為 optional dependency | 2.4 |
| 2.8 | MCP hash 偵測 | mcp.json 改變 → 強制 skip_resume（新 session 載入新工具） | Phase 1 |
| 2.9 | 整合測試：kill agent 進程 → 觀察自動重啟 | < 10 秒自動重啟；crash_count 正確遞增；連續 3 次後 cooldown | 2.4, 2.5 |

### 產出檔案

- `src/runtime/heartbeat.py`（新增）
- `src/runtime/failure_memory.py`（新增）
- `src/runtime/message_overflow.py`（新增）
- `src/runtime/daemon.py`（擴充 health loop）

### 回滾方式

移除 3 個新增檔案，還原 daemon.py 到 Phase 1 版本。常駐模式仍可運行，只是沒有自動恢復。

---

## 6. Phase 3：整合與 Bootstrap 接線（1.5 天）

### 目標

將新 Daemon 接入 bootstrap.py，取代現有 AgentProcess 建立邏輯；保留 spawn 模式作為 fallback。

### 任務清單

| # | 任務 | 驗收條件 | 依賴 |
|---|------|----------|------|
| 3.1 | 修改 `src/bootstrap.py` Agent 啟動區段 | 使用新 Daemon.start_all()；A2A spawn_fn 改為 Daemon.send_message | Phase 1+2 |
| 3.2 | 保留 AgentProcess 作為 fallback | `team.yaml` 設 `persistent: false` 時走舊 spawn 路徑 | 3.1 |
| 3.3 | 寫入 `.kiro/settings/mcp.json` 自動化 | KiroBackend.write_config 在 start_instance 時執行 | Phase 1 |
| 3.4 | Steering 自動部署 | SOUL.md / TEAM.md / AGENTS.md 由 KiroBackend 管理 | Phase 1 |
| 3.5 | Graceful shutdown 整合 | SIGTERM → Daemon.stop_all() → 所有 agent /quit → 退出 | 3.1 |
| 3.6 | API endpoint 擴充 | `GET /api/agents` 回傳 pid / status / crash_count / last_activity | 3.1 |
| 3.7 | 全團隊啟動測試 | `python -m src.bootstrap` 啟動所有 agent（≥ 3 個），30 分鐘穩定 | 3.1-3.6 |
| 3.8 | Spawn fallback 測試 | 設定 `persistent: false`，確認舊流程不受影響 | 3.2 |

### 產出檔案

- `src/bootstrap.py`（修改）
- `src/gateway/api/router.py`（擴充 status endpoint）
- `src/runtime/process.py`（保留不動，作為 fallback）

### 回滾方式

還原 `bootstrap.py` 到 git HEAD → 系統回到純 spawn 模式。

---

## 7. Phase 4：文件與收尾（0.5 天）

### 任務清單

| # | 任務 | 驗收條件 | 依賴 |
|---|------|----------|------|
| 4.1 | 更新 `MEMORY.md` | 記錄搬遷決策、踩坑、最終架構 | Phase 3 |
| 4.2 | 新增 `knowledge/wiki/persistent-mode.md` | 操作說明：啟動、停止、設定、troubleshooting | Phase 3 |
| 4.3 | 更新 `docs/specs/persistent-process-spec.md` | 關閉開放問題、更新狀態為 accepted | Phase 3 |
| 4.4 | 清理 PoC 檔案 | 刪除 `poc_persistent.py` | — |

---

## 8. 風險管理

| 風險 | 機率 | 影響 | 緩解策略 |
|------|------|------|----------|
| team-agent 程式碼依賴本地未移植的模組 | 高 | import error | 搬遷時逐一確認 import，缺少的替換為簡化版 |
| `--legacy-ui` flag 未來被移除 | 低 | 常駐失效 | 追蹤 kiro-cli changelog；備案用 `--no-interactive --resume` |
| MCP server 啟動失敗導致 agent 無工具 | 中 | agent 無法工作 | `--require-mcp-startup` 確保；health loop 偵測後重啟 |
| 多 agent 同時常駐 RAM 不足 | 低 | OOM | 監控 RSS；idle eviction 機制（Phase 2 延伸） |
| 現有 A2A Router 與新 Daemon 整合困難 | 中 | 阻塞 Phase 3 | A2A spawn_fn 介面不變，只改底層實作 |

---

## 9. 依賴圖

```
Phase 1 (核心搬遷)
    │
    ├──→ Phase 2 (穩定性)
    │        │
    └────────┴──→ Phase 3 (整合)
                       │
                       └──→ Phase 4 (文件)
```

---

## 10. 搬遷注意事項

### 需適配的差異

| 面向 | team-agent | ai-team-agent | 適配方式 |
|------|-----------|---------------|----------|
| 模組路徑 | `ark_team_agent.xxx` | `src/runtime/xxx` | 修改 import path |
| EventBus | 無（用 event_log SQLite） | 有 `coordinator.events.bus` | 接入現有 EventBus |
| DB | `state/events.db` 等多個 SQLite | `coordinator.db.models` 單一 DB | 用現有 DB 或獨立 overflow.db |
| TG 整合 | `telegram.py` 直接整合 | `src/gateway/telegram/` 分層 | 保持現有 gateway 層不動 |
| A2A | 無（daemon 直接 dispatch） | 有 A2A Router + Graph + Discovery | spawn_fn 介面對接 |
| Config 結構 | flat dataclass | 已有 `TeamConfig` / `InstanceConfig` | 擴充現有 dataclass |

### 可直接搬（幾乎不用改的）

- `ManagedProcess`：獨立，只依賴 asyncio + logging
- `heartbeat.py`：獨立，只依賴 asyncio + Path
- `failure_memory.py`：獨立，無外部依賴
- `message_overflow.py`：獨立，只依賴 sqlite3

### 需重構適配的

- `Daemon`：最大的整合工作，需對接 EventBus + A2A + TG gateway
- `KiroBackend`：MCP config 路徑需對齊本專案的 agent 目錄結構
- `config.py`：合併新舊欄位，保持向下相容

---

## 11. 回滾計畫

### 全量回滾（一鍵回到 spawn 模式）

```bash
git checkout HEAD -- src/runtime/daemon.py src/runtime/config.py src/bootstrap.py team.yaml
rm src/runtime/managed_process.py src/runtime/kiro_backend.py
rm src/runtime/heartbeat.py src/runtime/failure_memory.py src/runtime/message_overflow.py
# 重啟 → 回到純 spawn 模式
```

### 軟回滾（保留程式碼，設定切換）

```yaml
# team.yaml — 所有 agent 回到 spawn
defaults:
  persistent: false
```

---

## 12. 驗收標準

- [ ] ≥ 3 agents 以常駐模式啟動並穩定運行 30 分鐘
- [ ] send_message → agent 收到 → 用 MCP reply 回覆使用者（端到端）
- [ ] 手動 kill agent 進程 → 10 秒內自動重啟
- [ ] 連續崩潰 3 次 → 進入 cooldown → 10 分鐘後自動重試
- [ ] `persistent: false` 設定下完全走舊 spawn 模式（向後相容）
- [ ] `/quit` graceful stop → 所有 agent 正常退出（code=0）
- [ ] Windows 平台全流程通過
