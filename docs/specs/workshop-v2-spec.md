---
title: "AI Workshop v2 — 套件化翻新規格書"
type: spec
status: draft
created: 2026-09-14
language: zh-TW
owner: paddyyang
baseline:
  repo_head: 987d00d
  ark_bot_agent: "1.0.16"
  ark_team_agent: "1.8.16"
  ark_agent_skills_active: 50
---

# AI Workshop v2 — 套件化翻新規格書

## 一句話

教材教的是「用 scaffolder 產一套 10K 行手搭架構」，而現實已經是
「**裝 wheel + 8 行 start.py + 設定檔**」—— 本規格定義把整個 workshop
（教材 + samples + 報告 + 講師手冊）對齊 `ark_bot_agent` / `ark_team_agent`
兩套件與 `ark-agent-init` 初始化流程的完整翻新。

---

## 1. 背景與問題

### 1.1 架構已收斂為兩型 + 一個初始化器

| 層 | 現況 | 教材現在教的 |
|---|---|---|
| 單 bot | `ark_bot_agent` wheel（runtime / 三模式路由 / Web UI / 四層搜尋 / 記憶 / TG polling 全內建） | 手搭 `src/{bot,agent,llm,wiki,memory,server,skills,tools}` **9,995 行** |
| 多 agent 團隊 | `ark_team_agent` wheel（daemon / A2A / Kanban / REST / autopilot / 排程 / 決策路由全內建） | 手搭 `src/{gateway,coordinator,runtime,business}` **9,968 行** + Next.js `apps/web` |
| 角色初始化 | `ark-agent-init`（v2.0，產 steering 人格 + 多 CLI 入口） | `ark-kiro-init`（舊名，v1.x） |

三個 scaffolder 已於 2026-09-08 全面 v3.0 重寫，價值從「產程式碼」轉為
**「裝 wheel + 產設定骨架」**。教材停在重寫之前。

### 1.2 這不是「版本落差」，是「整段內容作廢」

教材的 Step 1 / Step 2 指令現在**跑不起來**（腳本已改名或已移除），
而學員照著做的第一個動作就是它們。這不是註腳層級的過時，是主線斷裂。

---

## 2. 現況總盤點

### 2.1 規模

| 項目 | 數量 |
|---|---|
| 教材 Markdown | 18 檔 / 3,974 行 |
| HTML 報告 | 5 檔 / 101 KB |
| docs/wiki（ADR + learnings + architecture + teaching） | 14 篇 |
| samples | 2 個專案 / 19,963 行 Python / 9 MB |

### 2.2 逐檔缺陷盤點

| 檔案 | 缺陷 | 嚴重度 |
|---|---|---|
| `README.md` | `ark-kiro-init` 舊名；「src 架構」對比表（扁平模組 vs 四層）全屬手搭時代；`PersistentDaemon`／`Gemini ReAct` 作為架構賣點；Skills「57 個」（現 50 active）；快速開始用 `pip install -r requirements.txt` 而非 wheel | **P0** |
| `course-ai-bot/build-guide.md` | `ark-agent-builder` ×5（已更名 `ark-agent-bot-builder` 且重寫）；`ark-kiro-init` ×5；`build_agent.py` / `build_kiro.py` 指令；產出清單列 `src/` 九模組；`KIRO.md`（已更名 `CODE.md`）；技術棧表整表是手搭模組；`sampless` 錯字 | **P0** |
| `course-ai-team-agent/build-guide.md` | `ark-kiro-init` ×8；`build_team.py`；`src/coordinator` ×9、`src/runtime`、`src/gateway`；`CoreDaemon` ×4；「產出 110+ 項」；Step 7 要學員打開 `a2a/graph.py`、`discovery.py`、`protocol.py` 讀碼（檔案在套件裡，不在專案裡）；`sampless` 錯字 | **P0** |
| `course-ai-bot/QUICKSTART-01~03` | Step「IDE 探索專案結構」依賴手搭 `src/`；Admin 後台、port 8000、Jinja 6 頁為 sample 自有實作 | **P1** |
| `course-ai-team-agent/QUICKSTART-04~05` | `ark-kiro-init` ×3；`build_team`；port 33333 與 21+ 端點清單；`apps/web` npm run dev | **P1** |
| `samples/ai-bot/` | 無 `ark_bot_agent` 依賴；手搭 9,995 行；`requirements.txt` 直列 telegram/fastapi/genai | **P0** |
| `samples/ai-team-agent/` | 無 `ark_team_agent` 依賴；手搭 9,968 行 + `apps/web` + 2 個 Dockerfile | **P0** |
| `docs/quickstart-ai-bot.md`、`docs/quickstart-llm-wiki.md` | Tier 0-3 為 sample 自有概念；port 8000；手搭流程 | **P1** |
| `instructor/teaching-guide.md` | `build_agent.py` / `build_kiro.py` / `build_team.py` ×4 | **P1** |
| `shared/bridge-diagram.md` | `build_team`；「五層架構對應」為手搭架構 | **P1** |
| `reports/*.html` ×5 | `ark-kiro-init`；`pip install -r requirements.txt`；架構圖為手搭四層 | **P2** |
| `docs/wiki/adr/004-same-architecture-two-products.md` | 立論基礎（兩產品同架構）已被套件化取代 | **P2** |
| `docs/wiki/adr/002-no-symlink-use-relative.md`、`learnings/kiro-cli-cwd-problem.md` | 引用 `KIRO.md`（已更名 `CODE.md`） | **P3** |

### 2.3 已移除／更名 skill 的引用（全庫）

| 舊名 | 現況 | 檔數 / 命中 |
|---|---|---|
| `ark-agent-builder` | → `ark-agent-bot-builder`（v3.0 重寫） | 2 / 6 |
| `ark-kiro-init` | → `ark-agent-init`（v2.0） | 7 / 22 |
| `ark-news-daily` | → `ark-daily-news`（舊單檔版已從套件與共用庫移除） | 4 / 6 |
| `ark-chatbot-generator` | 已移除（死引用，從未存在於現行庫） | 3 / 3 |
| `ark-scheduler-generator` | 併入 `ark-webapp-generator` v2.0 | 1 / 1 |
| `ark-llm-cli` | → `ark-agent-cli` | 1 / 1 |

> 🔴 這批是**教材裡的死引用**：學員（或 agent）說出這些觸發詞時不會有任何反應。

### 2.4 仍然成立、不該動的資產

盤點的價值一半在「哪些不用改」：

- **五堂課的能力遞進**（說話 → 做事 → 記住 → 合作 → 自己跑）與教學理念（`docs/teaching-philosophy.md`）**與套件無關**，全數保留。
- **SOUL.md 八段式**、Spec-Driven（grill-me → superpowers → spec-executor → validator）、Wiki 三動作（ingest / query / lint）**全部仍是現行做法**。
- **`agents/<name>/` 人格資產可搬運**這個賣點仍然成立 —— 而且套件化後更成立（bot 與 team 都讀同形狀的 `.kiro/steering`）。
- **貫穿案例（遊戲競品分析）** 與 `course-ai-bot/sample-docs/` 素材不受影響。
- `docs/wiki/` 的 ADR-001（用 Markdown 不用 SQLite）、ADR-003（bm25s）、多數 learnings 仍然有效。

---

## 3. 目標

| # | 目標 | 驗收方式 |
|---|---|---|
| G1 | 教材主線可從頭跑到尾，每一條指令都能執行 | 講師照 QUICKSTART 全程實跑一次，零卡點 |
| G2 | 兩個 sample 都是**套件消費端**，不含手搭 runtime | `grep -c 'ark_bot_agent\|ark_team_agent' requirements.txt` ≥ 1，且 `src/` 只剩業務 skill |
| G3 | 全庫零死引用（已移除／更名 skill） | `scripts/check_docs.py` exit 0 |
| G4 | 教學主線與現行三層分工一致（架構 → 人格 → 技能） | 每堂課標示使用的 skill，且該 skill 在共用庫 active |
| G5 | 課堂實際風險寫進教材（TG token 互搶、兩階段冷啟、extras 不可省） | 三項各有專節，且列在講師手冊「常見突發狀況」 |

### 非目標

- 不改五堂課的**課程結構與時長**（3 + 2 堂 × 50 min）。
- 不重寫 `docs/teaching-philosophy.md` 的教學理念。
- 不做套件本身的任何修改（本 repo 是消費端）。
- 不翻新 `docs/wiki/` 中與架構無關的 learnings。

---

## 4. 需求

### FR-1 教材主線改寫（課程 A）

| 舊 | 新 |
|---|---|
| Step 1 `build_agent.py my-agent` → 產 `src/` 九模組 | Step 1 `uv pip install 'ark_bot_agent-*.whl[search,skills]'` → 產 `start.py` + `bot.yaml` + `agents.yaml` |
| Step 2 `build_kiro.py --standalone` | Step 2 `ark-agent-init` 為 manager 與各 agent 產 `.kiro/steering` |
| Step 3 改 `SOUL.md` | **不變**（本堂核心，仍然成立） |

`.env` 必要變數、extras 必裝、`python -m ark_bot_agent paths` 診斷指令要列入。

### FR-2 教材主線改寫（課程 B）

| 舊 | 新 |
|---|---|
| Step 1 `build_team.py my-team` → 110+ 項 | Step 1 裝 `ark_team_agent` wheel → `start.py`（`asyncio.run(run_team(...))`）+ `team.yaml` + `scheduler.yaml` |
| Step 2 `build_kiro.py` ×3 | Step 2 `ark-agent-init` 補人格 → Step 2.5 `sync_skills.py` 依角色矩陣裝專業技能 |
| Step 7 讀 `src/coordinator/a2a/*.py` | 改為讀 **`team.yaml` 的 instances / group / access / cost_guard / hang_detector**（設定即架構） |

新增必教項：
- worker 歸屬用 **`group: <leader>`**（team 端），不是 bot 端的 `group_members` —— 寫錯會被套件靜默忽略。
- `kiro_files` 必須設 `skills.policy: skip`，否則套件每次啟動推翻角色矩陣。
- website port = `health_port + 5000`。

### FR-3 samples 重建

兩個 sample 重建為套件消費端骨架：

```
samples/ai-bot/                    samples/ai-team-agent/
├── start.py      (8 行)           ├── start.py      (3 行)
├── bot.yaml                       ├── team.yaml
├── agents.yaml                    ├── scheduler.yaml
├── requirements.txt (只列 wheel)   ├── requirements.txt (只列 wheel)
├── .env.example                   ├── .env.example
├── .kiro/steering/                ├── .kiro/steering/
├── agents/<name>-agent/           ├── agents/<name>-agent/
├── knowledge/shared/{wiki,raw}/   ├── knowledge/shared/{wiki,raw}/
├── memory/daily/                  ├── memory/
├── artifacts/reports/             ├── artifacts/reports/
└── skills/ (業務 skill，選填)      └── scripts/sync_skills.py
```

**保留**：`agents/*/` 八個角色人格（可搬運資產）、`knowledge/` 既有內容、`course-ai-bot/sample-docs/`。
**移除**：`src/` 全部、`templates/*.html`、`apps/web/`、`Dockerfile*`、`data/*.db`、`state/*.db`、`*.bat`。

### FR-4 死引用清除與名稱對映

依 §2.3 對映表全庫替換。歷史紀錄（`docs/wiki/adr/`、ADR 決策日誌）**保留當時名字**，
只在活的指標（教材、README、講師手冊）替換 —— 與長期慣例一致。

### FR-5 課堂實務風險專節（新增）

| 風險 | 內容 | 放哪 |
|---|---|---|
| TG token 互搶 | 同一 token 兩處 polling 會**隨機**吃訊息且不報錯 → 每位學員必須自己申請 | `shared/telegram-setup.md` + 講師手冊 |
| 兩階段冷啟 | ① daemon + TG ~20s ② kiro-cli backend 首次含 MCP 握手 **2–4 分鐘**，就緒訊號才算數；「送了沒回」先查 CPU 時間 | QUICKSTART-04 Step 4 + troubleshooting |
| extras 不可省 | 只裝 base wheel → 四層搜尋靜默降級、排程只印一行 WARNING 就跳過 | QUICKSTART-01 Step 1 + build-guide |

### FR-6 守門腳本（新增）

`scripts/check_docs.py`，deterministic、零 LLM、`--help` 無副作用：

| 規則 | 嚴重度 | 判準 |
|---|---|---|
| `dead-skill-ref` | P0 | 教材出現已移除／更名 skill 名（歷史目錄 `docs/wiki/adr/` 除外） |
| `stale-script-ref` | P0 | 教材出現 `build_agent.py` / `build_team.py` 等不存在的腳本路徑 |
| `broken-path` | P1 | 教材引用的 repo 內相對路徑不存在（含 `sampless` 這類錯字） |
| `sample-not-package` | P0 | sample 的 `requirements.txt` 未列 ark_* wheel，或 `src/` 內出現 runtime 模組 |
| `skill-not-active` | P1 | 教材宣稱使用的 skill 不在共用庫 active 清單 |

> 🔴 **先做守門再修內容**。這批缺陷沒有一條是「東西不見了」，全部是
> 「教材與消費端各自演化、對不上」。只修症狀它會漂移回去。
> 每條規則都必須用**反證**測過會紅。

---

## 5. 驗收條件（AC）

| ID | 條件 | 驗證 |
|---|---|---|
| AC-1 | `python3 scripts/check_docs.py` exit 0，P0/P1 為 0 | 指令 rc（**不接 pipe**） |
| AC-2 | 每條規則反證會紅 | 刻意植入 `ark-kiro-init` → P0；移除後歸零 |
| AC-3 | `samples/ai-bot` 可實跑：裝 wheel → `python start.py` → TG `/start` 有回應 | 實機 |
| AC-4 | `samples/ai-team-agent` 可實跑：health 端點 `/api/health` 回 200，instances 全 ready | `curl` + rc |
| AC-5 | 兩 sample 的 `src/` 不含任何 runtime 模組（bot/agent/llm/wiki/memory/server/gateway/coordinator/runtime） | `find` 斷言 |
| AC-6 | 全庫 `grep` 六個舊 skill 名，命中僅落在 §7 白名單（歷史目錄） | grep + 白名單比對 |
| AC-7 | 五堂 QUICKSTART 的每個 `bash` 區塊指令，其引用的檔案／腳本存在 | `check_docs.py` broken-path |
| AC-8 | README 的 skill 數字與共用庫 active 數一致，且該行標明「以守門輸出為準」 | 人工 + 守門 |
| AC-9 | 講師手冊「常見突發狀況」含 FR-5 三項 | 人工 |

---

## 6. 待裁決策

### D-1 舊 samples 的處置 ⭐

| 選項 | 說明 | 取捨 |
|---|---|---|
| 1️⃣ **直接重建，舊碼靠 git 歷史**（推薦） | `git rm -r src/ apps/ templates/`，重建骨架 | repo 從 9 MB 降到 < 1 MB；要看舊實作 `git show 987d00d:` 拿得到 |
| 2️⃣ 保留 `samples/legacy/` | 舊兩專案原封搬進 legacy 目錄 | 學員會困惑「我該看哪個」；守門要為 legacy 開豁免（豁免清單最常見的失敗模式就是順便蓋掉別的問題） |
| 3️⃣ 另開 repo 封存 | `ai-workshop-legacy` | 成本最高，收益僅「有個網址」 |

> 推薦 1️⃣：手搭實作的教學價值已被套件取代，而 git 歷史就是封存。

### D-2 課程 B 的 Web Dashboard 怎麼教

| 選項 | 說明 |
|---|---|
| 1️⃣ **改教套件內建 website**（推薦） | `health_port + 5000`，零前端建置，學員一個瀏覽器分頁就看到 |
| 2️⃣ 保留 Next.js `apps/web` | 要 Node 20+、`npm install`，課堂上是最大卡點來源，且與套件重複 |

### D-3 wheel 怎麼發給學員

| 選項 | 說明 |
|---|---|
| 1️⃣ **課前從 GitHub Release 下載**（推薦） | 教材寫 Release 網址 + 版本；與正式做法一致 |
| 2️⃣ wheel 進 repo | 二進位進版控、每次升版 repo 變胖 |
| 3️⃣ 現場 USB / 區網分享 | 最保險（教室網路不可靠），但與教材脫節 → 建議當 1️⃣ 的備援寫進講師手冊 |

---

## 7. 白名單（允許保留舊名的位置）

| 路徑 | 理由 |
|---|---|
| `docs/wiki/adr/*.md` | 決策紀錄 append-only，記當時事實 |
| `docs/specs/`、`docs/designs/`、`docs/plans/`（本批文件） | 盤點需引用舊名 |
| 各檔的「更名紀錄／遷移說明」段落 | 明確標示為歷史 |

---

## 8. 風險

| 風險 | 影響 | 對策 |
|---|---|---|
| 套件版本在翻新期間繼續前進 | 教材寫死版號會立刻過時 | 教材寫「從 Release 取最新」+ 一處 `baseline` 區塊記實測版號，其餘不寫死 |
| 兩個 sample 重建後沒人實跑就交付 | 交付一份跑不起來的教材（正是現在的處境） | AC-3/AC-4 要求實機，且**兩階段就緒**驗到第二階段 |
| 守門只驗「有沒有舊名」而漏「新名對不對」 | 綠燈但內容仍錯 | 加 `skill-not-active`：教材宣稱用的 skill 必須在 active 清單 |
| `check_docs.py` 掃到 0 個就回綠 | 一個什麼都沒驗的綠燈 | 規則須斷言「掃到的檔案數 > 0」，命中 0 視為錯誤 |

---

## 9. 參考

- `ark-agent-bot-builder` v3.0 SKILL.md（消費端骨架定義）
- `ark-agent-team-builder` v3.0 SKILL.md（三層分工圖 + `examples/market-team/`）
- `ark-agent-init` v2.0 SKILL.md（steering 五檔 + 多 CLI 入口）
- `ark-agent-init/references/architecture-drift-feedback.md`（三個骨架缺口）
- 本機實例：`projects/slot-bot`（bot 消費端）、`projects/market-team`（team 消費端）
