---
title: "A2A 精簡版 — 從個體升級為團隊"
type: onepager
status: approved
created: 2026-07-07
---

# A2A 精簡版 — 從個體升級為團隊

## 目標

同一個 ai-bot 專案，有 `team.yaml` 就跑團隊模式，沒有就跑個體模式。

```
沒有 team.yaml → 個體模式（課程 A：駕馭工程）
有 team.yaml  → 團隊模式（課程 B：迴圈工程）
```

## 從 ai-team-agent 搬什麼

| 搬 | 檔案 | 做什麼 |
|----|------|--------|
| ✅ | `team.yaml` | 定義誰在團隊 + role（leader/worker） |
| ✅ | `discovery.py` | 任務→Agent 語意匹配 |
| ✅ | `task_lifecycle.py` | 狀態機（pending→assigned→running→done/failed） |

| 不搬 | 原因 |
|------|------|
| EventBus | 太重，個人用不需要 pub/sub |
| SQLite DB | 用 knowledge/tasks/*.md 替代（Wiki 能查） |
| Scheduler | 先手動派工，排程是後續加 |
| apps/web/ | 已有 Web UI 6 頁 |
| gateway/ | 已有 handlers.py |

## 架構

```
start.py 啟動時：
  team.yaml 存在？
    ├── 是 → 載入團隊配置 → PM 能派工 → /assign 啟用
    └── 否 → 個體模式（現有行為不變）

對話路由變化：
  L3 keyword 加入：「派工」「assign」「分配」→ IntentType.TEAM
  L4 加入：PM discovery → 選人 → AgentProcess.send() → 回報結果
```

## 新增檔案

```
ai-bot/
├── team.yaml                    ← 團隊配置（選配，有才啟用）
├── team-ops.yaml                ← 營運團隊範本
├── team-dev.yaml                ← 研發團隊範本
└── src/agent/
    ├── discovery.py             ← 語意匹配（Agent description vs 任務）
    ├── task_lifecycle.py        ← 狀態機
    └── team_manager.py          ← 載入 team.yaml + 組隊管理
```

## team.yaml 格式（對齊 ai-team-agent）

```yaml
name: "遊戲開發團隊"

instances:
  admin-agent:
    working_directory: agents/admin-agent
    role: admin
  pm-agent:
    working_directory: agents/pm-agent
    role: leader
  market-agent:
    working_directory: agents/market-agent
    role: worker
  coder-agent:
    working_directory: agents/coder-agent
    role: worker
  qa-agent:
    working_directory: agents/qa-agent
    role: worker
```

## 新增 TG 指令

| 指令/觸發 | 做什麼 |
|-----------|--------|
| `/assign 描述` | PM 接收 → discovery 選人 → 派工 |
| `@pm 描述` | 自然語言派工（L3 TEAM intent） |
| `/board` | 看任務狀態（from task_lifecycle） |

## 任務狀態存到 Wiki

```
knowledge/tasks/
├── 2026-07-07_001_slot-analysis.md
│   ---
│   title: "老虎機競品分析"
│   type: task
│   status: done
│   assignee: market-agent
│   created: 2026-07-07
│   ---
│   ## 任務描述
│   ...
│   ## 結果
│   ...
```

好處：WikiEngine 能 RAG 到任務狀態 → TG 問「進度如何」自動回答。

## 實作步驟

| # | 任務 | 時間 |
|---|------|------|
| 1 | 搬 discovery.py（從 ai-team-agent 精簡） | 30 min |
| 2 | 搬 task_lifecycle.py（精簡為 Markdown 狀態機） | 30 min |
| 3 | 新建 team_manager.py（載入 team.yaml） | 20 min |
| 4 | handlers.py 加 TEAM intent 路由 | 30 min |
| 5 | 加 /assign /board TG 處理 | 30 min |
| 6 | team-ops.yaml + team-dev.yaml 範本 | 10 min |
| 7 | start.py 偵測 team.yaml 切換模式 | 15 min |

**總時間：~3 小時**

## 驗收條件

- [ ] 沒有 team.yaml 時行為完全不變（個體模式）
- [ ] 有 team.yaml 時 /assign 能派工
- [ ] discovery 能根據描述選正確的 Agent
- [ ] 任務狀態寫入 knowledge/tasks/
- [ ] /board 能看到任務列表
- [ ] TG 問「進度」能引用 tasks/ 回答

## 教學對應

| 堂 | 模式 | 教什麼 |
|----|------|--------|
| 01-03 | 個體（無 team.yaml） | SOUL + Skill + Wiki |
| 04 | 團隊（加 team.yaml） | /assign + discovery + 協作 |
| 05 | 團隊 + 排程 | 自動派工 + 知識迴圈 |

學員在 04 開始時：`cp team-ops.yaml team.yaml` → 馬上升級為團隊模式。
