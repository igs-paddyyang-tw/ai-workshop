---
title: "AgentProcess 常駐化 — 架構設計"
type: design
status: accepted
created: 2026-07-14
language: zh-TW
related_spec: docs/specs/persistent-process-spec.md
related_plan: docs/plans/persistent-process-plan.md
---

# AgentProcess 常駐化 — 設計文件

## 1. 設計摘要

在現有 `AgentProcess`（spawn 模式）旁新增 `PersistentAgentProcess` 類別，
透過長駐子進程的 stdin/stdout 管道實現持續對話，搭配 Supervisor 層做健康檢查與自動重啟。

---

## 2. 架構總覽

```
┌─────────────────────────────────────────────────────────────────┐
│                         bootstrap.py                             │
│  ┌───────────┐  ┌──────────────┐  ┌───────────────────────────┐ │
│  │ TeamConfig│→ │ ProcessFactory│→ │ PersistentAgentProcess ×N │ │
│  │ (yaml)    │  │ (選擇模式)   │  │  or AgentProcess (spawn) │ │
│  └───────────┘  └──────────────┘  └────────────┬──────────────┘ │
│                                                 │                │
│  ┌──────────────────────────────────────────────▼──────────────┐ │
│  │              AgentSupervisor                                 │ │
│  │  • health_check loop (5s)                                   │ │
│  │  • auto-restart on crash                                    │ │
│  │  • idle eviction                                            │ │
│  │  • memory monitoring                                        │ │
│  └─────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

---

## 3. 核心元件設計（基於 team-agent 驗證方案）

### 3.1 ManagedProcess（從 team-agent 移植）

```python
@dataclass
class ManagedProcess:
    """長駐子進程包裝 — stdin/stdout 持續連接。"""

    name: str
    proc: asyncio.subprocess.Process | None = None
    _output_lines: deque[str]  # ring buffer (maxlen=500)
    _reader_task: asyncio.Task | None = None
    _pipe_broken: bool = False
    _output_count: int = 0  # 累計輸出行數（活動偵測）

    async def start(self, cmd: str, cwd: str) -> None:
        """啟動子進程（stderr 合併到 stdout）。"""

    async def send_input(self, text: str) -> None:
        """寫入 stdin（含 pipe 保護 + drain timeout）。"""

    def capture(self, lines: int = 200) -> str:
        """取最近 N 行 stdout（供 health check / error detection）。"""

    async def kill(self) -> None:
        """Graceful stop: /quit → terminate → kill。"""

    def is_alive(self) -> bool:
        """proc.returncode is None。"""
```

#### 進程啟動命令

```bash
# 常駐模式（team-agent 驗證可行）
kiro-cli chat --trust-all-tools --legacy-ui --require-mcp-startup

# 加 --resume 保持 context（非首次啟動）
kiro-cli chat --trust-all-tools --legacy-ui --require-mcp-startup --resume
```

#### 關鍵 flags 說明

| Flag | 作用 | 為什麼需要 |
|------|------|-----------|
| `--legacy-ui` | 停用 TUI renderer | TUI 模式 stdout=空，legacy 模式 stdout 有結構化輸出 |
| `--require-mcp-startup` | MCP 載入失敗立即退出 | 確保 agent 有工具可用，否則 health check 重啟 |
| `--trust-all-tools` | 免確認執行工具 | 自動化必須 |
| `stderr=STDOUT` | stderr 合併到 stdout | 統一從一個 stream 讀取所有輸出 |

#### stdin/stdout 通訊模式

```
[Daemon]                          [kiro-cli 子進程]
    │                                 │
    │── stdin: "任務描述\n" ─────────→│
    │                                 │
    │←── stdout: spinner / thinking  ─│  (ring buffer 收集，不解析)
    │←── stdout: tool calls / output ─│
    │                                 │
    │   agent 用 MCP reply() 回覆使用者（走 HTTP API）
    │                                 │
    │── stdin: "下一個任務\n" ───────→│  (隨時可寫，Queue 控制節奏)
```

**核心洞察：不需從 stdout 截取回應。Agent 用 MCP `reply()` tool 主動回覆使用者。
stdout 只用來做 ready detection + error detection + hang detection。**

### 3.2 Daemon（全域健康管理）

```python
class Daemon:
    """管理所有常駐 instance 的生命週期。"""

    instances: dict[str, InstanceState]

    async def start_instance(self, name: str) -> None:
        """啟動 → _wait_for_ready → 開始 queue worker。"""

    async def send_message(self, name: str, text: str) -> bool:
        """送入 msg queue，backpressure 時持久化到 overflow DB。"""

    async def _global_health_loop(self) -> None:
        """30 秒巡檢所有 instance：崩潰/hang/memory/rate-limit。"""

    async def _queue_worker(self, name: str) -> None:
        """per-instance task：從 queue 取訊息 → send_input → 動態 delay。"""
```

### 3.3 KiroBackend（配置管理）

```python
class KiroBackend:
    """啟動前寫入 .kiro/ 配置（MCP、Steering、Agent files）。"""

    def build_command(self, cfg) -> str:
        """產生啟動命令字串。"""

    def write_config(self, cfg) -> None:
        """寫入 mcp.json + steering files。"""

    @staticmethod
    def is_ready(output: str) -> bool:
        """偵測 'All tools are now trusted' 等 ready pattern。"""

    @staticmethod
    def detect_error(output: str) -> tuple[str, str] | None:
        """偵測 rate_limit / auth_error / network_error 等。"""
```

### 3.4 ProcessFactory

```python
class ProcessFactory:
    """依設定建立對應模式的 Process。"""

    @staticmethod
    def create(name: str, config: InstanceConfig) -> ManagedProcess | AgentProcess:
        if config.persistent:
            return ManagedProcess(name=name)
        return AgentProcess(...)  # 現有 spawn 模式 fallback
```

---

## 4. 資料流

### 4.1 正常任務流程

```
使用者 → TG Bot → Daemon.send_message("pm-agent", text)
                       │
         ┌─────────────▼──────────────────┐
         │ _queue_worker loop              │
         │ 1. msg = queue.get()            │
         │ 2. process.send_input(msg)      │
         │ 3. (agent 自行用 MCP reply 回覆)│
         │ 4. sleep(dynamic delay)         │
         └─────────────────────────────────┘
                       │
         agent 內部呼叫 MCP reply() → FastAPI → TG Bot → 使用者
```

**注意：Daemon 不需等待回應。Agent 透過 MCP tool 主動回覆。**

### 4.2 崩潰重啟流程

```
AgentSupervisor._check_health()
    │
    ├─ proc.returncode is not None → 進程已死
    │   ├─ consecutive_failures < 3 → restart()
    │   │   └─ start_persistent() with --resume
    │   └─ consecutive_failures >= 3 → mark UNAVAILABLE
    │       └─ notify admin-agent
    │
    ├─ memory_mb > max_memory_mb → 記憶體超限
    │   └─ session_rotate() → restart with fresh context
    │
    └─ idle_time > idle_timeout → 閒置過久
        └─ evict() → stop process → lazy respawn on next send
```

### 4.3 Graceful Shutdown 流程

```
SIGTERM / shutdown()
    │
    ├─ AgentProcess._shutting_down = True（拒絕新任務）
    ├─ 等待所有進行中任務完成（max 30s）
    ├─ 對每個常駐進程：
    │   ├─ stdin.write("/exit\n")
    │   ├─ wait_for(proc.wait(), timeout=5)
    │   └─ proc.kill() if still alive
    └─ 清理資源
```

---

## 5. 替代方案比較

### 方案 A：stdin/stdout Pipe 互動模式 ❌ 已排除

- 直接用 kiro-cli 互動模式的 stdin/stdout
- **PoC 結果：不可行**
  - stdout 始終為空（0 bytes）
  - 所有輸出（含回應）寫入 stderr
  - stderr 混雜 TUI spinner（⠋⠙⠹ Thinking...），無法乾淨解析
  - 無結構化的「回答結束」標記

### 方案 B：Persistent Session Pool（`--no-interactive --resume`）✅ 選定

- 保持 `--no-interactive` 模式（stdout 乾淨輸出）
- 每次 send 仍 spawn 進程，但透過 `--resume` 保持 session
- 優化：**Pre-warm spawn** — 提前啟動進程等待 stdin（不帶 message 參數）
- 結合 **Session 長連接**：維持同一 session ID，避免重複載入 context

### 方案 C：WebSocket 模式 ❌ 排除

- 修改 kiro-cli 提供 WebSocket server
- 優點：結構化通訊、明確訊息邊界
- 缺點：需要 fork/修改 kiro-cli → 違反「不改 CLI」原則

### 方案 D：HTTP Long-Polling ❌ 排除

- 每個 agent 啟動一個 HTTP server
- 優點：可分散部署
- 缺點：複雜度高、port 管理、不適合單機場景

### 決策理由

選擇方案 B — Persistent Session Pool，因為：
1. `--no-interactive` 的 stdout 輸出乾淨可靠（PoC 驗證）
2. `--resume` 天然保持 context（不需自行管理 session）
3. 不需修改 kiro-cli 原始碼
4. 可漸進優化：先 resume → 再加 pre-warm → 再加 session pool

### PoC 關鍵數據

```
--legacy-ui 模式（stderr=STDOUT 合併）：  ✅ 全項通過
  • Ready 偵測: ✅（"ctrl-c to start chatting now" 觸發，2.8s）
  • stdout 讀取: ✅（32 行初始化輸出 + 回應）
  • 第一次 send: ✅（7.7s，含 MCP 啟動失敗重試）
  • 第二次 send: ✅（2.7s，穩定快速）
  • 回應內容: 可從 "> 收到" / "> 2" 正則提取
  • 結束標記: "▸ Time:" 穩定出現在回答末尾
  • Graceful stop: ✅（/quit → code=0）

--no-interactive 模式（之前 PoC）：
  • stdout: 乾淨回應（"> 2\n"），18 bytes
  • 但每次需 spawn 新進程（2-5 秒冷啟動）

互動模式 無 --legacy-ui：
  • stdout: 0 bytes（完全無輸出）❌ 不可用
```

---

## 6. ~~修正後架構：Persistent Session Pool~~ — 未採用

> **決策記錄（2026-07-29）：** 本節所描述的 Session Pool + Pre-warm 架構**未採用**。
> 實際選用了 §3 的 `ManagedProcess`（stdin pipe 常駐進程）方案，由 `PersistentDaemon` 統一管理。
>
> 保留此節僅作為決策脈絡參考，不代表待實作功能。
> `SessionPoolState` 和 `PreWarmPool` 為本節衍生的 model，同樣**不會實作**。

---

<details>
<summary>展開查看原始 Session Pool 設計（供參考）</summary>

### 核心概念

```
                 ┌─────────────────────────────────────┐
                 │        SessionPool (per agent)       │
                 │                                     │
                 │  session_id: "abc123"               │
                 │  state: idle / busy                 │
                 │  last_used: timestamp               │
                 │                                     │
                 │  send(msg):                         │
                 │    spawn --no-interactive --resume   │
                 │    --resume-id session_id msg       │
                 │    等待完成 → 回傳 stdout            │
                 └─────────────────────────────────────┘
```

### 與現有 spawn 模式的差異

| 面向 | 原始 spawn | Session Pool |
|------|-----------|-------------|
| Session | 每次 `--resume`（最新 session） | `--resume-id` 固定 session |
| Context | 每次從磁碟載入 | 固定 session 持續累積 |
| Cold start | 每次 2-5 秒 | 首次 2-5 秒，後續可 pre-warm |
| Pre-warm | 無 | 可提前 spawn 等待（準備好進程） |

### Pre-warm 機制（未採用）

```python
class PreWarmPool:
    """預先 spawn 進程，等到收到任務時立即用。"""
    async def warm_up(self, agent_name: str) -> None: ...
    async def acquire(self, agent_name: str, message: str) -> str: ...
```

</details>

---

## 7. Session Rotate 機制

```
觸發條件（任一）：
  • 累計處理 > 50 個任務
  • 估算 context tokens > 100K
  • 手動呼叫 rotate()

流程：
  1. 記錄當前 session_id
  2. 建立新 session（下次 send 不帶 --resume-id）
  3. 更新 session_id 為新值
  4. 重置計數器
```

---

## 8. 設定架構（team.yaml 擴充）

```yaml
defaults:
  backend: kiro-cli
  model: auto
  persistent: true
  idle_timeout_minutes: 30
  max_memory_mb: 512
  session_rotate_after: 50    # 每 50 任務 rotate

instances:
  admin-agent:
    persistent: true
    idle_timeout_minutes: 0   # 永不休眠（入口 agent）
  pm-agent:
    persistent: true
    idle_timeout_minutes: 60
  market-agent:
    persistent: false         # 低頻使用，保持 spawn 模式
```

---

## 9. 故障降級策略

| 故障場景 | 降級策略 |
|----------|----------|
| 常駐進程崩潰 | 自動 restart（最多 3 次），失敗後降級為 spawn 模式 |
| stdin 寫入失敗 | 重建管道，retry 1 次 |
| stdout 讀取超時 | kill 進程 → restart → 重送訊息 |
| 記憶體超限 | 強制 rotate（不等待任務完成） |
| 全部 persistent 失敗 | 全團降級為 spawn 模式 + 通知 admin |

---

## 10. 安全性考量

| 面向 | 措施 |
|------|------|
| 進程隔離 | 每個 agent 獨立進程 + 獨立 working_dir |
| 資源限制 | max_memory_mb + idle_timeout 防止失控 |
| 信號處理 | Windows: CREATE_NEW_PROCESS_GROUP；Linux: SIGTERM → SIGKILL |
| Secret 保護 | 不在 stdout 日誌中記錄 token/key |
| 輸入驗證 | send() 傳入的 message 做長度限制（< 100KB） |

---

## 11. 可觀測性

### Metrics（EventBus 事件）

| 事件 | 資料 |
|------|------|
| `AGENT_STARTED` | agent_id, mode, pid |
| `AGENT_RESTARTED` | agent_id, reason, restart_count |
| `AGENT_EVICTED` | agent_id, idle_minutes |
| `AGENT_CRASHED` | agent_id, returncode, stderr |
| `SESSION_ROTATED` | agent_id, tasks_before_rotate |

### API Endpoint

```
GET /api/agents/{id}/health
→ { "pid": 12345, "mode": "persistent", "uptime_s": 3600,
    "memory_mb": 256, "tasks_total": 42, "last_active": "2026-07-14T10:00:00Z",
    "consecutive_failures": 0 }
```

---

## 12. 檔案變更清單

| 檔案 | 動作 | 說明 |
|------|------|------|
| `src/runtime/persistent_process.py` | 新增 | PersistentAgentProcess + ResponseCollector |
| `src/runtime/supervisor.py` | 新增 | AgentSupervisor（健康檢查 + eviction） |
| `src/runtime/process_factory.py` | 新增 | ProcessFactory（依設定選擇模式） |
| `src/runtime/process.py` | 修改 | 抽取共用介面 BaseAgentProcess |
| `src/runtime/config.py` | 修改 | InstanceConfig 新增 persistent/idle_timeout/max_memory |
| `src/runtime/daemon.py` | 修改 | 整合 AgentSupervisor |
| `src/bootstrap.py` | 修改 | 使用 ProcessFactory 建立 agents |
| `team.yaml` | 修改 | 新增 persistent 相關設定 |
| `src/gateway/api/router.py` | 修改 | 新增 /health endpoint |
