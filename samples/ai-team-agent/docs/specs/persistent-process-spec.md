---
title: "AgentProcess 常駐化（Persistent Process）"
type: spec
status: accepted
created: 2026-07-14
language: zh-TW
related_design: docs/designs/persistent-process-design.md
related_plan: docs/plans/persistent-process-plan.md
---

# AgentProcess 常駐化 — 規格文件

## 1. 摘要

將 `AgentProcess` 的進程生命週期從「每次任務 spawn → 完成退出」改為「啟動後常駐，持續接收任務」，
降低冷啟動延遲（2-5s → <100ms），並天然保持 session context 不需每次 `--resume` 載入。

---

## 2. 問題陳述

### 現狀痛點

| 痛點 | 影響 |
|------|------|
| 每次 spawn 冷啟動 2-5 秒 | 多步驟任務（leader→worker→qa）累計延遲 10-15 秒 |
| `--resume` 每次重新載入完整 context | 重複消耗 token（context 越長成本越高） |
| 無法即時對話 | 使用者體驗差，秒級延遲不適合互動場景 |
| 每次 spawn 重新建立 MCP 連線 | 浪費連線建立開銷 |

### 根本原因

`AgentProcess._execute()` 以 `asyncio.create_subprocess_exec()` 每次建立新進程，
完成後進程退出、所有狀態丟失。

---

## 3. 目標

| 目標 | 量化指標 |
|------|----------|
| 降低任務延遲 | P95 < 200ms（從收到訊息到 agent 開始處理） |
| 減少重複 token 消耗 | context 載入次數降低 > 90% |
| 保持進程隔離 | 單一 agent crash 不影響其他 |
| 支援即時互動 | 單輪回覆 < 3 秒（不含 LLM 推理時間） |

---

## 4. 非目標

| 非目標 | 原因 |
|--------|------|
| 改變 kiro-cli 核心程式碼 | 本專案僅做外部整合，不 fork CLI |
| 支援多租戶並行（同一 agent 同時處理多任務） | 維持 Queue 排隊語義不變 |
| 去除 spawn 模式 | 保留為 fallback，新增 persistent 為可選模式 |
| 更換 LLM backend | 僅改變進程管理，不動推理層 |

---

## 5. 功能需求

### FR-1：常駐進程管理

- 系統啟動時，為每個 agent 啟動一個長駐子進程
- 子進程以 kiro-cli 互動模式運行（不帶 `--no-interactive`）
- 提供 `start_persistent()` / `stop()` / `restart()` 生命週期 API

### FR-2：訊息通訊協議

- 透過子進程的 stdin 寫入任務訊息
- 從 stdout 讀取回應（需定義訊息邊界偵測機制）
- 支援逾時：單次任務超過 `timeout` 自動標記失敗

### FR-3：健康檢查與自動重啟

- Daemon 定期檢查進程 `returncode`（None = 存活）
- 崩潰自動重啟，重啟時帶 `--resume` 恢復 context
- 連續失敗 N 次後標記為 UNAVAILABLE，通知 admin-agent

### FR-4：Graceful Shutdown

- 收到系統 shutdown 信號時：
  1. 停止接收新任務
  2. 等待當前任務完成（最多 30 秒）
  3. 向子進程發送 `/exit` 或 SIGTERM
  4. 確認退出

### FR-5：混合模式支援

- `team.yaml` 新增 `persistent: true/false` 設定
- 支援同一團隊混用 spawn 與 persistent 模式
- 預設值由 `defaults.persistent` 決定

### FR-6：Idle Eviction（閒置回收）

- 常駐進程閒置超過 `idle_timeout_minutes` 後自動休眠（kill）
- 下次有任務時自動 respawn
- 防止長時間佔用 RAM

---

## 6. 非功能性需求

| NFR | 指標 | 量測方式 |
|-----|------|----------|
| 記憶體 | 單一常駐 agent < 512MB | Process monitor |
| 可用率 | 自動重啟後 < 10 秒恢復 | Health check log |
| 併發 | 8 agents 同時常駐穩定運行 | 壓力測試 |
| 相容性 | Windows + Linux 均可運行 | CI 雙平台測試 |
| 可觀測 | 進程狀態即時可查（API + log） | `/api/agents` endpoint |

---

## 7. 使用者故事

### US-1：即時對話

> 身為使用者，我發送訊息後希望 agent 能立即開始處理（無冷啟動延遲），
> 讓多輪對話體驗更流暢。

### US-2：成本控制

> 身為 admin，我希望 agent 不需要每次都重新載入完整 context，
> 以減少重複的 token 消耗。

### US-3：穩定性

> 身為 admin，我希望某個 agent 崩潰時能自動重啟，
> 且不影響其他 agent 的正常運作。

### US-4：資源彈性

> 身為 admin，我希望長時間沒任務的 agent 自動休眠，
> 有新任務時再自動喚醒，平衡延遲與資源佔用。

---

## 8. 成功指標

| 指標 | Baseline | Target | 量測方式 |
|------|----------|--------|----------|
| 任務啟動延遲 | 2-5 秒 | < 200ms | Timestamp diff (receive → first output) |
| Token 重複消耗 | 每次載入完整 context | 僅首次 + rotate 時 | Token usage log |
| 崩潰恢復時間 | 手動重啟 | < 10 秒自動 | Health check timestamp |
| 空閒資源佔用 | 0（spawn 模式） | < 512MB/agent | RSS monitoring |

---

## 9. 介面定義

### 設定介面（team.yaml 擴充）

```yaml
defaults:
  backend: kiro-cli
  model: auto
  persistent: true              # 新增：預設常駐
  idle_timeout_minutes: 30      # 新增：閒置回收
  max_memory_mb: 512            # 新增：記憶體上限

instances:
  admin-agent:
    persistent: true            # 可 per-instance override
    idle_timeout_minutes: 0     # 0 = 永不休眠
```

### 程式介面（AgentProcess 擴充）

```python
class AgentProcess:
    async def start_persistent(self) -> None: ...
    async def send(self, text: str) -> str | None: ...  # 現有，語義不變
    async def stop(self) -> None: ...
    async def restart(self) -> None: ...
    def is_alive(self) -> bool: ...
    @property
    def mode(self) -> Literal["spawn", "persistent"]: ...
```

### API 介面（狀態查詢擴充）

```
GET /api/agents
→ [{ "id": "admin-agent", "status": "running", "mode": "persistent",
     "uptime_seconds": 3600, "memory_mb": 256, "tasks_completed": 42 }]
```

---

## 10. 依賴與限制

| 依賴 | 說明 |
|------|------|
| kiro-cli 互動模式 | 必須支援 stdin 輸入 + stdout 輸出的持續對話 |
| 訊息邊界偵測 | 需要辨識 kiro-cli 回答結束的 marker（prompt `> ` 或其他） |
| Windows 進程管理 | 需要 `CREATE_NEW_PROCESS_GROUP` + proper signal handling |

| 限制 | 影響 |
|------|------|
| kiro-cli 可能無 pipe 模式 | 需自行解析 stdout 偵測回答結束 |
| 長 session context 溢出 | 需實作 session rotate 機制 |
| 同一 agent 不支援並行 | 維持 Queue 語義，不改變 |

---

## 11. 開放問題

| # | 問題 | 影響 | 狀態 |
|---|------|------|------|
| 1 | kiro-cli 互動模式的 stdout 是否有結構化結束標記？ | 決定訊息邊界偵測策略 | ✅ 已驗證：互動模式 stdout=空，不可用。改用 --no-interactive + --resume-id |
| 2 | 常駐進程累積 context 後 token 上限如何處理？ | 長時間運行會 OOM | 用 session rotate（每 50 任務或 100K tokens 換新 session） |
| 3 | Windows 下 kiro-cli 是否支援 stdin pipe？ | 決定是否需要 wrapper | ✅ 已驗證：stdin 可寫入，進程不崩潰，graceful stop 正常 |
| 4 | `--resume-id` 是否支援指定固定 session？ | 決定 Session Pool 可行性 | 待驗證（CLI help 有 `--resume-id <SESSION_ID>` flag） |
| 5 | Pre-warm 是否可行（不帶 message 的 spawn）？ | 決定是否能消除冷啟動 | 待驗證：kiro-cli 需要 [INPUT] 參數才執行 |

---

## 12. 里程碑概覽

| Phase | 交付 | 預估 |
|-------|------|------|
| Phase 1 | PersistentProcess 核心 + stdin/stdout 通訊 | 3 天 |
| Phase 2 | Health check + auto-restart + graceful shutdown | 2 天 |
| Phase 3 | Idle eviction + memory guard + session rotate | 2 天 |
| Phase 4 | 混合模式 + team.yaml 設定 + API 擴充 | 1 天 |
| Phase 5 | 雙平台測試 + 文件更新 | 1 天 |
