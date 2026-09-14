---
title: "AI Workshop v2 — 套件化翻新設計文件"
type: design
status: draft
created: 2026-09-14
language: zh-TW
spec: ../specs/workshop-v2-spec.md
---

# AI Workshop v2 — 套件化翻新設計文件

## 0. 設計主張

**教材的骨幹不是「架構解說」，是「三層分工」。**

舊教材把「架構長什麼樣」當主線（讀 `a2a/graph.py`、看四層目錄），
那在手搭時代成立 —— 因為架構就在學員的專案裡。套件化之後架構在 wheel 裡，
再教「打開 coordinator 看看」等於教學員讀別人家的原始碼。

新主線改成套件化後真正需要人做的三件事：

```
① 架構          ② 人格                ③ 技能
ark-agent-bot-builder    ark-agent-init        sync_skills.py
ark-agent-team-builder   （SOUL / AGENTS）     （角色 × skill 矩陣）
   ↓                        ↓                     ↓
裝 wheel + 設定檔        每個 agent 是誰        每個 agent 有什麼工具
```

這三層同時是**課程結構的骨架**：01 給人格、02 給技能、03 給知識、04 定架構、05 讓它自轉。

---

## 1. 架構對照：學員的專案長什麼樣

### 1.1 課程 A 產出（ark_bot_agent 消費端）

```
my-bot/
├── start.py                  # 8 行：from ark_bot_agent import run_bot; run_bot()
├── agents.yaml               # 有誰（default/manager/admin/leader/worker）← 專案根哨兵
├── bot.yaml                  # 怎麼跑（server/modes/llm/backend/report/features/access）
├── .env                      # 機密（TELEGRAM_BOT_TOKEN / GEMINI_API_KEY）
├── requirements.txt          # 只列 wheel
├── .kiro/steering/           # 人格（ark-agent-init 產：SOUL/AGENTS/CODE/MEMORY/USER）
├── knowledge/shared/{wiki,raw}/   # 🔴 Wiki 引擎讀這層（少一層 shared 會靜默失效）
├── memory/daily/             # 🔴 套件記憶落點
├── artifacts/reports/        # 🔴 產出落點（取代舊 output/）
├── agents/<name>-agent/      # 各角色：.kiro + knowledge + memory + artifacts
└── skills/                   # 業務 skill（選填；空著就不要寫 run_bot(skills=[...])）
```

**學員實際會改的檔案只有三個**：`agents.yaml`（有誰）、`.kiro/steering/SOUL.md`（是誰）、`.env`（機密）。
這正好是第一堂的全部內容 —— 比舊版「探索 src/ 九個模組」清楚得多。

### 1.2 課程 B 產出（ark_team_agent 消費端）

```
my-team/
├── start.py                  # asyncio.run(run_team(Path("team.yaml")))
├── team.yaml                 # 唯一集中點：instances/access/cost_guard/hang_detector/kiro_files
├── scheduler.yaml            # 排程
├── .env
├── .kiro/steering/           # 全域規範（TEAM.md 由 daemon 動態產生，手改會被覆寫）
├── knowledge/{<team>,shared}/{wiki,raw}/   # 兩櫃，對應 knowledge_search_order
├── agents/<name>-agent/      # 各 instance 的 working_directory
└── scripts/sync_skills.py    # 角色 × skill 矩陣同步
```

### 1.3 設定即架構 —— 課程 B 的新教學素材

舊 Step 7 讓學員讀四個 Python 檔。新版讀 **`team.yaml` 的六個區塊**，每個對應一個架構概念：

| 區塊 | 架構概念 | 課堂示範 |
|---|---|---|
| `instances` + `role` | 誰在團隊、什麼位階（manager / leader / admin / worker） | 加一個 worker |
| `group: leader-agent` | **派工歸屬**（worker 指向所屬 leader） | 改歸屬 → 觀察輸出改發到哪個 topic |
| `access` | 誰能用（mode / allowed_users） | 加自己的 user_id |
| `cost_guard` | 費用護欄 | 調 daily_limit → 觀察告警 |
| `hang_detector` | 卡死偵測與升級 | 講解 timeout / escalation |
| `kiro_files` | skill 與 steering 的覆寫政策 | 講 `skills.policy: skip` 為何必要 |

> 🔴 **`group` 是 team 端寫法，`group_members` 是 bot 端寫法。** 寫錯套件會**靜默忽略**
> （只在 log 印一行「欄位不存在 → 已忽略」），派工歸屬不生效。這是必教的一條，
> 而且正好示範「設定看起來生效了其實沒有」這個更大的教訓。

---

## 2. 五堂課重新對映

| 堂 | 主題 | 保留 | 改寫 | 刪除 |
|---|---|---|---|---|
| **01** 🗣️ Agent 初始 | SOUL 八段式、IDE/TG 雙軌、切換 agent 體驗、遊戲場景 SOUL 設計 | Step 1「啟動」改為裝 wheel + `run_bot()`；Step 2「IDE 探索專案結構」改為**探索三個設定檔**（agents.yaml / bot.yaml / SOUL.md） | 探索 `src/` 九模組 |
| **02** ⚡ Skills 開發 | **整堂幾乎不動** —— grill-me → superpowers → skill-creator → validator 仍是現行做法 | 產出落點 `agents/<name>/.kiro/skills/`；`ark-skill-creator` 現行資產地圖（三管線）；驗證改用現行 Drift Report 契約 | 無 |
| **03** 🧠 LLM Wiki | ingest / query / lint 三動作、自演化循環、`sample-docs/` 素材 | 「四層搜尋」改為**套件內建**（不是 sample 自己實作）；路徑改 `knowledge/shared/`；改用 `ark-wiki-engine` 的 `wiki_query.py` / `wiki_index.py` / `wiki_lint.py` 而非 sample 的 `/api/v1/wiki/*` | Admin 後台頁面（sample 自有 Jinja） |
| **04** 🤝 Agent Team | 一句話派工、加新 agent、複合任務驗證 | Step 1 改裝 wheel；Step 2 改 `team.yaml`；Step 3.3「初始化新 Agent」改 `ark-agent-init` + `sync_skills.py`；**新增兩階段就緒**（冷啟 2–4 分鐘） | `build_team.py`、110+ 項產出清單 |
| **05** 🏭 營運落地 | 排程 + 費控 + 迴圈體驗（產出→raw→ingest→wiki→引用）、上線 checklist | `scheduler.yaml` 對齊現行格式；監控改用 `/api/health` + 套件 website（`health_port + 5000`）；上線 checklist 加 systemd user service | `apps/web` npm 建置、21+ 端點逐一 curl |

### 2.1 第二堂為什麼幾乎不用改

Loop 五件套是**共用庫層**的東西，與套件化正交。這一堂在盤點裡只有兩處要動
（skill 產出路徑、README 的「4 個 IDE Skill」清單），是五堂裡成本最低的。
> 判準：翻新的範圍要由「它依賴誰」決定，不是由「它看起來舊不舊」決定。

---

## 3. samples 重建設計

### 3.1 處置矩陣

| 目前內容 | 處置 | 理由 |
|---|---|---|
| `src/{bot,agent,llm,memory,server,wiki,tools}`（ai-bot） | **刪** | 套件內建，留著就是兩套並存必漂移 |
| `src/{gateway,coordinator,runtime}`（team） | **刪** | 同上 |
| `src/skills/internal/`、`src/business/` | **評估後刪**（業務 skill 另以 1 個最小範例重寫） | 教「怎麼加業務 skill」只需要一個能跑的最小例 |
| `templates/*.html`（6 頁 Jinja） | **刪** | 套件 `web_ui` 內建 |
| `apps/web/`（Next.js） | **刪** | 套件 website 內建（見 D-2） |
| `Dockerfile` / `Dockerfile.web` / `docker-compose.prod.yml` | **刪**，部署改指 `ark-docker-deploy` skill + systemd user service | 課程 B 的部署一節改教 systemd（本機實際做法） |
| `data/*.db`、`state/*.db` | **刪** | 執行產物，重啟自動重生；且進版控會帶走聊天紀錄 |
| `*.bat`（Windows 啟動腳本） | **刪** | 與 `.bat` 編碼 spawn 的 learning 一起標為歷史 |
| `agents/<8 個角色>/` 的 `.kiro/steering/` | **保留** | 人格資產可搬運 —— 這是 workshop 的賣點，套件化後依然成立 |
| `knowledge/`、`course-ai-bot/sample-docs/` | **保留** | 教學素材 |
| `agents.yaml` / `team.yaml` / `scheduler.yaml` | **重寫** | 對齊現行 schema（尤其 `group` 與 `kiro_files`） |

### 3.2 兩個 sample 的角色編制

維持八角色（學員已熟悉的貫穿案例），但**語意對齊現行組織軸**（以「能不能改 code」分）：

| 現有 | 保留為 | 說明 |
|---|---|---|
| admin-agent | 👑 管家 | 維運：CI / 版控 / 發布（能改 code，限維運面） |
| leader-agent | 🎯 隊長 | team 模式統籌（不改 code） |
| ai-dev-agent / coder-agent | 💻 工程師 | 唯一的業務邏輯寫手 |
| qa-agent | 🧪 驗證 | 反證與對等測試 |
| market-agent / data-agent / report-agent | 📖 顧問 / 📐 企劃 | 只讀不寫，產規格與報告 |

> 這個對映讓 sample 同時是「貫穿案例（遊戲競品分析）」與「現行編制示範」，
> 不需要再多一份說明。

### 3.3 sample 是否需要 `.venv`

**不進版控，也不預先建**。教材第一步就是建 venv 裝 wheel —— 那是課程內容本身。
（`.venv` 進版控會寫死絕對路徑，跨機必壞，本機已有多次紀錄。）

---

## 4. 守門設計：`scripts/check_docs.py`

### 4.1 設計原則

| 原則 | 為什麼 |
|---|---|
| deterministic、零 LLM | 守門要能在 CI 與 pre-commit 跑，且結果可重現 |
| `--help` 無副作用 | 「先看 help」是所有人面對陌生 CLI 的第一個動作，而所有人都預期它唯讀 |
| help 攔截放在第三方 import **之前** | help 本來就不該需要依賴 |
| exit code 只由 P0 + P1 決定 | P2/P3 讓報告醒目，但不擋提交 |
| **命中 0 視為錯誤** | 掃到 0 個檔案的綠燈是「什麼都沒驗」，不是「全部通過」 |
| 每條規則附反證測試 | 綠燈只代表「規則沒作用」的機率很高，除非證明它會紅 |

### 4.2 規則表

| 規則 | 級 | 實作 | 反證 |
|---|---|---|---|
| `dead-skill-ref` | P0 | 舊名清單（§spec 2.3）逐一 grep，扣除白名單路徑 | 在 README 植入 `ark-kiro-init` → 應報 P0 |
| `stale-script-ref` | P0 | 抓教材 bash 區塊裡的 `*.py` 路徑，驗檔案存在（相對共用庫或 repo） | 植入 `build_team.py` → 應報 P0 |
| `broken-path` | P1 | 抓 `\`路徑\`` 與 bash 區塊的 repo 內相對路徑，驗存在 | 現存的 `sampless/` 錯字應當場被抓到 |
| `sample-not-package` | P0 | sample 的 `requirements.txt` 須含 `ark_bot_agent` / `ark_team_agent`；`src/` 不得出現 runtime 模組名 | 建一個 `src/runtime/` → 應報 P0 |
| `skill-not-active` | P1 | 教材宣稱使用的 `ark-*` 須在共用庫 active 清單（讀 `.kiro/skills/*/SKILL.md` 的 `status`） | 引用一個 deprecated stub → 應報 P1 |
| `scanned-zero` | P0 | 任一規則掃描檔數為 0 → 直接失敗 | 把掃描根指到空目錄 → 應報 P0 |

### 4.3 接線

| 位置 | 動作 |
|---|---|
| 本地 | `python3 scripts/check_docs.py`（看 rc，**不接 pipe** —— pipe 會吃掉非 0 的 rc） |
| CI（選配） | GitHub Actions 一個 job，job summary 明講掃了幾個檔、命中幾條 |
| 講師課前 | 列入講師手冊「開課前 checklist」第一項 |

---

## 5. 決策紀錄（ADR）

### ADR-005：教材主線從「架構解說」改為「三層分工」

- **背景**：套件化後架構在 wheel 裡，不在學員專案裡。
- **決策**：主線改為 ① builder 定架構 ② agent-init 給人格 ③ sync_skills 給技能。
- **後果**：課程 B 的 Step 7（讀 a2a 原始碼）整段作廢，改為讀 `team.yaml` 六區塊。
  失去「看得到實作」的深度，換得「每一步學員都能自己做」。想深入的人改看套件 repo。

### ADR-006：舊 samples 直接重建，不保留 legacy 目錄

- **背景**：19,963 行手搭實作已被套件取代。
- **決策**：`git rm`，靠 git 歷史封存（`git show 987d00d:samples/ai-bot/src/...`）。
- **後果**：repo 9 MB → < 1 MB；守門不必為 legacy 開豁免
  （豁免清單最常見的失敗模式就是順便蓋掉別的問題）。

### ADR-007：Web Dashboard 改用套件內建 website

- **背景**：`apps/web` 是 Next.js，需 Node 20 + `npm install`，是課堂最大卡點。
- **決策**：改教套件內建 website（`health_port + 5000`）。
- **後果**：少一個技術棧；學員看到的 dashboard 與正式環境一致。

### ADR-008：ADR-004（兩產品同架構）標為 superseded 而非刪除

- **背景**：ADR-004 的立論（兩產品共用能力模組、架構刻意不同）已被套件化取代。
- **決策**：保留原文，加 `status: superseded-by: ADR-005` 標頭。
- **後果**：決策紀錄是 append-only，記當時事實；讀者看得到「為什麼後來變了」。

---

## 6. 教材檔案處置總表

| 檔案 | 動作 | 工作量 |
|---|---|---|
| `README.md` | 改寫架構對比表、快速開始、skill 清單與數字 | M |
| `course-ai-bot/build-guide.md` | Phase 1 全改（Step 0-3）、技術棧表重寫、修錯字 | L |
| `course-ai-team-agent/build-guide.md` | Phase 1 全改、Step 7 改 team.yaml 導讀、技術棧表重寫 | L |
| `course-ai-bot/QUICKSTART-01` | Step 1-2 改寫，Step 3-6 微調 | M |
| `course-ai-bot/QUICKSTART-02` | 產出路徑與 skill 清單微調 | S |
| `course-ai-bot/QUICKSTART-03` | API 改 wiki-engine 腳本、路徑加 `shared/` | M |
| `course-ai-team-agent/QUICKSTART-04` | Step 1-3 改寫 + 兩階段就緒專節 | L |
| `course-ai-team-agent/QUICKSTART-05` | scheduler/監控/部署改寫 | M |
| `course-ai-team-agent/troubleshooting.md` | 重寫（現行故障模式：冷啟、token 互搶、extras、group 靜默忽略） | M |
| `docs/quickstart-ai-bot.md`、`docs/quickstart-llm-wiki.md` | 改寫或合併進 QUICKSTART（見 plan T6） | M |
| `instructor/teaching-guide.md` | 指令更新 + 課前 checklist + 突發狀況三項 | M |
| `shared/bridge-diagram.md` | 五層架構對應改為三層分工對應 | S |
| `shared/telegram-setup.md`（6 行） | 擴寫：每人專屬 token + 互搶風險 | S |
| `shared/env-check.md` | 加 wheel / extras / venv 檢查 | S |
| `reports/*.html` ×5 | 依定稿後的 Markdown 重新產生（`ark-html-report`） | M |
| `docs/wiki/adr/004` | 標 superseded | S |
| `docs/wiki/adr/002`、`learnings/kiro-cli-cwd-problem.md` | `KIRO.md` → `CODE.md` | S |
| `samples/ai-bot`、`samples/ai-team-agent` | 重建 | XL |
| `scripts/check_docs.py` + 測試 | 新建 | M |

---

## 7. 開放問題

1. `docs/quickstart-ai-bot.md` 與 `course-ai-bot/QUICKSTART-01~03` 內容重疊約 40%，
   翻新時要合併還是各自保留？（plan T6 先做重疊分析再決定，避免兩份各自演化 —— 那正是
   目前 build-guide 與 QUICKSTART 對不上的原因。）
2. 課程 B 的 `team-dev.yaml` / `team-ops.yaml` 兩套編制是否保留？
   現行 `ark-agent-team-builder` 的 `references/templates/` 已有 team-full / team-dev / team-ops 三份 —— 建議直接引用，不在 sample 內另維護一份。
3. 五堂課是否加一堂「多 CLI 共用 workspace」（`ark-agent-init` v2.0 的 SSOT + CLAUDE.md/AGENTS.md）？
   目前傾向**併入第一堂尾段**（10 分鐘），不另開堂。
