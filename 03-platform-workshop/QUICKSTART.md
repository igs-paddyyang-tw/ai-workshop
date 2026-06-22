# Workshop 03：Platform — 進階平台功能（50 分鐘）

> **前提**：已完成 Workshop 02，擁有運行中的 `my-team` 專案。
> 本次不需重新安裝，直接在現有專案上探索平台能力。

---

## 🎯 學習目標

| # | 主題 | 你會學到 |
|---|------|---------|
| 1 | Backend API | 21 個 REST 端點、curl 測試、管理面板 |
| 2 | Web Dashboard | Next.js 前端、即時狀態監控 |
| 3 | A2A 協作 | TaskGraph 依賴、Agent Discovery 自動匹配 |
| 4 | 四層架構 | 入口→協調→執行→知識 的設計哲學 |

---

## 📐 四層架構概念

在動手之前，理解平台的設計哲學：

```
┌─────────────────────────────────────────────┐
│ Layer 1：入口層（Entry）                      │
│   Telegram Bot / Web UI / REST API           │
├─────────────────────────────────────────────┤
│ Layer 2：協調層（Orchestration）              │
│   TaskGraph / A2A Discovery / 排程引擎       │
├─────────────────────────────────────────────┤
│ Layer 3：執行層（Execution）                  │
│   Agent Skills / LLM Adapters / Tools        │
├─────────────────────────────────────────────┤
│ Layer 4：知識層（Knowledge）                  │
│   Wiki Engine / Memory / Session / FTS5      │
└─────────────────────────────────────────────┘
```

- **入口層**：使用者從哪裡進來（TG、Web、API）
- **協調層**：決定「誰做什麼」（任務分配、依賴解析）
- **執行層**：真正做事的 Agent 和 Skill
- **知識層**：持久化記憶、搜尋、學習

本次 Workshop 聚焦 Layer 1（API + Web）和 Layer 2（A2A 協作）。

---

## 1️⃣ Backend API（20 分鐘）

### 確認服務啟動

```bash
cd my-team
source .venv/bin/activate
uvicorn src.server.main:app --reload --port 8000
```

### 21 個端點總覽

| 類別 | 端點範例 | 數量 |
|------|---------|------|
| Health | `/api/v1/health` | 1 |
| Skills | `/api/v1/skills`, `/api/v1/skills/invoke` | 2 |
| Chat | `/api/v1/chat` | 1 |
| Wiki | `/api/v1/wiki/query`, `ingest`, `lint` | 3 |
| Workflows | `/api/v1/workflows`, `run`, `status` | 3 |
| Schedules | `/api/v1/schedules`, `toggle` | 2 |
| Admin | `/api/admin/dashboard/stats`, `agents`, `tasks`, `audit`, `config` | 8 |
| Files | `/api/files` | 1 |

### 🔨 動手：curl 測試

```bash
# 系統狀態
curl -s http://localhost:8000/api/v1/health | python -m json.tool

# 管理面板統計（重點！）
curl -s http://localhost:8000/api/admin/dashboard/stats | python -m json.tool

# 查看已註冊的 Skills
curl -s http://localhost:8000/api/v1/skills | python -m json.tool

# 審計日誌
curl -s http://localhost:8000/api/admin/audit | python -m json.tool
```

✅ **檢查點**：`dashboard/stats` 回傳 JSON 含 `agents_online`、`tasks_today`、`skill_count`。

---

## 2️⃣ Web Dashboard（25 分鐘）

### 安裝與啟動前端

```bash
cd my-team/web          # 前端目錄
npm install             # 安裝依賴（首次約 30 秒）
npm run dev             # 啟動 dev server
```

開啟瀏覽器：**http://localhost:3000**

### Dashboard 功能

| 頁面 | 功能 |
|------|------|
| Overview | KPI 卡片 + 即時 Agent 狀態 |
| Agents | Agent 列表、能力標籤、在線狀態 |
| Tasks | 任務清單、狀態追蹤、依賴圖 |
| Audit | 操作審計日誌（誰在什麼時候做了什麼） |
| Settings | 系統設定、LLM 模型切換 |

### 🔨 動手：探索 Dashboard

1. Overview → 確認 KPI 數字與 curl 結果一致
2. Agents → 看到你的 Bot Agent 在線
3. Tasks → 目前應為空（等下會有任務）
4. Audit → 看到剛才的 API 呼叫記錄

✅ **檢查點**：Dashboard 正常顯示，無 CORS 錯誤。

---

## 3️⃣ A2A 協作（30 分鐘）

### 核心概念

**A2A（Agent-to-Agent）** 讓多個 Agent 自動協作：

```
使用者 /assign "分析上週數據並產出報表"
         │
         ▼
┌─ TaskGraph 拆解 ──────────────────┐
│  Task 1: 查詢數據（db_query）      │
│  Task 2: 分析趨勢（llm_analyze）   │  ← 依賴 Task 1
│  Task 3: 產出報表（report_template）│  ← 依賴 Task 2
└───────────────────────────────────┘
         │
         ▼
┌─ Discovery 匹配 ──────────────────┐
│  Task 1 → DataAgent（有 db 能力）  │
│  Task 2 → AnalystAgent（有 LLM）   │
│  Task 3 → ReportAgent（有模板）    │
└───────────────────────────────────┘
```

- **TaskGraph**：自動拆解複合任務，建立依賴關係
- **Discovery**：根據 Agent 能力標籤自動匹配最適合的執行者
- **依賴執行**：Task 2 等 Task 1 完成才啟動（DAG 拓撲排序）

### 🔨 動手：觸發 A2A 協作

在 Telegram Bot 中：

```
/assign 查詢今日 Skills 執行統計並產出摘要
```

觀察 Dashboard：Tasks 頁面出現新任務（含子任務），依序從 pending → running → completed，最終 Bot 回覆結果摘要。

### 驗證 A2A 路由

```bash
curl -s http://localhost:8000/api/admin/tasks | python -m json.tool
curl -s http://localhost:8000/api/admin/audit | python -m json.tool
```

✅ **檢查點**：Tasks API 回傳含 `subtasks` 陣列，每個 subtask 有 `assigned_agent`。

---

## 4️⃣ 整合驗證（15 分鐘）

### 端到端流程

```
TG /assign → API → TaskGraph 拆解 → Discovery 匹配 → Agent 執行 → Dashboard 更新 → TG 通知
```

### 🔨 最終動手

1. TG 發送：`/assign 列出所有 Skill 並統計各類別數量`
2. 同時觀察 Dashboard Tasks 頁面
3. 完成後：`curl -s http://localhost:8000/api/admin/audit?limit=20 | python -m json.tool`

---

## 🏆 完成度分級

| 等級 | 條件 |
|------|------|
| ⭐ 基礎 | curl 測試 API 成功、Dashboard 正常開啟 |
| ⭐⭐ 進階 | A2A 任務成功執行、Dashboard 即時更新 |
| ⭐⭐⭐ 精通 | 理解四層架構、能解釋 TaskGraph 拆解邏輯 |
| 🌟 超越 | 自訂 Agent 能力標籤、影響 Discovery 匹配結果 |

---

## ❓ 常見問題

### Node.js 版本不對

```bash
node --version  # 需要 v20+

# 使用 nvm 切換
nvm install 20
nvm use 20
```

### CORS 錯誤（Dashboard 無法呼叫 API）

確認 Backend 的 CORS 設定：

```python
# src/server/main.py 中應有
from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:3000"], ...)
```

如果沒有，加入後重啟 Backend。

### Port 衝突

```bash
# 檢查 port 佔用
lsof -i :8000  # Backend
lsof -i :3000  # Frontend

# 殺掉佔用的 process
kill -9 <PID>

# 或改用其他 port
uvicorn src.server.main:app --port 8001
PORT=3001 npm run dev
```

### Dashboard 顯示空白

確認 Backend 運行中 → 確認 `.env` 有 `NEXT_PUBLIC_API_URL=http://localhost:8000` → 清快取 `rm -rf web/.next && npm run dev`。

### A2A 任務沒有被拆解

簡單任務不會拆解；確認 `config/agents.yaml` 有正確能力標籤，且至少 Bot Agent 在線。

---

## ⏭️ 下一步

Workshop 03 完成！你已掌握 21 個 API 端點、Web Dashboard 監控、A2A 協作機制、四層架構哲學。

**進階探索**：自訂 Agent 能力標籤影響 Discovery、建立含條件分支的 TaskGraph、整合外部 API 資料來源。
