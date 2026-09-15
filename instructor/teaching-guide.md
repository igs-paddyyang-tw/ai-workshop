# 🎓 講師指導手冊

> 課程 A（個體 Agent）+ 課程 B（Agent Team），共 5 堂。

---

## ✅ 開課前 Checklist（做完再進教室）

| # | 項目 | 怎麼確認 |
|---|------|---------|
| 1 | **教材守門是綠的** | `python3 scripts/check_docs.py`（看 rc，**不接 pipe**） |
| 2 | 兩個 wheel 已下載 | `ls ark_*.whl` |
| 2b | **學員課前跑過 `./create.sh`**（或直接用 samples） | 他們的目錄有 `.venv` 且 `import` 驗得過 |
| 3 | **每位學員有自己的 TG Bot Token** | 報名表收集；🔴 絕不共用（見下） |
| 4 | 教室網路可連 api.telegram.org 與 Gemini | 課前實測一次 |
| 5 | 離線備援：wheel 放 USB / 區網 | Release 下載不到時的 Plan B |
| 6 | 自己完整跑過一次 01→05 | 每堂實際耗時記在下方時間表 |

> 🔴 **第 3 項不是形式**。同一個 token 在兩台電腦 polling 會**隨機**吃掉對方的訊息，
> 而且兩邊都不報錯 —— 全班共用一個 token 會製造一整堂課查不出來的「有時候會回」。

## 課程 A — AI Agent 開發入門（3 堂 × 50 min）

### 教學目標

學員完成後能獨立建構「有人格 + 有技能 + 有記憶」的 AI Agent。

### 第一堂：Agent 初始（Phase 1, Step 0-3）

| 時間 | 動作 | 講師做什麼 |
|------|------|-----------|
| 0-5 | 環境確認 + 裝 wheel | 協助安裝問題；**強調 extras `[search,skills]` 不可省** |
| 5-15 | 探索三個設定檔 | agents.yaml / bot.yaml / SOUL.md —— 專案裡沒有 runtime |
| 15-20 | ark-agent-init 產人格 | 解釋 `.kiro/steering/` 與多 CLI 入口 |
| 20-40 | ⭐ SOUL.md 設計 | 帶學員修改 SOUL，觀察風格變化 |
| 40-50 | 實測 + Q&A | /agents 切換，體驗不同人格 |

**教學重點**：
- SOUL.md 是 Agent 最重要的「靈魂」
- 同一套程式碼，不同 SOUL = 不同 Bot
- 讓學員動手改人格、觀察變化（互動式）

**常見問題**：
- Bot Token 錯誤 → 確認 @BotFather；`InvalidToken` 多半是 `.env` 還是 `your_token`
- Gemini 429 → 等 1 分鐘重試
- **Bot 有時回有時不回** → 🔴 同一 token 有第二處在 polling（最難查的一種）
- 搜尋品質怪 → wheel 沒帶 `[search]` extras，靜默降級了
- `ModuleNotFoundError: ark_bot_agent` → 驗 `python -c "import ark_bot_agent"`，不看 pip 輸出

### 第二堂：Skills 開發（Phase 2, Step 4-7）

| 時間 | 動作 | 講師做什麼 |
|------|------|-----------|
| 0-5 | 回顧 Phase 1 | 確認 Bot 能跑 |
| 5-20 | ⭐ 拷問設計 | 帶學員被 AI 拷問，示範「主動參與」 |
| 20-30 | 產出 Spec | 展示 Spec 格式，解釋驗收條件 |
| 30-40 | 實作 Skill | 用 ark-skill-creator 產出 |
| 40-45 | 驗證 | 跑 code-spec-validator，解讀 Drift Report |
| 45-50 | TG 驗證 + Q&A | 對比「有 Skill / 沒 Skill」的輸出差異 |

> ⏱️ 本堂原本排到 55 分（超時）。壓縮點在 Step 3 ——
> **AI 產 Spec 很快，慢的是人審**。時間不夠砍 Step 3 細節，**絕不砍拷問**。

**教學重點**：
- Spec-Driven = 先想清楚再寫（不是先寫再改）
- 拷問時「不要全部 OK」— 主動質疑
- Score ≥ 90 才能 Ship

**反模式提醒**：
- ❌ 跳過拷問直接寫
- ❌ Spec 太簡略
- ❌ 從不驗證

### 第三堂：LLM Wiki（Phase 3, Step 8-10）

| 時間 | 動作 | 講師做什麼 |
|------|------|-----------|
| 0-5 | 回顧 Phase 1-2 | Skills 能觸發、Bot 有人格 |
| 5-15 | 匯入知識 | 帶學員把文件丟進 raw/，觸發 ingest |
| 15-30 | ⭐ RAG 問答 | 問問題 → 觀察引用 → 比較有/無 Wiki 的差異 |
| 30-40 | Lint + 圖譜 | 展示 wikilink、孤立頁面 |
| 40-50 | 自演化循環 + Q&A | 解釋 memory → raw → wiki 的成長循環 |

**教學重點**：
- Agent 會「越用越聰明」（自演化）
- raw/ 是人類丟進來的，wiki/ 是 AI 整理的
- 每次對話後 memory.py 自動寫入 → 知識累積

---

## 課程 B — AI Agent Team 實戰（2 堂 × 50 min）

### 教學目標

學員完成後能管理「8 Agent 常駐 + 排程 + 費控 + 知識迴圈」的完整團隊。

### 第四堂：Agent Team（Phase 1, Step 0-4）

| 時間 | 動作 | 講師做什麼 |
|------|------|-----------|
| 0-10 | 啟動 + **等冷啟** | 🔴 先講兩階段就緒；等待的 2–4 分鐘拿來講 `group` vs `group_members` |
| 10-20 | ⭐ 讀 team.yaml 六區塊 | instances / group / access / cost_guard / hang_detector / kiro_files |
| 20-30 | ⭐ 修改團隊配置 | 加一個 agent，觀察 log 有沒有「欄位不存在」 |
| 30-42 | 派工驗證 | `/assign` 與自然語言派工 |
| 42-50 | 新 Agent 複合任務 + Q&A | market + report 分工 |

> ⏱️ **裝 wheel 與 `sync_skills.py` 移到課前**（用 `create.sh` 一鍵完成）。
> 課堂第 0 分鐘就是 `python start.py` —— 裝機不該吃掉核心時間。

**教學重點**：
- 課程 A 的**人格資產可以直接搬過來**（兩邊 SOUL.md 同形狀）
- **`team.yaml` 就是架構** —— 套件化後，架構的決定全在設定裡
- 🔴 **`group` vs `group_members`**：寫錯套件靜默忽略，只在 log 印一行。
  這是本課最值得帶走的一課：**設定類系統最危險的失敗不是報錯，是沒生效**
- 故障隔離：一個 Agent 掛不影響其他

**⏱️ 一定要先講的事（否則會被當成故障）**：
| 現象 | 真相 |
|---|---|
| 啟動後私訊沒回 | kiro-cli 冷啟 **2–4 分鐘**，訊息在佇列裡沒掉 |
| `/health` 404 | team 套件是 `/api/health` |
| 看板打不開 | 在 `health_port + 5000`（23050 → 28050） |

**關鍵示範**：
- `/assign 寫 REST API` → 觀察 leader 派給 coder
- 同時 `/assign 抓新聞` → 觀察並行執行

### 第五堂：營運落地 — 它能「自己跑」

| 時間 | 動作 | 講師做什麼 |
|------|------|-----------|
| 0-10 | ⭐ 設定排程 | 帶學員用 Kiro 加 scheduler.yaml（日報+週報） |
| 10-18 | 設定費控 | 帶學員改 cost_guard 5.0，解釋超額機制 |
| 18-22 | 重啟確認 | Kiro 確認排程已註冊 |
| 22-32 | 觸發排程 | Kiro 手動觸發 → TG 看結果 → /board + /costs |
| 32-42 | ⭐ 迴圈體驗 | 確認 raw/ → ingest → TG 問到引用 → 加 ingest 排程 |
| 42-50 | 上線 Checklist | Kiro 產出遊戲部門 Checklist + 收尾 |

**教學重點**：
- 04 手動派工 → 05 排程自動 = Demo → 正式上線
- Step 5 是迴圈體驗關鍵：學員要「動手 ingest + 問到引用」才算體驗到
- 排程產出自動進 knowledge/raw/ → ingest → Wiki 成長 = 自演化
- 最後加 ingest 排程 = 迴圈完全自動化

**收尾**：
- 學員帶走 `samples/ai-team-agent/`
- 改 team.yaml + scheduler.yaml 直接用在業務
- 所有排程產出自動累積成知識 = 系統自己在成長

---

## 教學節奏建議

| 原則 | 說明 |
|------|------|
| 先體驗再講 | 每堂開頭跑 sample，讓學員先「有感覺」 |
| 動手 > 聽講 | 50 min 中至少 30 min 是學員操作 |
| 一個核心 | 每堂只有一個 ⭐ 重點，其他是鋪墊 |
| 瓶頸引出需求 | Phase 1 結尾讓學員感受「能力有限」→ 自然引出 Phase 2 |

## 常見突發狀況

| 問題 | 處理 |
|------|------|
| 全班環境裝不好 | 直接用 sample 體驗，跳過安裝步驟 |
| **有人 Bot 時好時壞** | 🔴 查是不是兩個人用同一個 token（或同一人開了兩個 instance）——
  它**不報錯**，只會隨機吃訊息 |
| **第四堂啟動後全班說「壞了」** | 正常：kiro-cli 首次冷啟 2–4 分鐘。請學員看
  `/api/health` 的 `instances.running`，或 `cat /proc/<pid>/stat` 看 CPU 時間 |
| **搜尋結果很差 / 排程沒跑** | wheel 沒帶 extras（`[search,skills]`）——
  它只印一行 WARNING，不會擋啟動 |
| 下載不到 wheel | 用課前備好的 USB / 區網副本 |
| Gemini API 額度用完 | 切到 agent 模式（走 CLI backend，零 API 費用）繼續 |
| 50 min 講不完 | 砍「選讀」步驟，保住 ⭐ 核心 |
| 學員程度差異大 | 快的人做「進階練習」，慢的人保底完成 ⭐ |

---

## 參考文件位置

| 文件 | 位置 |
|------|------|
| 課程 A 規格 | `course-ai-bot/build-guide.md` |
| 課程 B 規格 | `course-ai-team-agent/build-guide.md` |
| 體驗成品 | `samples/ai-bot/` + `samples/ai-team-agent/` |
| 銜接全覽 | `shared/bridge-diagram.md` |
| 故障排除 | `course-ai-team-agent/troubleshooting.md` |
| 教材守門 | `scripts/check_docs.py`（改完教材必跑） |

---

## 📋 實際耗時記錄（乾跑後填）

| 堂 | 設計時長 | 實際耗時 | 卡點 |
|---|---|---|---|
| 01 | 50 min | | |
| 02 | 50 min | | |
| 03 | 50 min | | |
| 04 | 50 min | | |
| 05 | 50 min | | |

> 💡 這張表空著就代表**沒有人從頭跑過一次**。開新班前務必補上。
