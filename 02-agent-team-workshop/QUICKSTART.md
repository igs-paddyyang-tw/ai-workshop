# 🚀 Agent Team Workshop — 快速上手指南

> 用 AI 團隊協作開發，50 分鐘建立你的第一支 Agent 艦隊。

**作者：** paddyyang
**更新：** 2026-06-17

---

## 🎯 上課目標（50 分鐘）

### 時間分配

| 時間 | 動作 | 你做什麼 | Script 做什麼 |
|------|------|---------|-------------|
| 0-10 min | 環境確認 | clone skills + `kiro-cli --version` | ark-env-doctor 自動檢查 |
| 10-20 min | 建團隊 | 執行 `build_team.py` | 一次產出完整平台（63 項） |
| 20-30 min | 配角色 | 執行 `build_kiro.py` | 批次產出所有 agent .kiro/ |
| 30-40 min | 設定 TG | venv + pip install + 填 .env + 對 Bot 發訊取 user_id | （唯一手動步驟） |
| 40-45 min | 啟動 | `python start.py` | 一鍵啟動 5 服務 |
| 45-50 min | 派工 | TG 發一句話給 leader | agent 執行 + TG 回覆 |

### 完成度分級

```
🏆 快速組（50 min 內全完成）
   → TG /assign 派工 → 收到 agent 回覆 + /costs 有費用記錄

✅ 標準組（大多數人）
   → 團隊啟動 + Telegram /start 收到歡迎訊息

🎯 保底組（至少完成這個）
   → team.yaml 產出 + 目錄結構正確（validate 通過）
```

### 回家自我練習

- 自訂角色（改 SOUL.md 八段式定義）
- 新增 agent（加 instance + 重跑 build_kiro.py）
- Web Dashboard（`cd apps/web && npm run dev`）
- Docker 部署（`docker compose -f docker-compose.prod.yml up`）

---

## 你需要準備的東西

| 項目 | 說明 |
|------|------|
| 電腦 | Windows / Mac / Linux |
| Kiro CLI | `kiro-cli --version`（2.7+） |
| Python 3.12+ | https://python.org |
| Git | https://git-scm.com |
| Telegram 帳號 | 建立 Bot 用 |
| Telegram Bot Token | @BotFather 取得 |

---

## Step 0：環境安裝

### 確認工具已安裝

```bash
kiro-cli --version    # 需要 2.7+
python3 --version     # 需要 3.12+
git --version
```

### 取得 Skills

```bash
git clone https://github.com/igs-paddyyang-tw/ark-kiro-skills .kiro/skills/
```

### 確認環境（選用）

在 Kiro 聊天框輸入：

```
檢查我的開發環境
```

---

## Step 1：建立完整專案

### Script 直接產出（推薦）

```bash
# 產出完整平台（63 項：Backend API + TG Bot + Agent Daemon + Docker）
python3 .kiro/skills/ark-agent-team-builder/scripts/build_team.py my-team

# 驗證結構
python3 .kiro/skills/ark-agent-team-builder/scripts/build_team.py --validate my-team
```

### 產出內容

```
my-team/
├── start.py               ← 一鍵啟動全平台
├── team.yaml              ← 5 人團隊配置
├── src/
│   ├── ark_team_core/     ← Agent Runtime（spawn kiro-cli）
│   ├── backend/           ← REST API（21 端點 + EventBus）
│   └── tg_ui/             ← Telegram Bot（11 指令）
├── agents/                ← 5 個 Agent 工作目錄
├── Dockerfile             ← 容器化部署
└── tests/test_api.py      ← 測試
```

### AI 觸發（自動呼叫 script）

在 Kiro 聊天框輸入：

```
建立 5 人 AI 團隊，角色：admin + leader + ai-dev + coder + qa
```

---

## Step 2：配置所有 Agent 的 .kiro/

```bash
# 批次產出所有 agent 的 .kiro/（一次完成）
python3 .kiro/skills/ark-kiro-init/scripts/build_kiro.py my-team/team.yaml my-team

# clone 共用 Skills
python3 .kiro/skills/ark-kiro-init/scripts/build_kiro.py --clone-skills my-team

# 驗證
python3 .kiro/skills/ark-kiro-init/scripts/build_kiro.py --validate my-team
```

---

## Step 3：設定 Telegram（唯一手動步驟）

### ⚠️ 重要：先建 venv

```bash
cd my-team
python3 -m venv .venv
source .venv/bin/activate    # Linux/Mac
# .venv\Scripts\activate     # Windows
pip install -r requirements.txt
```

> **為什麼需要 venv？** Ubuntu 22.04+ 啟用 PEP 668，直接 `pip install` 會被拒絕。

### 建立 Bot

1. Telegram 找 `@BotFather` → `/newbot`
2. 設定名稱 → 取得 **Bot Token**

### 建立 .env

```bash
cp .env.example .env
```

編輯 `.env`：
```
TELEGRAM_BOT_TOKEN=你的token
```

### 取得你的 User ID

1. **先對 Bot 私訊一則任意訊息**（如 "hello"）
2. 然後執行：

```bash
curl -s "https://api.telegram.org/bot你的TOKEN/getUpdates" | python3 -m json.tool
```

3. 找到 `"from": {"id": 123456789}` 的數字
4. 填入 `team.yaml` 的 `allowed_users` 和 `admin-agent` 的 `private_chat`

### 純私聊模式 vs Group Topics

| 模式 | 設定 | 用法 |
|------|------|------|
| 純私聊（推薦新手） | team.yaml 不設 `group_id` | 直接對 Bot 發訊 |
| Group Topics | 設定 `group_id` + `topic_id` | 每 agent 一個 topic |

---

## Step 4：啟動團隊

```bash
# 確保在 venv 中
source .venv/bin/activate

# 一鍵啟動全平台
python start.py
```

啟動後會看到：
```
✅ Ark Agent Platform 全部服務已啟動
├── Backend API :33333
├── 5 Agents ready
├── Telegram Bot 已啟動
├── Scheduler started
└── NotificationService 已訂閱 6 種事件
```

### 驗證啟動

```bash
curl http://127.0.0.1:33333/api/health
# → {"status": "ok"}

curl http://127.0.0.1:33333/api/agents
# → Agent 列表
```

### ⚠️ 常見問題

| 錯誤 | 原因 | 解法 |
|------|------|------|
| `Conflict: terminated by other getUpdates` | 多個 Bot instance | `pkill -f start.py` 只留一個 |
| `Address already in use :33333` | port 被佔 | `fuser -k 33333/tcp` |
| `No module named 'fastapi'` | 沒在 venv 中 | `source .venv/bin/activate` |

---

## Step 5：實戰派工

### Telegram 指令

| 指令 | 功能 |
|------|------|
| `/start` | 歡迎訊息 |
| `/status` | 團隊即時狀態 |
| `/agents` | Agent 列表 |
| `/assign 描述` | 建立任務並派工 |
| `/board` | 看板摘要 |
| `/costs` | 費用報告 |
| `/queue` | 待處理佇列 |

### 自然語言派工

直接對 Bot 發訊（自動路由到 leader）：
```
規劃一個 Todo App，拆解任務分派給團隊
```

指定 agent：
```
@coder 建立 Express.js REST API
```

### HTTP API 派工（不用 Telegram）

```bash
# 建立任務
curl -X POST http://127.0.0.1:33333/api/issues \
  -H "Content-Type: application/json" \
  -d '{"title": "建立 REST API", "assignee": "coder-agent"}'

# 查看狀態
curl http://127.0.0.1:33333/api/admin/dashboard/stats
```

---

## 進階功能

### Web Dashboard（回家做）

```bash
cd apps/web
npm install
npm run dev
# → http://localhost:3000/admin/dashboard
```

### Docker 部署

```bash
docker compose -f docker-compose.prod.yml up -d
```

### 費用追蹤

每次 Agent 執行自動記錄費用：
```bash
curl http://127.0.0.1:33333/api/admin/costs
```

### 審計日誌

所有操作自動記錄：
```bash
curl http://127.0.0.1:33333/api/admin/audit
```

---

## 團隊配置（team.yaml）

```yaml
instances:
  admin-agent:    ⚙️ 服務監控、重啟、成本控制
  pm-agent:       🧠 需求分析、派工、驗收（leader）
  ai-dev-agent:   🤖 AI 架構、Prompt 工程（worker）
  coder-agent:    💻 全端開發、API 實作（worker）
  qa-agent:       🧪 測試、品質保證（worker）
```

### 上下文壓縮建議

| Agent | 觸發點 | 理由 |
|-------|--------|------|
| pm-agent | 70% | 派工決策鏈珍貴，早壓縮保留摘要 |
| worker agents | 75% | 保留當前任務，完成的可丟 |
| admin-agent | 85% | 短指令為主 |

---

## 教材包檔案說明

```
agent-team-workshop/
├── QUICKSTART.md          ← 本文件（快速上手）
├── agent-team-build-guide.md ← 完整教學
├── team.example.yaml      ← team.yaml 範例
├── troubleshooting.md     ← 故障排除
└── structured-example.json
```

---

*作者：paddyyang ｜ 更新：2026-06-17*
