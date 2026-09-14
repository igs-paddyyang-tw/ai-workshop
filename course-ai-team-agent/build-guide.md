---
title: "課程 B — AI Agent Team 建置完整指南"
type: guide
created: 2026-07-02
language: zh-TW
---

# 課程 B — AI Agent Team 建置完整指南

> 一個平台，兩堂課（Phase 1-2），Step 0-8。
> 從個體升級為「5 Agent 並行 + 營運落地」的完整團隊。

**操作位置圖示：**
- 📝 = AI IDE 聊天框（Kiro CLI）
- 📱 = Telegram Bot 對話
- 💻 = 終端機

---

## ✅ 先體驗成品？

```bash
cd ai-workshop/samples/ai-team-agent
python3 -m venv .venv && source .venv/bin/activate
pip install './ark_team_agent-<版本>-py3-none-any.whl'
python3 scripts/sync_skills.py          # 裝各 agent 的專業技能
cp .env.example .env                    # 填你自己的 TELEGRAM_BOT_TOKEN
python start.py
```

| Phase | sample 中對應 |
|-------|-------------|
| 1 Team | `team.yaml`（instances / group / access）+ `agents/` |
| 2 管理 | `team.yaml`（cost_guard / hang_detector）+ `scheduler.yaml` + 內建 website |

> 🔴 **這個專案裡沒有 runtime 程式碼。** daemon / A2A / Kanban / REST / 排程
> 都在 `ark_team_agent` wheel 裡。**`team.yaml` 就是架構。**

---

## 從課程 A 到課程 B

| 課程 A 你有的 | 課程 B 升級為 |
|-------------|-------------|
| 1 個 bot 進程、9 個 agent 定義 | 8 個 agent **各自一個常駐進程** |
| `agents.yaml` 的 `group_members` | `team.yaml` 的 `group`（worker 指向所屬 leader） |
| 模式切換（chat / agent / team） | 排程驅動 + A2A 派工（配置定義迴圈） |
| 單一知識庫 | 每 agent 私有 knowledge + 團隊共用櫃 |
| 你自己開著終端 | systemd user service 常駐 |
| `/health` | `/api/health` + 內建看板 + 費控 + 卡死偵測 |

> 🔴 **兩邊的套件不同**：課程 A 是 `ark_bot_agent`（單 bot 入口），
> 課程 B 是 `ark_team_agent`（多 agent daemon）。**agent 的人格資產可以直接搬**
> —— `.kiro/steering/SOUL.md` 兩邊同形狀。

---

## 建置步驟總覽

```
── Phase 1：Agent Team 建構（第四堂）─────────────
Step 0: 環境準備
Step 1: 裝 ark_team_agent wheel（ark-agent-team-builder 產骨架）
Step 2: ark-agent-init 補人格 → sync_skills.py 裝專業技能
Step 3: 設定 Telegram + .env + allowed_users
Step 4: 啟動團隊（🔴 兩階段就緒）+ 實戰派工

── Phase 2：營運落地（第五堂）─────────────────
Step 5: 排程設定（scheduler.yaml）
Step 6: 費用控管（cost_guard）
Step 7: 觸發排程 + 迴圈體驗（產出→raw→ingest→Wiki→引用）
Step 8: 上線 Checklist + ingest 排程自動化
```

| Phase | 核心 Skill | 學什麼 |
|-------|-----------|--------|
| 1 | `ark-agent-team-builder` + `ark-agent-init` + `sync_skills.py` | 團隊建構 + 派工 |
| 2 | （續用 Phase 1 產出） | 設定即架構 + 運維管理 |

> 💡 **三層分工**：① `ark-agent-team-builder` 定架構 → ② `ark-agent-init` 給人格
> → ③ `sync_skills.py` 給工具。順序不能反 —— 先有誰在團隊，才談他是誰、他會什麼。

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

## Step 1：產骨架 + 裝套件（ark-agent-team-builder）

📝 Kiro IDE 輸入：

```
用 ark-agent-team-builder 幫我建一個團隊：my-team
```

產出的是**設定骨架**，不是平台：
```
my-team/
├── start.py                 ← asyncio.run(run_team(team.yaml))
├── team.yaml                ← 🏗️ 團隊設定（唯一集中點）＝ 架構本身
├── scheduler.yaml           ← 排程任務定義
├── .env                     ← 機密
├── requirements.txt         ← 只列 wheel
├── knowledge/shared/{wiki,raw}/   ← 團隊共用知識庫
├── agents/<name>-agent/     ← 各 instance 的 working_directory
└── scripts/sync_skills.py   ← 角色 × skill 矩陣
```

💻 裝套件：

```bash
cd my-team
python3 -m venv .venv && source .venv/bin/activate
pip install './ark_team_agent-<版本>-py3-none-any.whl'
python -c "import ark_team_agent; print(ark_team_agent.__version__)"   # 驗版號
```

> 🔴 驗 import 版號，**不看 pip 輸出**。若你在 `pyproject.toml` 釘了版號，
> 升級時要同步改 pin。

## Step 2：補人格（ark-agent-init）+ 裝技能（sync_skills）

📝 Kiro IDE 輸入：

```
用 ark-agent-init 為 my-team 的每個 agent 產 .kiro/steering 人格
```

💻 裝各 agent 的專業技能：

```bash
python3 scripts/sync_skills.py            # 依角色矩陣同步
python3 scripts/sync_skills.py --check    # 驗一致（rc=0 才算過）
```

每個 Agent 得到：人格（SOUL/AGENTS/CODE/MEMORY/USER）+ 專業 skill + 私有知識庫。

> 🔴 **`team.yaml` 的 `kiro_files.skills.policy` 必須是 `skip`** ——
> 否則套件每次啟動都會把內建 skill 鋪回去，**推翻你剛才定的角色矩陣**。
> 這是「設定看起來生效了，下次啟動就沒了」的典型。

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

確認第一階段（約 20 秒）：
```bash
curl -s localhost:23050/api/health
# {"ok":true,"version":"1.8.x","instances":{"running":2,"alive":2,...},
#  "website":{"port":28050,...}}
```

> 🔴 **啟動就緒分兩階段，第一階段完成不代表私訊會回。**
>
> | 階段 | 多久 | 怎麼確認 |
> |---|---|---|
> | ① daemon + TG | 約 20 秒 | `/api/health` 回 200、log 有 `Application started` |
> | ② kiro-cli backend 冷啟 | **首次 2–4 分鐘** | 它要 spawn team MCP、握手、印 `All tools are now trusted` |
>
> 訊息會先進佇列（log 有 `Queued message`），第二階段就緒後才處理（`Delivered message`）。
> **「送了沒回」先查 kiro-cli 的 CPU 時間有沒有在動**（`cat /proc/<pid>/stat`），
> 再懷疑壞掉 —— 冷啟未完成不是故障。

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

# Phase 2：營運落地（第五堂）

> 目標：理解架構 + 掌控全平台（API + Dashboard + 費用 + 監控）。

## Step 5：Backend API 探索

💻 啟動 Server（如果還沒啟動）：
```bash
python start.py
```

測試核心端點（port 來自 `team.yaml` 的 `health_port`）：
```bash
curl -s localhost:23050/api/health      # 🔴 是 /api/health，/health 回 404
curl -s localhost:23050/api/status
curl -s localhost:23050/api/instances
curl -s localhost:23050/api/costs
curl -s localhost:23050/api/events/summary
```

### 端點分類（全部由套件提供）

| 分類 | 範例 |
|------|------|
| 健康 / 狀態 | `/api/health` · `/api/status` |
| 實例 | `/api/instances` · `/api/instances/{name}/restart` |
| 費用 | `/api/costs` · `/api/costs/spend` |
| 事件 | `/api/events` · `/api/events/summary` |
| 派工 | `/api/v1/agents` · `/api/v1/dispatch` |
| 產出 / 文件 | `/api/output/{name}` · `/api/docs/list` |
| 運維 | `/api/reload` · `/api/restart-service` · `/api/log` |

> 💡 這些端點**不在你的專案裡** —— 改 port 只需改 `team.yaml`，不用碰任何程式碼。

## Step 6：Web Dashboard

💻 **不用建置任何前端** —— 套件內建看板，跟著 daemon 一起起來：

```bash
# website port = health_port + 5000
open http://localhost:28050        # 或瀏覽器直接輸入
```

`/api/health` 回應裡就寫著它在哪：
```json
"website": {"port": 28050, "source": "builtin",
            "note": "dashboard 前端在此 port；本 API port 只有 /api/*"}
```

> 💡 舊版課程要 `npm install` 一套 Next.js Dashboard —— 那是手搭時代的產物，
> 現在套件內建。少一個技術棧，也少一個課堂卡點。

## Step 7：設定即架構 —— `team.yaml` 六區塊導讀 ⭐

套件化之後，架構不在你的專案裡（它在 wheel 裡），**但架構的「決定」全在 `team.yaml`**。
這一節逐區塊看，每個區塊對應一個架構概念。

### ① `instances` + `role` — 誰在團隊、什麼位階

```yaml
instances:
  admin-agent:   { working_directory: agents/admin-agent, role: admin }
  leader-agent:  { working_directory: agents/leader-agent, role: leader }
  coder-agent:   { working_directory: agents/coder-agent, role: worker, persistent: false }
```

- `role` 決定它在派工鏈的位置（manager / leader / admin / worker）
- `persistent: false` = **lazy spawn**（有需求才啟動，省資源）
- `working_directory` 決定它讀哪份 `.kiro/steering/SOUL.md`

### ② `group` — 派工歸屬 🔴 最容易寫錯的一個

```yaml
  coder-agent:
    role: worker
    group: leader-agent      # ← 指向所屬 leader
```

> 🔴 **team 端是 `group`，bot 端（課程 A 的 `agents.yaml`）是 `group_members`。**
> 寫錯的話套件**靜默忽略**，只在 log 印一行
> 「欄位 'group_members' 不存在 → 已忽略。你是不是想寫 'group'？」，
> 而派工歸屬不生效。
>
> 💡 **這是本課最值得帶走的一課**：設定類系統最危險的失敗不是報錯，
> 是「看起來生效了其實沒有」。改完設定要去 log 找證據。

### ③ `access` — 誰能指揮

```yaml
access:
  mode: locked              # locked | group | open
  allowed_users: [你的TG_user_id]
```
沒填 `allowed_users` = 誰都指揮不動（包括你）。

### ④ `cost_guard` — 費用護欄（第五堂細談）
### ⑤ `hang_detector` — 卡死偵測與升級
### ⑥ `kiro_files` — skill 與 steering 的覆寫政策

```yaml
kiro_files:
  skills:   { policy: skip }        # 🔴 不設 → 每次啟動推翻角色矩陣
  steering: { team_md: always, soul_md: once }
```

- `team_md: always` — 成員表以 `team.yaml` 為唯一真相，每次啟動重產
- `soul_md: once` — **你手寫的人格不會被覆蓋**（存在就跳過）

📝 IDE 實驗：
```
把 coder-agent 的 group 改掉，重啟，看 log 有沒有出現「欄位不存在」的警告
```

### 請求生命週期（全部在套件裡）

```
使用者發訊 → TG channel → 依 access 檢查 → 依 role/group 決定誰接
    → daemon spawn/喚醒 kiro-cli instance → agent 執行
    → 事件回報 → TG 回覆 + 看板更新
```

## Step 8：費用 + 排程 + 監控

### 費用追蹤

```bash
curl -s localhost:23050/api/costs
# → 今日花費、日限額、各 agent 明細
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
curl -s localhost:23050/api/status
```

### 健康監控

```bash
curl -s localhost:23050/api/health
# → ok / instances.running / instances.alive / heartbeat_stale
```

`team.yaml` 中的 hang_detector：
```yaml
hang_detector:
  enabled: true
  timeout_minutes: 60
```

> 🎉 Phase 2 完成！排程 + 費控 + 知識累積 = 自動運作的 AI 團隊。

---

# 完成！你的平台具備

| 能力 | 來自 Phase | **你改哪裡**（能力本身在套件裡） |
|------|-----------|---------|
| 8 Agent 並行 | 1 | `team.yaml` 的 `instances` |
| 派工歸屬 | 1 | `team.yaml` 的 `group` |
| 誰能指揮 | 1 | `team.yaml` 的 `access` |
| 每個 agent 是誰 | 1 | `agents/*/.kiro/steering/SOUL.md` |
| 每個 agent 會什麼 | 1 | `scripts/sync_skills.py` 的矩陣 |
| 費用控管 | 2 | `team.yaml` 的 `cost_guard` |
| 卡死偵測 | 2 | `team.yaml` 的 `hang_detector` |
| 排程自動化 | 2 | `scheduler.yaml` |
| 看板 / 健康監控 | 2 | 內建（`health_port + 5000` / `/api/health`） |
| 常駐部署 | 2 | systemd user service |

## 團隊配置選擇

想跑精簡編制，**把 `team.yaml` 裡不需要的 instance 整段註解掉**：

```yaml
# 營運 5 人：admin + leader + market + data + report
# 研發 5 人：admin + leader + ai-dev + coder + qa
```

> 💡 舊版用三份 yaml 互相複製（`cp team-ops.yaml team.yaml`），
> 結果是三份各自演化、對不上。**一份設定 + 註解**才有單一真相。

## 常駐部署（systemd user service）

課堂上你開著終端跑；要真的常駐，用 systemd user service：

```bash
# ~/.config/systemd/user/my-team.service
[Unit]
Description=my-team (ark_team_agent)
[Service]
Type=simple
WorkingDirectory=%h/my-team
ExecStart=%h/my-team/.venv/bin/python start.py
Restart=on-failure
[Install]
WantedBy=default.target
```

```bash
systemctl --user daemon-reload
systemctl --user enable --now my-team
systemctl --user status my-team
journalctl --user -u my-team -n 50 --no-pager
```

> 💡 要容器化改用 `ark-docker-deploy` skill 產 Dockerfile —— 不在本課範圍。

---

## 技術棧

| 能力 | 在哪 | 你要碰嗎 |
|------|------|---------|
| daemon + 進程管理 + watchdog | `ark_team_agent` | ❌ |
| A2A 派工 + 任務生命週期 | `ark_team_agent` | ❌ |
| TG Bot + REST API + 看板 website | `ark_team_agent` | ❌ |
| 費控 / 稽核 / 健康監控 | `ark_team_agent` | 只在 `team.yaml` 設門檻 |
| 排程 autopilot | `ark_team_agent` | 只寫 `scheduler.yaml` |
| **誰在團隊、什麼角色、派工歸屬** | `team.yaml` | ✅✅ 本課重點 |
| **何時自動做什麼** | `scheduler.yaml` | ✅ |
| **每個 agent 是誰** | `agents/*/.kiro/steering/SOUL.md` | ✅ |
| **每個 agent 會什麼** | `scripts/sync_skills.py` 的矩陣 | ✅ |

---

## 快速複製

```bash
# ① 在 Kiro 說「用 ark-agent-team-builder 建 my-team」
# ② 裝套件
cd my-team
python3 -m venv .venv && source .venv/bin/activate
pip install './ark_team_agent-<版本>-py3-none-any.whl'
# ③ 在 Kiro 說「用 ark-agent-init 產 my-team 各 agent 的 steering 人格」
# ④ 裝專業技能
python3 scripts/sync_skills.py

# 設定 + 啟動
cp .env.example .env       # 填你自己的 TELEGRAM_BOT_TOKEN
#   team.yaml 的 access.allowed_users 填你的 TG user_id
python start.py
```

> ⏱️ 首次啟動要**兩階段**：daemon + TG 約 20 秒，kiro-cli backend 冷啟 **2–4 分鐘**。
> 第一階段完成不代表私訊會回。

---

*一個平台，兩堂課，完整的 Agent Team。*
