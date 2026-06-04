# 🚀 Agent Team Workshop — 快速上手指南

> 用 AI 團隊協作開發，50 分鐘建立你的第一支 Agent 艦隊。

**作者：** paddyyang  
**更新：** 2026-05-27

---

## 🎯 上課目標（50 分鐘）

### 時間分配

| 時間 | 動作 | 你做什麼 | Script 做什麼 |
|------|------|---------|-------------|
| 0-10 min | 環境確認 | clone skills + `kiro-cli --version` | ark-env-doctor 自動檢查 |
| 10-20 min | 建團隊 | 執行 `build_team.py` | 一次產出完整可運作專案 |
| 20-30 min | 配角色 | 執行 `build_kiro.py` | 批次產出所有 agent .kiro/ |
| 30-40 min | 設定 TG | `pip install -r requirements.txt` + 填 .env + 建 Group + 加 Bot | （唯一手動步驟） |
| 40-45 min | 啟動 | 雙擊 `start-team.bat` | daemon 自動啟動全部 agents |
| 45-50 min | 派工 | TG 發一句話給 leader | leader 自動拆解 + 派工給 workers |

### 完成度分級

```
🏆 快速組（50 min 內全完成）
   → 跨 agent 派工成功（leader 委派任務給 dev）

✅ 標準組（大多數人）
   → 團隊啟動 + Telegram 能收到 agent 回覆

🎯 保底組（至少完成這個）
   → team.yaml 產出 + 目錄結構正確（validate 通過）
```

### 回家自我練習

課堂上跳過的部分，回家照 `agent-team-build-guide.md` 完成：

- 自訂角色（改 SOUL.md 八段式定義）
- 新增 agent（加 instance + 重跑 build_kiro.py）
- 加入 Skills（ark-project-planning、ark-wiki-engine）
- Docker 部署、排程自動化

---

## 你需要準備的東西

| 項目 | 說明 |
|------|------|
| 電腦 | Windows / Mac / Linux |
| Kiro IDE | https://kiro.dev |
| Python 3.11+ | https://python.org |
| Git | https://git-scm.com |
| Telegram 帳號 | 建立 Bot + Group 用 |
| Telegram Bot Token | @BotFather 取得 |

---

## Step 0：環境安裝

### 確認工具已安裝

```bash
kiro-cli --version
python --version      # 3.11+
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

## Step 1：建立完整專案骨架

### Script 直接產出（推薦）

```bash
# 產出完整專案（含 start.py + ark_team_core/ + 業務層）
python .kiro/skills/ark-agent-team-builder/scripts/build_team.py my-team

# 驗證結構
python .kiro/skills/ark-agent-team-builder/scripts/build_team.py --validate my-team
```

### AI 觸發（自動呼叫 script）

在 Kiro 聊天框輸入：

```
建立 5 人 AI 團隊，角色：admin + leader + ai-dev + coder + qa
```

---

## Step 2：配置所有 Agent 的 .kiro/

### Script 批次產出（推薦）

```bash
# 批次產出所有 agent 的 .kiro/（一次完成）
python .kiro/skills/ark-kiro-init/scripts/build_kiro.py my-team/team.yaml my-team

# clone 共用 Skills 倉庫
python .kiro/skills/ark-kiro-init/scripts/build_kiro.py --clone-skills my-team

# 驗證
python .kiro/skills/ark-kiro-init/scripts/build_kiro.py --validate my-team
```

### AI 觸發

在 Kiro 聊天框輸入：

```
為所有 agent 配置 .kiro/，讀取 my-team/team.yaml
```

---

## Step 3：設定 Telegram（唯一手動步驟）

### 安裝依賴

```bash
cd my-team
pip install -r requirements.txt
```

### 建立 Bot

1. Telegram 找 `@BotFather` → `/newbot` → 取得 token

### 建立 .env

```bash
cp .env.example .env
# 填入 TELEGRAM_BOT_TOKEN=你的token
```

### 取得 Group ID（Group Topics 模式）

```bash
curl "https://api.telegram.org/bot你的TOKEN/getUpdates" | python -m json.tool
```

找到 `chat.id`（group_id）和 `message_thread_id`（topic_id），填入 team.yaml。

### 純私聊模式（個人使用，不需建 Group）

team.yaml 不設 `group_id`，用 @mention 指定 agent：

```
@leader 規劃一個 Todo App
@coder 建立 Express API
```

---

## Step 4：啟動團隊

### Windows

```bash
start-team.bat
```

### Mac / Linux

```bash
bash start-team.sh
```

### 驗證啟動

```bash
curl http://127.0.0.1:13030/api/status
```

---

## Step 5：實戰派工

### Telegram 派工

在 leader 的 Topic 或私聊發送：

```
@leader 規劃一個 Todo App，拆解任務分派給團隊
```

Leader 會自動：
1. 釐清需求
2. 撰寫規格
3. 拆解任務
4. 用 `delegate_task` 分派給 dev / qa

### HTTP API 派工

```bash
curl -X POST http://127.0.0.1:13030/api/send \
  -H "Content-Type: application/json" \
  -d '{"instance": "coder-agent", "message": "建立 Express.js REST API"}'

curl http://127.0.0.1:13030/api/status
```

---

## 常見問題

### Q：Telegram Bot 沒回應？

- 確認 Bot 在群組裡且是 Admin
- 確認 `.env` 的 `TELEGRAM_BOT_TOKEN` 正確
- 確認 `team.yaml` 的 `group_id` 和 `topic_id` 正確

### Q：Agent 啟動超時？

```bash
# 查看日誌
cat logs/team.log
```

確認 `working_directory` 路徑存在，kiro-cli 可正常執行。

### Q：想用 HTTP API 不用 Telegram？

team.yaml 不設 `channel` 區塊，透過 HTTP API 操作：

```bash
curl -X POST http://127.0.0.1:13030/api/send \
  -d '{"instance": "dev-agent", "message": "你的任務"}'
```

### Q：費用會很高嗎？

預設有 `cost_guard.daily_limit_usd`，到上限自動暫停。
建議先設低（$5-10），觀察用量再調整。

### Q：如何重啟服務？

```bash
# 寫入重啟旗標 → watchdog 自動拉起（3 秒後）
echo "" > restart.flag
```

---

## 教材包檔案說明

```
agent-team-workshop/
├── QUICKSTART.md                ← 本文件（快速上手）
├── quickstart.html              ← HTML 版快速指南
├── agent-team-build-guide.md    ← 完整教學（5 步驟）
├── team.example.yaml            ← team.yaml 範例
├── .env.example                 ← 環境變數範本
└── troubleshooting.md           ← 故障排除
```

---

*作者：paddyyang ｜ 更新：2026-05-27*
