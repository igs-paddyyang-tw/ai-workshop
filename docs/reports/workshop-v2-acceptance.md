---
title: "AI Workshop v2 套件化翻新 — 驗收報告"
type: acceptance
status: complete
created: 2026-09-14
plan: ../plans/workshop-v2-plan.md
baseline: 987d00d
head: 0390331
---

# AI Workshop v2 套件化翻新 — 驗收報告

## 摘要

| 指標 | 值 |
|------|-----|
| 任務 | 13（T1–T13） |
| 完成 | 12 完成 · 1 部分完成（T13） |
| 驗收條件（AC） | 31 條 |
| 通過 | **28 ✅** · 3 ⚠️（需真人 / 需 Telegram token） |
| 通過率 | **90.3%** |
| commit | 13（`987d00d..0390331`） |
| 版控大小 | 9 MB → **2.29 MiB** |

### 一句話

教材從「用 scaffolder 產 2 萬行手搭架構」改為「裝 wheel + 寫設定檔」，
並先建守門再改內容 —— 守門在改動前是紅的（P0=47 P1=2），現在是綠的（P0=0 P1=0）。

---

## 任務結果

| # | 任務 | 狀態 | 關鍵驗證 |
|---|------|------|---------|
| T1 | 教材守門 `check_docs.py` | ✅ | 建立當下即抓到 P0=47 P1=2；24 條反證測試全過 |
| T2 | `samples/ai-bot` 重建 | ✅ | 9 agent 載入、12 skills、知識庫 17 頁、四層搜尋命中 |
| T3 | `samples/ai-team-agent` 重建 | ✅ | `/api/health` 200 `ok=true`、instances 2/2、sync `--check` rc=0 |
| T4 | 骨架三缺口 + 版控邊界 | ✅ | 實跑後零未追蹤檔案 |
| T5 | 課程 A 教材 | ✅ | course-ai-bot P0/P1 歸零 |
| T6 | quickstart 重疊收斂 | ✅ | 分析寫入 plan 附錄 C；兩份加定位聲明 |
| T7 | 課程 B 教材 | ✅ | Step 7 改 team.yaml 六區塊；troubleshooting 重寫 |
| T8 | README + bridge-diagram | ✅ | 五層架構 → 三層分工；skill 數校正為 50 |
| T9 | 講師手冊 + 共用資源 | ✅ | 課前 checklist + 三項風險處置 |
| T10 | ADR 與歷史資產 | ✅ | ADR-004 superseded；新增 ADR-005~008 |
| T11 | HTML 報告 | ✅ | 5 份加更新橫幅 + 修過時內容 |
| T12 | 全案守門與端到端 | ✅ | rc=0、反證雙向驗證、舊名殘留歸零 |
| T13 | 乾跑 | ⚠️ 部分 | 指令層乾跑完成；**真人五堂乾跑未執行** |

---

## 驗收條件明細

### ✅ 通過（28）

| AC | 內容 | 證據 |
|---|---|---|
| 1.1 | 守門在翻新前是紅的 | P0=47 P1=2（commit `c678cff` 當下） |
| 1.2 | 每條規則有反證測試 | `pytest scripts/tests/` 24 passed |
| 1.3 | `--help` 無副作用 | `test_help_has_no_side_effect`：空目錄跑完仍為空 |
| 1.4 | 掃到 0 個 → 失敗 | `scanned-zero` 兩條測試 |
| 2.1 | ai-bot requirements 只列 wheel | `ark_bot_agent[search,skills]` |
| 2.2 | ai-bot 無 runtime 模組 | `src/` 整個目錄已移除 |
| 2.4 | 無 skills 空注入假警報 | 啟動日誌無該警告 |
| 2.5 | 知識庫索引非空 + 查詢命中 | 17 頁；查「Ocean King 競品」命中 3 筆 |
| 3.1 | `group` + `kiro_files.skills.policy: skip` | team.yaml 已設 |
| 3.2 | `validate_team.py` 過 + 佔位符 0 | rc=0；殘留 0 |
| 3.3 | `/api/health` 200、instances ready | `ok:true`、running=2/alive=2 |
| 3.5 | `sync_skills.py --check` 一致 | 同步 58 個後 rc=0 |
| 4.1 | 三缺口目錄齊備 | 兩 sample × 4 目錄全 ✅ |
| 4.2 | 實跑後版控乾淨 | `git status --untracked=all` 空 |
| 5.1 | 課程 A 指令可執行 | broken-path 零命中 |
| 5.2 | course-ai-bot P0/P1 = 0 | 守門輸出 |
| 5.3 | 第二堂僅改路徑與清單 | 3 行 knowledge 路徑 |
| 6.1 | 重疊分析產出 | plan 附錄 C |
| 6.2 | 同一主題不存在兩份真相 | 兩份 quickstart 加「以課堂教材為準」 |
| 7.1 | 無 src/coordinator 等字樣 | grep 零命中 |
| 7.2 | 兩階段就緒有專節 | QUICKSTART-04 + build-guide + README + troubleshooting |
| 7.3 | course-ai-team-agent P0/P1 = 0 | 守門輸出 |
| 8.1 | README skill 數與 active 一致 | 50（並標明以守門輸出為準） |
| 8.2 | 快速開始指令可跑 | 見 §乾跑 |
| 9.1 | 三項風險有處置步驟 | 講師手冊「常見突發狀況」+ telegram-setup + env-check |
| 9.2 | 課前 checklist 第一項是守門 | ✅ |
| 10.1 | ADR append-only | ADR-004 本文一字未改 |
| 10.2 | 新 ADR 有 frontmatter | 4 篇 |
| 11.1 | HTML 無舊 skill 名 | 守門零命中 |
| 12.1 | 全案守門 rc=0 | 不接 pipe 直接看 rc |
| 12.2 | 反證雙向 | 植入→rc=1；移除→rc=0 |
| 12.4 | 舊名殘留僅在白名單 | 版控內 2 個真殘留已清（`settings/skills.json`） |

### ⚠️ 未完全達成（3）

| AC | 內容 | 為什麼 | 補做方式 |
|---|---|---|---|
| **2.3** | ai-bot 實跑到 **TG `/start` 有回應** | 需要一個 **Telegram Bot Token**。刻意**不借用**既有服務的 token —— 同一 token 兩處 polling 會隨機吃訊息且不報錯，會干擾本機在跑的 bot | 填 `.env` 後 `python start.py`，TG 打 `/start` |
| **3.4** | team 第二階段就緒（TG 私訊有回覆） | 同上 | 同上，等冷啟 2–4 分鐘 |
| **13.1/13.2** | 真人五堂乾跑 + 耗時記錄 | 需要一個人照教材從頭操作 50 min × 5 | 講師手冊已備「實際耗時記錄」表，開新班前補 |

> 🔴 **AC-12.3（從零實跑）只達成一半**：套件行為、設定解析、啟動流程、知識庫、
> daemon health 全部實測過；但「新 venv + 從 `.whl` 檔安裝」這一步沒做
> —— 本機沒有 wheel 檔（它在 GitHub Release）。
> **已改用可驗證的方式確認教材沒寫錯**：查套件 metadata 確認
> `ark_bot_agent` 真的有 `search` / `skills` 兩個 extras（教材寫的 `[search,skills]` 正確），
> `ark_team_agent` 沒有這兩個 extras（教材也沒要求它裝）。

---

## 乾跑（T13，指令層）

五堂 QUICKSTART 的 shell 指令共 **16 條**：

| 類別 | 條數 | 結果 |
|---|---|---|
| 可靜態驗證（cd / venv / cp / import / paths / sync / curl health） | 11 | ✅ 全部驗過 |
| 需真人或 token（pip install wheel / start.py / getUpdates / @BotFather） | 5 | ⚠️ 待真人 |

另外，第三堂的 Wiki API（`/api/v1/wiki/query` · `/ingest` · `/lint` · `/admin`）
經比對套件路由表**全部存在** —— 這批指令不需要改。

---

## 這次翻新真正解決的問題

| 現象 | 根因 | 處置 |
|---|---|---|
| 教材第一個指令就跑不起來 | scaffolder 於 2026-09-08 全面 v3.0 重寫，教材停在重寫前 | 主線改為三層分工 |
| sample 是 2 萬行手搭實作 | 那些能力已套件化 | 重建為消費端骨架（ADR-006） |
| 6 個 skill 名早已更名/移除 | 共用庫演化，教材沒跟上 | 全庫替換 + `dead-skill-ref` 守門 |
| 同一件事寫兩份且沒標主從 | build-guide vs QUICKSTART、skills.json vs 角色矩陣 | 標明主從 / 刪掉其中一份 |
| 課堂最難查的故障沒寫進教材 | token 互搶、冷啟 2–4 分鐘、extras 靜默降級 | 三項各有專節 + 講師手冊 |

> 💡 **沒有一條缺陷是「東西不見了」** —— 全部是兩份真相各自演化、對不上。
> 所以第一個任務是守門，不是改內容（ADR-008）。

---

## 後續建議

1. **開新班前**：跑一次真人乾跑，補講師手冊的耗時表（T13 剩項）
2. **wheel 發放**：確認 Release 有對應版本，並準備離線備援（USB / 區網）
3. **守門維護**：`check_docs.py` 的 `DEAD_SKILLS` 清單要隨共用庫更新（腳本頂部一處維護）
4. **選配**：把 `check_docs.py` 接進 CI（GitHub Actions 一個 job）
