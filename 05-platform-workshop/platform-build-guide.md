---
title: "Workshop 03 — 進階平台功能自學指南"
type: guide
created: 2026-06-23
language: zh-TW
---

# Workshop 03 — 進階平台功能自學指南

> **定位**：進階平台功能 — API + Web Dashboard + A2A 協作 + 四層架構
> **五層對應**：L1 Entry + L2 AI Team OS
> **時間**：約 60 分鐘

## 操作位置圖示

| 圖示 | 意義 |
|------|------|
| 📝 | AI IDE 聊天框（Kiro CLI / Cursor） |
| 📱 | Telegram Bot 對話 |
| 💻 | 終端機（Terminal） |

---

## 前置條件

- [x] 已完成 Workshop 04（有 `my-team` 專案）
- [x] Python 3.12+ 已安裝
- [x] Node.js 20+ 已安裝
- [x] `my-team` 專案可正常啟動

---

## Step 1：Backend API 探索（21 個端點）

### 1.1 啟動 Server

💻 終端機：

```bash
cd my-team
uvicorn src.server.main:app --reload --port 8000
```

看到 `Uvicorn running on http://0.0.0.0:8000` 即成功。

### 1.2 測試核心端點

💻 開另一個終端機視窗：

```bash
# Health Check
curl http://localhost:8000/api/v1/health

# 列出所有已註冊 Skills
curl http://localhost:8000/api/v1/skills

# Dashboard 統計
curl http://localhost:8000/api/admin/dashboard/stats

# 審計日誌
curl http://localhost:8000/api/admin/audit
```

### 1.3 完整端點分類表

| 分類 | 數量 | 端點 |
|------|------|------|
| **Health** | 1 | `GET /api/v1/health` |
| **Skills** | 2 | `GET /api/v1/skills`、`POST /api/v1/skills/invoke` |
| **Chat** | 1 | `POST /api/v1/chat` |
| **Wiki** | 3 | `POST /api/v1/wiki/query`、`POST /api/v1/wiki/ingest`、`POST /api/v1/wiki/lint` |
| **Workflows** | 3 | `GET /api/v1/workflows`、`POST /api/v1/workflows/run`、`GET /api/v1/workflows/{id}/status/{run_id}` |
| **Schedules** | 2 | `GET /api/v1/schedules`、`POST /api/v1/schedules/{id}/toggle` |
| **Admin** | 8 | `GET /api/admin/dashboard/stats`、`GET /api/admin/audit`、`GET /api/admin/agents`、`POST /api/admin/agents/{id}/pause`、`POST /api/admin/agents/{id}/resume`、`GET /api/admin/tasks`、`POST /api/admin/tasks`、`GET /api/admin/settings` |
| **Files** | 1 | `GET /api/files` |
| **合計** | **21** | |

### 1.4 驗證

✅ `GET /api/admin/dashboard/stats` 回傳包含：

```json
{
  "agents_online": 3,
  "tasks_today": 12,
  "success_rate": 0.95,
  "avg_response_ms": 420
}
```

看到 `agents_online` 和 `tasks_today` 欄位即代表 Admin API 正常運作。

---

## Step 2：Web Dashboard

### 2.1 安裝與啟動

💻 終端機：

```bash
cd my-team/apps/web
npm install
npm run dev
```

### 2.2 開啟 Dashboard

瀏覽器開啟：**http://localhost:3000**

### 2.3 功能巡覽

| 頁面 | 功能 | 對應 API |
|------|------|---------|
| **Overview** | KPI 卡片（在線 Agent 數、今日任務、成功率） | `/api/admin/dashboard/stats` |
| **Agents** | Agent 列表、狀態燈、暫停/恢復操作 | `/api/admin/agents` |
| **Tasks** | 任務追蹤、狀態流轉、依賴圖視覺化 | `/api/admin/tasks` |
| **Audit** | 操作日誌時間軸、篩選與搜尋 | `/api/admin/audit` |
| **Settings** | 系統設定、LLM 後端切換、排程管理 | `/api/admin/settings` |

### 2.4 驗證

✅ Dashboard 首頁顯示 KPI 卡片，數據與 `curl /api/admin/dashboard/stats` 回傳一致。

---

## Step 3：A2A 協作機制

### 3.1 核心概念

**A2A（Agent-to-Agent）** 讓多個 Agent 協作完成複雜任務：

```
使用者需求
    ↓
TaskGraph 拆解為子任務
    ↓
Agent Discovery 匹配最適 Agent
    ↓
並行/序列執行
    ↓
結果彙整回報
```

### 3.2 TaskGraph — 任務依賴圖

TaskGraph 支援兩種執行模式：

```
parallel（並行）：獨立任務同時執行
┌─ Task A ─┐
│           ├→ Task D（等 A+B 完成）
└─ Task B ─┘

sequential（序列）：有依賴的任務依序執行
Task A → Task B → Task C
```

### 3.3 Agent Discovery — 自動匹配

系統根據 Agent 的能力標籤（capabilities）自動派工：

```
任務需要: ["python", "data-analysis"]
    ↓
掃描所有 Agent 的 capabilities
    ↓
匹配到: data-agent (capabilities: ["python", "data-analysis", "sql"])
    ↓
自動派工
```

### 3.4 實測 A2A 協作

💻 建立一個有依賴的複合任務：

```bash
# 建立任務（含子任務依賴）
curl -X POST http://localhost:8000/api/admin/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "title": "產出日報",
    "subtasks": [
      {"id": "fetch", "skill": "news_scraper", "depends_on": []},
      {"id": "analyze", "skill": "llm_analyze", "depends_on": ["fetch"]},
      {"id": "render", "skill": "report_template", "depends_on": ["analyze"]}
    ]
  }'
```

💻 觀察任務狀態流轉：

```bash
# 查看任務列表與狀態
curl http://localhost:8000/api/admin/tasks
```

### 3.5 驗證

✅ 任務狀態流轉正確：

```
pending → assigned → running → completed
                        ↓
                      failed → retry
```

- `fetch` 先執行（無依賴）
- `analyze` 等 `fetch` 完成後才開始
- `render` 等 `analyze` 完成後才開始

### 3.6 打開程式碼看 A2A 背後邏輯（選讀）

> 💡 不只 curl API — 打開程式碼看「02 派工時 leader 背後在做的事」。

💻 打開 TaskGraph（任務依賴解析）：

```bash
# 找到核心檔案
cat src/coordinator/task_graph.py | head -60
```

**重點看：**
- `resolve_dependencies()` — 怎麼判斷哪些任務可以並行、哪些要等
- `topological_sort()` — 任務排序演算法（DAG）
- 這就是 02 Step 5 你派工時，leader 背後「拆解任務順序」的邏輯

💻 打開 Agent Discovery（自動配對）：

```bash
cat src/coordinator/discovery.py | head -60
```

**重點看：**
- `match_agent(task)` — 根據 capabilities 標籤匹配最適 Agent
- `score_match()` — 匹配分數計算
- 這就是「leader 怎麼決定派給 market-agent 而不是 coder-agent」

💻 看一個真實的派工流程：

```bash
# 查看審計日誌，找最近一次任務派工
curl -s http://localhost:8000/api/admin/audit | python3 -m json.tool | head -30
```

對照程式碼，你可以追蹤：
1. 需求進入 → `src/gateway/` 接收
2. 意圖分析 → `src/coordinator/` 拆解
3. Agent 匹配 → `discovery.py` 配對
4. 任務執行 → `src/runtime/` 啟動 kiro-cli
5. 結果回報 → event → 通知

> 📌 **01 的 planner.py 只做第 2 步（意圖路由）；02 的 coordinator/ 做了 2-4 步。**
> 這就是「單兵升級為團隊」在程式碼層面的體現。

---

## Step 4：四層架構理解

### 4.1 架構全貌

```
┌─────────────────────────────────────────────────────┐
│                   入口層 (Gateway)                    │
│         Telegram │ Web Chat │ REST API │ CLI         │
├─────────────────────────────────────────────────────┤
│                  協調層 (Coordinator)                  │
│      TaskGraph │ A2A Discovery │ LLM Router          │
├─────────────────────────────────────────────────────┤
│                  執行層 (Runtime)                      │
│    Agent Skills │ Workflow Engine │ Schedule Engine    │
├─────────────────────────────────────────────────────┤
│                  知識層 (Knowledge)                    │
│       Wiki │ Memory │ Session │ FTS5 Search          │
└─────────────────────────────────────────────────────┘
```

### 4.2 對應程式碼結構

| 層級 | 目錄 | 職責 |
|------|------|------|
| **入口層** | `src/bot/`、`src/server/api/`、`apps/web/` | 接收使用者輸入，路由到協調層 |
| **協調層** | `src/coordinator/`、`src/llm/` | 任務拆解、Agent 匹配、LLM 路由 |
| **執行層** | `src/skills/`、`src/workflow/`、`src/scheduler/` | 實際執行 Skill、工作流、排程 |
| **知識層** | `knowledge/`、`src/conversation/`、`data/` | 知識庫、對話記憶、持久化 |

### 4.3 請求生命週期

以「幫我查今天的新遊戲」為例：

```
1. [入口層] Telegram Bot 收到訊息
2. [入口層] handlers.py → 判斷為自然語言
3. [協調層] ConversationPlanner.parse_intent() → "query_general"
4. [協調層] TaskGraph 建立單一任務
5. [協調層] Agent Discovery → 匹配 game_fetcher
6. [執行層] SkillRegistry.invoke("game_fetcher", params)
7. [知識層] MemorySearch 記錄對話
8. [入口層] 格式化結果 → 回傳 Telegram
```

### 4.4 驗證

✅ 對照自己的 `my-team` 專案目錄，確認四層結構存在且職責明確。

---

## 常見問題

### Port 被佔用

```bash
# 找到佔用 port 的 process
lsof -i :8000
# 或直接換 port
uvicorn src.server.main:app --reload --port 8001
```

### CORS 錯誤

Web Dashboard 連不到 Backend 時，確認 `src/server/main.py` 有加入 CORS middleware：

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### npm install 失敗

```bash
# 清除快取重試
rm -rf node_modules package-lock.json
npm cache clean --force
npm install

# 若 node 版本不對
node --version  # 需要 20+
```

### Backend 啟動報錯 ModuleNotFoundError

```bash
# 確認在專案根目錄
cd my-team
pip install -r requirements.txt
```

---

## 本課重點回顧

| 主題 | 學到什麼 |
|------|---------|
| Backend API | 21 個端點分 8 大類，RESTful 設計 |
| Web Dashboard | 前後端分離，Next.js + FastAPI |
| A2A 協作 | TaskGraph 依賴圖 + Agent Discovery 自動派工 |
| 四層架構 | 入口 → 協調 → 執行 → 知識，職責分明 |
| 運維管理 | 費用追蹤、排程管理、Agent 狀態監控 |

---

## 下一步

恭喜完成全部五堂課！你已擁有完整 AI Agent 生態系的建構和管理能力。
