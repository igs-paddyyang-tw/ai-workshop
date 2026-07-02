---
title: "課程 B — AI Agent Team 建置完整指南"
type: guide
created: 2026-07-02
language: zh-TW
---

# 課程 B — AI Agent Team 建置完整指南

> 一個平台，兩堂課（Phase 1-2），Step 0-8。
> 從個體升級為「5 Agent 並行 + 平台管理」的完整團隊。

**操作位置圖示：**
- 📝 = AI IDE 聊天框（Kiro CLI）
- 📱 = Telegram Bot 對話
- 💻 = 終端機

---

## ✅ 先體驗成品？

```bash
cd ai-workshop/sample/ai-team-agent
pip install -r requirements.txt && cp .env.example .env
cp team-ops.yaml team.yaml   # 營運團隊
python start.py
```

| Phase | sample 中對應 |
|-------|-------------|
| 1 Team | `src/runtime/` + `src/coordinator/` + `agents/` + `team.yaml` |
| 2 管理 | `src/gateway/api/` + `apps/web/` + `src/coordinator/services/` |

---

## 從課程 A 到課程 B

| 課程 A 你有的 | 課程 B 升級為 |
|-------------|-------------|
| 1 個 Agent | 5 個 Agent 並行 |
| Planner 路由 | TaskGraph 依賴圖 + 自動派工 |
| Session（per user） | A2A Protocol（Agent 間通訊） |
| memory.py 寫 raw/ | 每 Agent 獨立 knowledge/ + 共用 |
| python start.py | CoreDaemon 多進程 + watchdog |
| FastAPI health | 21+ 端點 + Dashboard |

---

## 建置步驟總覽

```
── Phase 1：Agent Team 建構（第四堂）─────────────
Step 0: 環境準備
Step 1: ark-agent-team-builder → 完整平台骨架
Step 2: ark-kiro-init → 批次產出所有 Agent .kiro/
Step 3: 設定 Telegram + .env
Step 4: 啟動團隊 + 實戰派工

── Phase 2：平台管理（第五堂）─────────────────
Step 5: Backend API 探索（21+ 端點）
Step 6: Web Dashboard
Step 7: A2A 協作 + TaskGraph 程式碼閱讀
Step 8: 費用追蹤 + 排程管理 + 監控
```

| Phase | 核心 Skill | 學什麼 |
|-------|-----------|--------|
| 1 | `ark-agent-team-builder` + `ark-kiro-init` | 團隊建構 + 派工 |
| 2 | （續用 Phase 1 產出） | 理解架構 + 運維管理 |

---

# Phase 1：Agent Team 建構（第四堂）

> 目標：5 Agent 並行運作，能透過 Telegram 派工。

## Step 0：環境準備

```bash
git clone https://github.com/igs-paddyyang-tw/ark-agent-skills .kiro/skills/
```

| 項目 | 最低需求 |
|------|---------|
| Python | 3.12+ |
| Kiro CLI | 2.7+（`kiro-cli login` 完成） |
| Git | 已安裝 |
| Telegram Bot Token | @BotFather 取得 |
| Node.js | 20+（Web Dashboard 需要） |

## Step 1：一鍵建構平台（ark-agent-team-builder）

💻 執行：

```bash
python3 .kiro/skills/ark-agent-team-builder/scripts/build_team.py my-team
```

產出 110+ 項：
```
my-team/
├── start.py                 ← 一鍵啟動全平台
├── team.yaml                ← 5 人團隊配置
├── scheduler.yaml           ← 排程任務定義
├── src/
│   ├── runtime/             ← CoreDaemon + Agent 進程管理
│   ├── coordinator/         ← A2A + EventBus + TaskLifecycle
│   ├── gateway/             ← Telegram + REST API
│   └── business/            ← 業務技能
├── agents/                  ← 5 個 Agent 工作目錄
├── apps/web/                ← Next.js Dashboard
├── Dockerfile + docker-compose
└── knowledge/               ← 共用知識庫
```

## Step 2：配置所有 Agent（ark-kiro-init）

💻 批次產出 .kiro/：

```bash
python3 .kiro/skills/ark-kiro-init/scripts/build_kiro.py my-team/team.yaml my-team
python3 .kiro/skills/ark-kiro-init/scripts/build_kiro.py --clone-skills my-team
python3 .kiro/skills/ark-kiro-init/scripts/build_kiro.py --validate my-team
```

每個 Agent 獲得完整配置（steering + skills + mcp.json + prompts）。

## Step 3：設定 Telegram

💻 唯一手動步驟：

```bash
cd my-team
pip install -r requirements.txt
cp .env.example .env
# 填入 TELEGRAM_BOT_TOKEN
```

取得 user_id：
```bash
# 先對 Bot 發一則訊息，然後：
curl -s "https://api.telegram.org/bot你的TOKEN/getUpdates" | python3 -m json.tool
# 找到 "from": {"id": 123456789}
```

填入 `team.yaml` 的 `allowed_users`。

## Step 4：啟動 + 派工

💻 啟動：
```bash
python start.py
```

看到：
```
✅ Ark Agent Platform 全部服務已啟動
├── Backend API :33333
├── 5 Agents ready
├── Telegram Bot 已啟動
└── Scheduler started
```

📱 Telegram 實測：

| 指令 | 功能 |
|------|------|
| `/start` | 歡迎訊息 |
| `/agents` | Agent 列表 |
| `/assign 描述` | 建立任務並派工 |
| `/board` | 看板摘要 |
| `/costs` | 費用報告 |

### 科技日報實戰

📱 輸入：
```
@leader 規劃科技日報：market 抓新聞、report 產出 HTML 日報
```

觀察：leader 拆任務 → market 爬蟲 → report 渲染 → TG 推送。

> 🎉 Phase 1 完成！5 Agent 並行運作。

---

# Phase 2：平台管理（第五堂）

> 目標：理解架構 + 掌控全平台（API + Dashboard + 費用 + 監控）。

## Step 5：Backend API 探索

💻 啟動 Server（如果還沒啟動）：
```bash
python start.py
```

測試核心端點：
```bash
curl http://localhost:33333/api/health
curl http://localhost:33333/api/agents
curl http://localhost:33333/api/admin/dashboard/stats
curl http://localhost:33333/api/admin/audit
curl http://localhost:33333/api/admin/costs
```

### 21+ 端點分類

| 分類 | 端點數 | 範例 |
|------|--------|------|
| Health | 1 | `GET /api/health` |
| Agents | 4 | CRUD |
| Tasks | 5 | CRUD + assign |
| Skills | 2 | list + invoke |
| Schedules | 3 | CRUD |
| Admin | 6 | dashboard/audit/costs/settings |
| WebSocket | 1 | 即時事件 |

## Step 6：Web Dashboard

💻 啟動：
```bash
cd apps/web && npm install && npm run dev
# http://localhost:3000
```

頁面：
| 頁面 | 功能 |
|------|------|
| Dashboard | KPI 卡片（Agent 數、任務數、成功率） |
| Agents | 列表 + 狀態燈 + 暫停/恢復 |
| Tasks | 任務追蹤 + 狀態流轉 |
| Costs | 費用統計 + 日限額 |
| Audit | 操作日誌時間軸 |
| Sessions | Agent 對話歷史 |

## Step 7：A2A 協作 + 程式碼閱讀

### TaskGraph（任務依賴）

💻 打開 `src/coordinator/a2a/graph.py`：
- `resolve_dependencies()` — 哪些任務可並行
- `topological_sort()` — DAG 排序

### Agent Discovery（能力匹配）

💻 打開 `src/coordinator/a2a/discovery.py`：
- `match_agent()` — 根據 capabilities 配對
- `score_match()` — 匹配分數計算

### A2A Protocol

💻 打開 `src/coordinator/a2a/protocol.py`：
- `delegate_task()` — Agent 委派任務給另一個 Agent
- `send_to_instance()` — 跨 Agent 通訊

### 請求生命週期

```
使用者發訊 → Gateway → TaskGraph 拆解
    → Discovery 匹配 → CoreDaemon spawn kiro-cli
    → Agent 執行 → EventBus 通知 → Gateway 回覆
```

## Step 8：費用 + 排程 + 監控

### 費用追蹤

```bash
curl http://localhost:33333/api/admin/costs
# → today_usd, daily_limit, breakdown by agent
```

設定在 `team.yaml`：
```yaml
cost_guard:
  daily_limit_usd: 15.0
  warn_at_percentage: 80
```

### 排程管理

查看 `scheduler.yaml`：
```yaml
jobs:
  - id: daily-news
    target: market-agent
    cron: "0 8 * * *"
    prompt: "抓取今日科技新聞..."
```

```bash
curl http://localhost:33333/api/admin/schedules
```

### 健康監控

```bash
curl http://localhost:33333/api/admin/dashboard/stats
# → agents_online, success_rate, avg_response_ms
```

`team.yaml` 中的 hang_detector：
```yaml
hang_detector:
  enabled: true
  timeout_minutes: 60
```

> 🎉 Phase 2 完成！你能掌控全平台。

---

# 完成！你的平台具備

| 能力 | 來自 Phase | 對應模組 |
|------|-----------|---------|
| 5 Agent 並行 | 1 | `src/runtime/daemon.py` |
| 自動派工 | 1 | `src/coordinator/a2a/` |
| 任務狀態機 | 1 | `src/coordinator/task_lifecycle.py` |
| Telegram 指揮 | 1 | `src/gateway/telegram/` |
| 21+ API 端點 | 2 | `src/gateway/api/` |
| Web Dashboard | 2 | `apps/web/` |
| 費用控管 | 2 | `src/coordinator/services/cost_tracker.py` |
| 排程自動化 | 2 | `scheduler.yaml` + `src/runtime/scheduler.py` |
| 健康監控 | 2 | `src/coordinator/services/health_monitor.py` |
| Docker 部署 | 2 | `docker-compose.prod.yml` |

## 團隊配置選擇

```bash
cp team-ops.yaml team.yaml    # 營運：admin + pm + market + data + report
cp team-dev.yaml team.yaml    # 研發：admin + pm + ai-dev + coder + qa
```

## Docker 部署

```bash
docker compose -f docker-compose.prod.yml up -d
```

---

## 技術棧

| 層 | 技術 |
|----|------|
| 執行 | CoreDaemon + kiro-cli subprocess |
| 協調 | A2A Protocol + EventBus + TaskLifecycle |
| 入口 | Telegram Bot + FastAPI 21+ 端點 |
| 服務 | cost_tracker + audit_logger + health_monitor |
| 前端 | Next.js + Tailwind + WebSocket |
| 部署 | Docker Compose + systemd + watchdog |

---

## 快速複製

```bash
# 一鍵完成
python3 .kiro/skills/ark-agent-team-builder/scripts/build_team.py my-team
python3 .kiro/skills/ark-kiro-init/scripts/build_kiro.py my-team/team.yaml my-team
python3 .kiro/skills/ark-kiro-init/scripts/build_kiro.py --clone-skills my-team

# 設定 + 啟動
cd my-team && cp .env.example .env
pip install -r requirements.txt
python start.py
```

---

*一個平台，兩堂課，完整的 Agent Team。*
