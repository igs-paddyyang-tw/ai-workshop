# ai-team-agent — 🔄 AI Agent 團隊平台

> `ark_team_agent` **套件消費端**：8 個 agent 的常駐 daemon + A2A 派工 + 排程 +
> 費控 + 看板。框架在 wheel 裡，這個資料夾只有**設定與人格**。

---

## 這裡面沒有 runtime —— 那是刻意的

| 你在別處看過的 | 在這裡 |
|---|---|
| `src/runtime/`（daemon / 進程管理） | 在 `ark_team_agent` 套件裡 |
| `src/coordinator/`（A2A / EventBus / TaskLifecycle） | 同上 |
| `src/gateway/`（TG + REST 21 端點） | 同上 |
| `apps/web/`（Next.js Dashboard） | 套件內建 website（`health_port + 5000`） |
| 你要維護的 | **`team.yaml`**、`scheduler.yaml`、各 agent 的 `SOUL.md` |

**`team.yaml` 就是架構。** 第四堂讀的六個區塊：
`instances` · `group` · `access` · `cost_guard` · `hang_detector` · `kiro_files`。

---

## 快速啟動

```bash
# 1. 建環境
python3 -m venv .venv && source .venv/bin/activate

# 2. 裝 wheel（從 Release 下載後放本目錄）
#    github.com/igs-paddyyang-tw/ark_team_agent/releases
pip install './ark_team_agent-<版本>-py3-none-any.whl'

# 3. 驗版號 —— 🔴 看 import，不看 pip 輸出
python -c "import ark_team_agent; print(ark_team_agent.__version__)"

# 4. 裝各 agent 的專業技能（三層分工的第三層）
python3 scripts/sync_skills.py

# 5. 填機密與權限
cp .env.example .env          # TELEGRAM_BOT_TOKEN
#   team.yaml 的 access.allowed_users 填你自己的 TG user_id

# 6. 跑
python start.py
```

---

## 🔴 啟動就緒分兩階段 —— 「送了沒回」通常不是故障

| 階段 | 要多久 | 怎麼確認 |
|---|---|---|
| ① daemon + TG | 約 20 秒 | `curl localhost:23050/api/health` 回 200、log 出現 `Application started` |
| ② kiro-cli backend 冷啟 | **首次 2–4 分鐘** | 它要 spawn team MCP、握手、印就緒訊號 `All tools are now trusted` |

**第一階段完成不代表私訊會回。** 訊息會先進佇列（log 有 `Queued message`），
等第二階段就緒才被處理（`Delivered message`）。

送了沒回先查這個，再懷疑壞掉：

```bash
cat /proc/<kiro-cli pid>/stat     # CPU 時間有沒有在動
```

---

## 目錄結構

```
ai-team-agent/
├── start.py              asyncio.run(run_team(team.yaml))
├── team.yaml             🏗️ 團隊設定（唯一集中點）＝ 架構本身
├── scheduler.yaml        ⏰ 排程（第五堂）
├── .env                  🔑 機密（不進版控）
├── scripts/sync_skills.py  🛠️ 角色 × skill 矩陣同步
├── .kiro/steering/       🧠 全域規範（TEAM.md 由 daemon 每次啟動重產，手改會被覆寫）
├── agents/<name>-agent/  各 instance 的 working_directory
│   ├── .kiro/steering/   人格（SOUL.md）
│   ├── .kiro/skills/     專業技能（sync 產生，**不進版控**）
│   ├── knowledge/        私有知識
│   └── memory/           私有記憶
├── knowledge/shared/     📚 團隊共用知識庫（wiki / raw / schema / index / log）
├── memory/               🧠 團隊記憶
├── artifacts/reports/    📄 產出落點
└── docs/                 📝 課堂產出的 spec / design / plan
```

---

## 端點

| 用途 | URL |
|---|---|
| 健康檢查 | `http://localhost:23050/api/health` 🔴 是 `/api/health`，`/health` 回 404 |
| 狀態 | `http://localhost:23050/api/status` |
| 看板（給人看） | `http://localhost:28050`（= `health_port + 5000`，套件內建） |

---

## 編制（8 agent）

| | 角色 | group | 能改 code |
|---|---|---|---|
| 👑 | admin-agent（預設入口、維運） | — | ✅ 限維運面 |
| 🧠 | leader-agent（拆解、派工、驗收） | — | ❌ |
| 🤖 | ai-dev-agent（Prompt / RAG / MCP） | leader-agent | ✅ 限 AI 層 |
| 💻 | coder-agent（業務邏輯） | leader-agent | ✅✅ 唯一寫手 |
| 🧪 | qa-agent（測試 / 反證） | leader-agent | ✅ 限測試 |
| 🗺️📊📝 | market / data / report | leader-agent | ❌ 只讀不寫 |

> 🔴 worker 用 **`group: leader-agent`** 指向所屬 leader ——
> **不是** bot 端 `agents.yaml` 的 `group_members`。寫錯套件會**靜默忽略**：
> log 只印一行「欄位不存在 → 已忽略」，派工歸屬不生效。
> 這是「設定看起來生效了其實沒有」最典型的一種。

想跑精簡編制（營運 5 人 / 研發 5 人）→ 把 `team.yaml` 裡不需要的 instance 整段註解掉。

---

## 常見狀況

| 現象 | 不是故障，是 | 怎麼確認 |
|---|---|---|
| 私訊送了沒回 | kiro-cli 首次冷啟（2–4 分鐘） | 看 CPU 時間 + 就緒訊號 |
| `/health` 回 404 | team 套件的端點是 `/api/health` | `curl .../api/health` |
| `authority-matrix.yml not found` | 決策鎖是選配 | 非致命，可忽略 |
| 各 agent 的 skill 又變回預設 | `kiro_files.skills.policy` 不是 `skip` | 看 `team.yaml` |
| 派工不照 group 走 | 寫成 `group_members`（bot 端寫法） | 看啟動 log 的「欄位不存在」 |
| 看板打不開 | website 在 `health_port + 5000` | `curl localhost:28050` |

---

## 上一步

還沒做過單 bot？→ `../ai-bot/`（`ark_bot_agent` 消費端）
