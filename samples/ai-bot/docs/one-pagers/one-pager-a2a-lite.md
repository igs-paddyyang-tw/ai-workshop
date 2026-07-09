---
title: "A2A 精簡版 — 從個體升級為跨機團隊"
type: onepager
status: approved
created: 2026-07-07
updated: 2026-07-08
---

# A2A 精簡版 — 從個體升級為跨機團隊

## 目標

同一個 ai-bot 專案，三階段漸進升級，架構與 ai-team-agent 完全一致：

```
沒有 team.yaml → 個體模式（課程 A：駕馭工程）
有 team.yaml  → 團隊模式（課程 B-04：本地協作）
team.yaml 含 transport: http → 跨機模式（課程 B-06：分散式協作）
```

核心原則：**沒有就不啟用**，每一層對下相容。

## 架構對齊

ai-bot 與 ai-team-agent 使用**同一套 coordinator/a2a/**，確保：
- 學員學一套，兩邊都會用
- 專家系統蒸餾的 Agent 能力可直接搬到遊戲開發平台
- 遇到問題隨時回專家系統調整，不需要適配

---

## 從 ai-team-agent 搬入

完整複製 `src/coordinator/a2a/` 整包，不精簡、不重寫：

| 檔案 | 職責 |
|------|------|
| `protocol.py` | TaskHandoff + ProgressEvent dataclass |
| `router.py` | A2ARouter — dispatch + on_complete + on_failed |
| `graph.py` | TaskGraph — DAG 依賴圖 |
| `shared_memory.py` | 檔案系統寫 knowledge/shared/tasks/*.md |
| `discovery.py` | 語意匹配（description + 同義詞 + 負載） |
| `feedback_loop.py` | 失敗重試迴圈 |
| `progress_parser.py` | 從 agent stdout 解析進度 |
| `transport.py` | 🆕 transport 抽象層（local + http） |
| `server.py` | 🆕 A2A HTTP endpoints |

不搬的（ai-bot 不需要）：

| 不搬 | 原因 |
|------|------|
| `coordinator/db/` | 不用 SQLite，SharedMemory（Markdown）就是唯一 store |
| `coordinator/events/` | 不用 EventBus，router 直接回傳結果 |
| `coordinator/services/` | cost_tracker / health_monitor 等先不引入 |
| `coordinator/task_lifecycle.py` | 依賴 SQLite 的狀態機，不搬；task 狀態由 SharedMemory 管 |
| `runtime/scheduler.py` | 先手動派工，排程是後續加 |

---

## team.yaml 格式（統一，兩邊完全一致）

```yaml
name: "遊戲開發團隊"

instances:
  pm-agent:
    working_directory: agents/pm-agent
    role: leader
    transport: local                      # 預設，可省略

  market-agent:
    working_directory: agents/market-agent
    role: worker

  coder-agent:
    role: worker
    transport: http                       # 遠端
    endpoint: http://192.168.1.52:8000    # 另一台 ai-bot 的位址
    auth_token_env: CODER_AGENT_TOKEN     # token 放 .env，不進 yaml

  qa-agent:
    role: worker
    transport: http
    endpoint: http://192.168.1.53:8000
    auth_token_env: QA_AGENT_TOKEN
```

`transport` 沒寫就是 `local`，現有 team.yaml 完全相容。

---

## transport.py — 核心抽象

```python
"""Transport 抽象層 — 本地/遠端透明切換。"""

async def dispatch(agent_cfg, task: TaskHandoff, spawn_fn) -> str | None:
    """統一派工介面。"""
    if agent_cfg.transport == "local":
        return await spawn_fn(agent_cfg.name, _build_message(task))
    elif agent_cfg.transport == "http":
        return await http_dispatch(agent_cfg, task)
    else:
        raise ValueError(f"Unknown transport: {agent_cfg.transport}")


async def http_dispatch(agent_cfg, task: TaskHandoff) -> str | None:
    """POST 到遠端 ai-bot 的 /api/v1/a2a/task，等待 callback 回報。"""
    import os, httpx

    token = os.getenv(agent_cfg.auth_token_env, "")
    headers = {"X-A2A-Token": token, "Content-Type": "application/json"}

    payload = {
        "task_id": task.task_id,
        "goal": task.title,
        "context": task.context,
        "callback_url": f"http://{get_local_ip()}:{get_port()}/api/v1/a2a/callback",
        "priority": task.priority,
        "timeout_seconds": 240,
        "metadata": {"requester": task.from_agent}
    }

    async with httpx.AsyncClient(timeout=240) as client:
        resp = await client.post(
            f"{agent_cfg.endpoint}/api/v1/a2a/task",
            json=payload, headers=headers,
        )
        resp.raise_for_status()

    # 等待 callback 回報（或 fallback 輪詢）
    return await wait_for_result(task.task_id, timeout=240)
```

---

## A2A HTTP endpoints（server.py，掛到現有 FastAPI）

每台 ai-bot 都是 server 也是 client：

| Method | Path | 功能 |
|--------|------|------|
| POST | `/api/v1/a2a/task` | 接收派工 |
| POST | `/api/v1/a2a/callback` | 接收遠端回報結果 |
| GET | `/api/v1/a2a/card` | 回傳 Agent Card（能力宣告） |
| PATCH | `/api/v1/a2a/task/{task_id}` | 心跳/進度更新 |

### Request：POST /api/v1/a2a/task

```json
{
  "task_id": "2026-07-08_003_code-review",
  "goal": "Review 老虎機主迴圈 performance",
  "context": "相關背景資訊",
  "callback_url": "http://192.168.1.50:8000/api/v1/a2a/callback",
  "priority": 3,
  "timeout_seconds": 240,
  "metadata": { "requester": "pm-agent" }
}
```

### Response

```json
{
  "task_id": "2026-07-08_003_code-review",
  "status": "accepted",
  "agent_id": "coder-agent"
}
```

### Callback：遠端完成後 POST 回 coordinator

```json
{
  "task_id": "2026-07-08_003_code-review",
  "status": "done",
  "result": "## Code Review 結果\n\n1. 主迴圈有 3 處可優化...",
  "token_usage": { "input_tokens": 2340, "output_tokens": 1890 },
  "duration_seconds": 95
}
```

### Agent Card：GET /api/v1/a2a/card

```json
{
  "name": "coder-agent",
  "description": "Pixijs + Go 開發，H5 老虎機實作",
  "skills": ["ark-code-spec-validator"],
  "status": "idle",
  "version": "1.0.0"
}
```

---

## Discovery 擴展

本地 Agent：讀 `agents/*/SOUL.md` 的 description → 進 registry。
遠端 Agent：啟動時打 `GET /api/v1/a2a/card` → 拿回 description → 進同一個 registry。

discovery.py 的匹配邏輯**一行都不改** — 它只看 description，不管來源。

---

## 任務存儲：雙寫

```
Coordinator（派工方）：knowledge/shared/tasks/task_003.md  ← SharedMemory 寫
Executor（執行方）：  knowledge/shared/tasks/task_003.md  ← 本地也存一份
```

兩台機器各自的 WikiEngine 都能 RAG 到任務狀態。

---

## 安全與網路

| 關注點 | 方案 |
|--------|------|
| **認證** | X-A2A-Token，雙方 .env 各存一份，FastAPI dependency 驗證 |
| **逾時** | http_dispatch timeout 240s，失敗標 failed + TG 通知 |
| **心跳** | 長任務定期 PATCH 狀態，coordinator 超過 N 分鐘沒心跳自動回收 |
| **回報路徑** | callback_url 填 coordinator 可達位址；NAT 環境 fallback 輪詢 |
| **冪等** | task_id 全域唯一，重複 POST 回傳已存在狀態 |

---

## 新增檔案

```
ai-bot/
├── team.yaml                           ← 團隊配置（選配）
├── team-distributed.yaml               ← 跨機團隊範本
└── src/
    └── coordinator/                    ← 🆕 從 ai-team-agent 完整搬入
        └── a2a/
            ├── __init__.py
            ├── protocol.py             ← TaskHandoff + ProgressEvent
            ├── router.py               ← A2ARouter dispatch 核心
            ├── graph.py                ← TaskGraph DAG
            ├── shared_memory.py        ← 檔案系統 tasks/*.md
            ├── discovery.py            ← 語意匹配
            ├── feedback_loop.py        ← 失敗重試
            ├── progress_parser.py      ← stdout 進度解析
            ├── transport.py            ← 🆕 local + http dispatch
            └── server.py              ← 🆕 A2A HTTP endpoints
```

## 修改檔案

| 檔案 | 改動 |
|------|------|
| `src/server/main.py` | 掛載 a2a/server.py 的路由（`app.include_router`） |
| `src/bot/handlers.py` | L3 加 TEAM intent → 走 A2ARouter.dispatch() |
| `src/agent/process.py` | 不動（繼續當 local transport 的 spawn_fn） |
| `.env.example` | 加 `CODER_AGENT_TOKEN`、`QA_AGENT_TOKEN` 範例 |
| `requirements.txt` | 加 `httpx>=0.27` |

---

## 啟動邏輯（加在現有 start.py）

```python
# start.py 新增判斷
team_yaml = Path("team.yaml")
if team_yaml.exists():
    from src.coordinator.a2a.router import A2ARouter
    from src.coordinator.a2a.graph import TaskGraph
    from src.coordinator.a2a.shared_memory import SharedMemory
    from src.coordinator.a2a.discovery import AgentDiscovery

    # 組裝 router
    graph = TaskGraph()
    memory = SharedMemory()
    discovery = AgentDiscovery(memory)
    router = A2ARouter(graph, memory, discovery, spawn_fn=_spawn_fn)

    # 對 http instances 打 GET /card 註冊遠端 Agent
    # ...
```

沒有 team.yaml → 完全不 import coordinator，個體模式零影響。

---

## 新增 TG 指令

| 指令 | 做什麼 |
|------|--------|
| `/assign 描述` | PM 接收 → discovery 選人 → transport dispatch |
| `/board` | 看 knowledge/shared/tasks/ 任務狀態 |
| `@pm 描述` | 自然語言派工（L3 TEAM intent） |

---

## 實作步驟

| # | 任務 | 時間 |
|---|------|------|
| 1 | 搬 coordinator/a2a/ 整包到 ai-bot | 15 min |
| 2 | 新增 transport.py（local + http dispatch） | 45 min |
| 3 | 新增 server.py（A2A endpoints + token auth） | 45 min |
| 4 | start.py 偵測 team.yaml → 組裝 router | 20 min |
| 5 | handlers.py 加 TEAM intent → router.dispatch() | 30 min |
| 6 | 加 /assign /board TG 處理 | 30 min |
| 7 | discovery 啟動時 fetch 遠端 Agent Card | 20 min |
| 8 | timeout / heartbeat / failed + TG 通知 | 40 min |
| 9 | 驗收：兩台機器互派任務 | 30 min |

**總計 ~4.5 小時**

---

## 驗收條件

- [ ] 沒有 team.yaml 時行為完全不變（個體模式）
- [ ] 有 team.yaml 時 /assign 能派工（本地 Agent）
- [ ] discovery 根據描述選正確的 Agent
- [ ] 任務狀態寫入 knowledge/shared/tasks/
- [ ] /board 能看到任務列表
- [ ] transport: http 的 Agent 能收到派工並回報結果
- [ ] 遠端 Agent 出現在 discovery 候選名單（via Card）
- [ ] 錯 token 被拒（401）
- [ ] 遠端斷線時任務標 failed + TG 通知，不卡死
- [ ] Coordinator 和 Executor 雙寫 task，各自 Wiki 可查
- [ ] 心跳逾時自動回收

---

## 教學對應

| 堂 | 模式 | 教什麼 |
|----|------|--------|
| 01-03 | 個體（無 team.yaml） | SOUL + Skill + Wiki |
| 04 | 團隊（加 team.yaml） | /assign + discovery + 協作 |
| 05 | 團隊 + 排程 | 自動派工 + 知識迴圈 |
| **06** | **跨機（加 transport: http）** | **兩人一組互掛 IP，分散式 Agent** |

學員操作：
- 04：`cp team-ops.yaml team.yaml` → 團隊模式
- 06：team.yaml 加一個 `transport: http` instance → 跨機模式
- 06 課堂：兩人一組，各自跑 ai-bot，互相掛對方的 Agent
