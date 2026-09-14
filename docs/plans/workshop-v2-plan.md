---
title: "AI Workshop v2 — 套件化翻新執行計畫"
type: plan
status: draft
created: 2026-09-14
language: zh-TW
spec: ../specs/workshop-v2-spec.md
design: ../designs/workshop-v2-design.md
---

# AI Workshop v2 — 套件化翻新執行計畫

## 執行原則

| # | 原則 | 為什麼 |
|---|---|---|
| 1 | **守門先於修內容**（T1 是第一個任務） | 這批缺陷沒有一條是「東西不見了」，全是兩邊各自演化對不上。只修症狀它會漂移回去 |
| 2 | 每個任務一個 commit，commit 前 `git reset HEAD .` 再精確 `git add` | 本機多 agent 同工作樹，index 是共享的 |
| 3 | 驗守門**看 rc，而看 rc 就不能接 pipe** | `\| tail`／`\| grep` 會吃掉非 0 的 rc |
| 4 | 新規則一律用**反證**測「它會不會紅」 | 綠燈只代表規則沒作用的機率很高 |
| 5 | 掃描類腳本先看它「掃到幾個」合不合理，再看它報不報錯 | 命中 0 是錯誤，不是「本來就沒有」 |
| 6 | 實跑驗證要驗到**第二階段就緒** | 「6/6 ready + TG started」≠「私訊會回」 |

---

## 階段總覽

```
P0 守門          T1
P1 樣本重建      T2 → T3 → T4      （最大宗，決定教材怎麼寫）
P2 教材主線      T5 → T6 → T7 → T8
P3 周邊資產      T9 → T10 → T11
P4 驗收          T12 → T13
```

---

## 任務表

### T1 — 建立守門 `scripts/check_docs.py`

| 項目 | 內容 |
|---|---|
| 依賴 | 無（第一個做） |
| 產出 | `scripts/check_docs.py`、`scripts/tests/test_check_docs.py` |
| 內容 | 實作 design §4.2 六條規則；`--help` 攔截置於第三方 import 之前；exit code 只由 P0+P1 決定 |
| AC-1.1 | 對**當前**（未翻新）的 repo 執行 → 應報出 §spec 2.3 的六個舊名與 `sampless` 錯字（**現在就該是紅的**） |
| AC-1.2 | 每條規則各有一個反證測試，植入缺陷會紅、移除會綠 |
| AC-1.3 | `python3 scripts/check_docs.py --help` 在空目錄執行後，該目錄仍為空（無副作用） |
| AC-1.4 | 掃描檔數為 0 時回非 0（`scanned-zero`） |

> 🔴 T1 完成時守門**必須是紅的**。一個在翻新前就綠的守門，代表它什麼都沒驗。

---

### T2 — 重建 `samples/ai-bot` 為 ark_bot_agent 消費端

| 項目 | 內容 |
|---|---|
| 依賴 | T1 |
| 手段 | `ark-agent-bot-builder` v3.0 產骨架 → `ark-agent-init` 補人格 |
| 保留 | `agents/*/` 八角色人格、`knowledge/`、`sample-docs/` |
| 刪除 | `src/`、`templates/`、`data/*.db`、`state/*.db`、`*.bat`、舊 `requirements.txt` |
| AC-2.1 | `requirements.txt` 只列 `ark_bot_agent[search,skills]` wheel |
| AC-2.2 | `find samples/ai-bot/src -type d` 不含 bot/agent/llm/memory/server/wiki/tools |
| AC-2.3 | 實跑：建 venv → 裝 wheel（**驗 import 版號，不看 pip 輸出**）→ `python start.py` → TG `/start` 有回應 |
| AC-2.4 | 啟動橫幅無「注入了 skills 但一個都沒載到」假警報 |
| AC-2.5 | `knowledge/shared/{wiki,raw}/` 存在且 `wiki_index.py build` 能建出非空索引 |

---

### T3 — 重建 `samples/ai-team-agent` 為 ark_team_agent 消費端

| 項目 | 內容 |
|---|---|
| 依賴 | T2（編制與人格對映沿用） |
| 手段 | `ark-agent-team-builder` v3.0 產骨架（參考 `examples/market-team/`）→ `ark-agent-init` 補人格 → `sync_skills.py` 裝技能 |
| 刪除 | `src/`、`apps/web/`、`Dockerfile*`、`docker-compose.prod.yml`、`*.bat` |
| AC-3.1 | `team.yaml` 的 worker 用 **`group: leader-agent`**（不是 `group_members`），且 `kiro_files.skills.policy: skip` |
| AC-3.2 | `validate_team.py` 通過、佔位符殘留 0 |
| AC-3.3 | 實跑：`/api/health` 回 **200**、instances 全 ready |
| AC-3.4 | **第二階段就緒驗到**：TG 私訊有回覆（首次冷啟含 MCP 握手 2–4 分鐘，期間非故障） |
| AC-3.5 | `scripts/sync_skills.py --check` 一致（矩陣與實際部署對得上） |

---

### T4 — samples 骨架三缺口與 .gitignore

| 項目 | 內容 |
|---|---|
| 依賴 | T2, T3 |
| 內容 | 兩 sample 都要有 `knowledge/shared/`、`memory/daily/`、`artifacts/reports/`；`.gitignore` 排除 `.venv/`、`state/`、`*.db`、`memory/daily/`（執行產物） |
| AC-4.1 | 三個目錄在兩個 sample 都存在且有 `.gitkeep` 或內容 |
| AC-4.2 | `git status` 在實跑一次後仍乾淨（執行產物不入版控） |

---

### T5 — 課程 A 教材改寫

| 項目 | 內容 |
|---|---|
| 依賴 | T2（教材要照重建後的 sample 寫） |
| 檔案 | `course-ai-bot/build-guide.md`、`QUICKSTART-01/02/03`、`course-ai-bot/README.md` |
| 內容 | Phase 1 改「裝 wheel + 三個設定檔 + ark-agent-init」；Step 2 改探索三檔；Phase 3 改 wiki-engine 腳本與 `knowledge/shared/` 路徑；技術棧表重寫；修 `sampless` 錯字；加 extras 警告 |
| AC-5.1 | build-guide 每個 bash 區塊的指令在重建後的 sample 上可實跑 |
| AC-5.2 | `check_docs.py` 對 `course-ai-bot/` 零 P0/P1 |
| AC-5.3 | 第二堂改動僅限 skill 產出路徑與清單（不重寫 Loop 流程） |

---

### T6 — `docs/quickstart-*.md` 重疊分析與收斂

| 項目 | 內容 |
|---|---|
| 依賴 | T5 |
| 內容 | 先做重疊度分析（`docs/quickstart-ai-bot.md` vs `QUICKSTART-01~03`），再決定合併或分工。**任一內容只能有一份真相** |
| AC-6.1 | 產出一頁分析（哪些段落重複、留哪份），寫進本 plan 的附錄 |
| AC-6.2 | 收斂後，同一主題不存在兩份各自維護的說明 |

> 目前 build-guide 與 QUICKSTART 對不上，根因就是同一件事寫了兩份。

---

### T7 — 課程 B 教材改寫

| 項目 | 內容 |
|---|---|
| 依賴 | T3 |
| 檔案 | `course-ai-team-agent/build-guide.md`、`QUICKSTART-04/05`、`README.md`、`troubleshooting.md` |
| 內容 | Phase 1 改裝 wheel + team.yaml；Step 2 改 ark-agent-init + sync_skills；**Step 7 改「team.yaml 六區塊導讀」**；監控改 `/api/health` + 內建 website（`health_port + 5000`）；部署改 systemd user service；troubleshooting 重寫為現行四大故障模式 |
| AC-7.1 | 無 `src/coordinator`／`src/runtime`／`src/gateway`／`CoreDaemon` 字樣 |
| AC-7.2 | 兩階段就緒有獨立小節，含「送了沒回先查 kiro-cli CPU 時間」的判準 |
| AC-7.3 | `check_docs.py` 對 `course-ai-team-agent/` 零 P0/P1 |

---

### T8 — README 與 bridge-diagram 改寫

| 項目 | 內容 |
|---|---|
| 依賴 | T5, T7 |
| 內容 | 架構對比表改「兩型套件 + 一個初始化器」；快速開始改 wheel；skill 清單改現行 base_skills 8 個並標「數字以守門輸出為準」；`shared/bridge-diagram.md` 五層架構 → 三層分工 |
| AC-8.1 | README 的 skill 數與共用庫 active 數一致 |
| AC-8.2 | 快速開始的指令可在乾淨環境實跑 |

---

### T9 — 講師手冊與共用資源

| 項目 | 內容 |
|---|---|
| 依賴 | T5, T7 |
| 檔案 | `instructor/teaching-guide.md`、`shared/telegram-setup.md`、`shared/env-check.md` |
| 內容 | 指令更新；新增「開課前 checklist」（守門綠、wheel 已下載、每位學員自己的 TG token）；「常見突發狀況」加三項（token 互搶 / 冷啟 2–4 分鐘 / extras 缺失靜默降級）；`telegram-setup.md` 從 6 行擴寫 |
| AC-9.1 | 三項風險各有處置步驟，不只是提及 |
| AC-9.2 | 課前 checklist 第一項是跑 `check_docs.py` |

---

### T10 — `docs/wiki` 歷史資產標記

| 項目 | 內容 |
|---|---|
| 依賴 | T8 |
| 內容 | ADR-004 標 `superseded`（保留原文）；ADR-002 與 `learnings/kiro-cli-cwd-problem.md` 的 `KIRO.md` → `CODE.md`；新增 ADR-005~008（design §5） |
| AC-10.1 | ADR 目錄 append-only，無既有 ADR 內文被改寫（除 status 標頭） |
| AC-10.2 | 新 ADR 四篇有完整 frontmatter |

---

### T11 — HTML 報告重產

| 項目 | 內容 |
|---|---|
| 依賴 | T8, T9 |
| 內容 | 依定稿 Markdown 用 `ark-html-report` 重產 5 份；架構圖改三層分工 |
| AC-11.1 | 5 份 HTML 無舊 skill 名、無 `pip install -r requirements.txt` |
| AC-11.2 | 內容與對應 Markdown 一致（同一真相） |

---

### T12 — 全案守門與端到端驗收

| 項目 | 內容 |
|---|---|
| 依賴 | T1–T11 |
| AC-12.1 | `python3 scripts/check_docs.py` **rc = 0**（不接 pipe），P0/P1 為 0 |
| AC-12.2 | 反證：植入 `ark-kiro-init` → 紅；移除 → 綠 |
| AC-12.3 | 兩個 sample 從零實跑（新 venv → 裝 wheel → 啟動 → TG 驗證），course A 與 course B 各一次 |
| AC-12.4 | 全庫六個舊名的 grep 命中，僅落在 spec §7 白名單 |

---

### T13 — 乾跑（dry-run）一次完整課程

| 項目 | 內容 |
|---|---|
| 依賴 | T12 |
| 內容 | 由一個人（最好不是改教材的人）照 QUICKSTART-01 → 05 全程操作，記錄每個卡點與耗時 |
| AC-13.1 | 五堂全程零卡點，或卡點已回寫教材 |
| AC-13.2 | 每堂實際耗時記錄進講師手冊（對照 50 min 設計） |

> 🔴 這一步不能省。目前這份教材的問題，本質上就是「沒有人從頭跑過一次」。

---

## 相依圖

```
T1 ──┬─ T2 ─┬─ T3 ─── T4
     │      │
     │      └─ T5 ─── T6 ──┐
     │                      ├─ T8 ─┬─ T10 ─┐
     └───────── T7 ─────────┘      │       ├─ T12 ─── T13
                └──────────────────┴─ T9 ──┴─ T11 ─┘
```

---

## 工作量估計

| 階段 | 任務 | 估計 |
|---|---|---|
| P0 守門 | T1 | 0.5 天 |
| P1 樣本重建 | T2–T4 | 2 天（含實跑，team 冷啟等待佔時間） |
| P2 教材主線 | T5–T8 | 2.5 天 |
| P3 周邊 | T9–T11 | 1 天 |
| P4 驗收 | T12–T13 | 1 天（T13 乾跑本身就要 4 小時） |
| **合計** | | **約 7 天** |

---

## 開工前必須先裁的事

| # | 決策 | 推薦 | 影響任務 |
|---|---|---|---|
| D-1 | 舊 samples 處置 | 1️⃣ 直接重建，靠 git 歷史封存 | T2, T3 |
| D-2 | 課程 B 的 Dashboard | 1️⃣ 改用套件內建 website | T3, T7 |
| D-3 | wheel 發給學員的方式 | 1️⃣ GitHub Release + 3️⃣ 當備援 | T5, T7, T9 |

---

## 附錄 A — 名稱對映速查（給執行者）

| 舊 | 新 |
|---|---|
| `ark-agent-builder` | `ark-agent-bot-builder` |
| `ark-kiro-init` | `ark-agent-init` |
| `ark-news-daily` | `ark-daily-news` |
| `ark-scheduler-generator` / `ark-telegram-bot` | `ark-webapp-generator`（三合一） |
| `ark-llm-cli` | `ark-agent-cli` |
| `ark-chatbot-generator` | 已移除，無對應 |
| `KIRO.md` | `CODE.md` |
| `build_agent.py` / `build_kiro.py` / `build_team.py` | 裝 wheel + 設定檔（無對應腳本） |
| `output/` | `artifacts/` |
| `knowledge/wiki/` | `knowledge/shared/wiki/` |

## 附錄 C — T6 重疊分析結果（2026-09-14）

用章節主題比對 `docs/quickstart-*` 與 `course-*` 教材：

| 文件 | 重疊主題 | 獨有主題 | 判定 |
|---|---|---|---|
| `docs/quickstart-ai-bot.md` | Agent · Skill · TG · Wiki · 啟動 · 知識（6） | 安裝 · 初始化 · 對話（4） | **保留，收窄定位**為「課前自學：從零到第一次對話」；重疊主題改為指向課堂教材 |
| `docs/quickstart-llm-wiki.md` | Wiki · 知識（2） | 安裝 · 初始化 · 匯入 · 查詢 · 對話（5） | **保留**：定位「知識庫的獨立使用」（不跑 bot），與第三堂的「知識庫 + Agent 迴圈」分工 |

**處置**（AC-6.2 的落實方式）：兩份都在開頭加「📍 這份文件的定位」區塊，
明寫重疊主題**以課堂教材為準**並附連結。不刪內容 —— 自學路徑仍要能一個人走完 ——
但「哪一份是真相」不再模糊。

> 💡 判準：重複本身不是問題，**沒有人知道哪一份是真的**才是。
> 目前 build-guide 與 QUICKSTART 對不上，根因就是同一件事寫了兩份且都沒標主從。

---

## 附錄 B — 實測基準（2026-09-14）

| 項目 | 值 | 來源 |
|---|---|---|
| `ark_bot_agent` | 1.0.16 | `projects/paddy-bot/.venv` import 版號 |
| `ark_team_agent` | 1.8.16 | 同上 |
| 套件開發源 | `projects/paddy-bot/src/` | editable 安裝 |
| 共用庫 active skill | 50 | `audit_skills.py` |
| website port | `health_port + 5000` | 套件 1.6.2 起 |
| 冷啟第二階段 | 2–4 分鐘 | 本機 market-team 實測 |

> 教材內文**不寫死版號**，只在本附錄與 README 的 baseline 區塊記一次。
