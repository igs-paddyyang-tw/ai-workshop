# 🎓 講師指導手冊

> 課程 A（個體 Agent）+ 課程 B（Agent Team），共 5 堂。

---

## 課程 A — AI Agent 開發入門（3 堂 × 50 min）

### 教學目標

學員完成後能獨立建構「有人格 + 有技能 + 有記憶」的 AI Agent。

### 第一堂：Agent 初始（Phase 1, Step 0-3）

| 時間 | 動作 | 講師做什麼 |
|------|------|-----------|
| 0-5 | 環境確認 | 協助解決安裝問題 |
| 5-15 | build_agent.py 產出 | 展示產出結構，解釋各目錄用途 |
| 15-20 | ark-kiro-init --standalone | 解釋 .kiro/ 的意義 |
| 20-40 | ⭐ SOUL.md 設計 | 帶學員修改 SOUL，觀察風格變化 |
| 40-50 | 實測 + Q&A | /agents 切換，體驗不同人格 |

**教學重點**：
- SOUL.md 是 Agent 最重要的「靈魂」
- 同一套程式碼，不同 SOUL = 不同 Bot
- 讓學員動手改人格、觀察變化（互動式）

**常見問題**：
- Bot Token 錯誤 → 確認 @BotFather
- Gemini 429 → 等 1 分鐘重試
- Bot 沒回應 → 確認只有一個 instance 在跑

### 第二堂：Skills 開發（Phase 2, Step 4-7）

| 時間 | 動作 | 講師做什麼 |
|------|------|-----------|
| 0-5 | 回顧 Phase 1 | 確認 Bot 能跑 |
| 5-20 | ⭐ 拷問設計 | 帶學員被 AI 拷問，示範「主動參與」 |
| 20-30 | 產出 Spec | 展示 Spec 格式，解釋驗收條件 |
| 30-40 | 實作 Skill | 用 ark-skill-creator 產出 |
| 40-50 | 驗證 + Q&A | 跑 code-spec-validator，解讀 Drift Report |

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

學員完成後能管理「5 Agent 並行 + Dashboard + 費用控管」的完整平台。

### 第四堂：Agent Team（Phase 1, Step 0-4）

| 時間 | 動作 | 講師做什麼 |
|------|------|-----------|
| 0-10 | 環境確認 + build_team.py | 展示 110+ 檔案的產出 |
| 10-20 | build_kiro.py | 解釋 team.yaml + Agent 角色分工 |
| 20-30 | 設定 Telegram | 協助取得 user_id |
| 30-40 | ⭐ 啟動 + 派工 | /assign 實測，觀察 leader 拆任務 |
| 40-50 | 科技日報實戰 + Q&A | market + report 分工 |

**教學重點**：
- 課程 A 的 Agent 在 Team 裡「各就各位」
- build_team.py 一鍵 = 你在課程 A 手動做的 × 5
- 故障隔離：一個 Agent 掛不影響其他

**關鍵示範**：
- `/assign 寫 REST API` → 觀察 leader 派給 coder
- 同時 `/assign 抓新聞` → 觀察並行執行

### 第五堂：平台管理（Phase 2, Step 5-8）

| 時間 | 動作 | 講師做什麼 |
|------|------|-----------|
| 0-10 | API 探索 | 帶學員 curl 各端點 |
| 10-20 | Web Dashboard | 展示 KPI + Agent Grid |
| 20-35 | ⭐ 程式碼閱讀 | 打開 task_graph + discovery，對照派工行為 |
| 35-45 | 費用 + 排程 + 監控 | 展示 costs API、scheduler.yaml |
| 45-50 | 全系列回顧 + Q&A | 五堂課旅程總結 |

**教學重點**：
- 理解「背後在做什麼」比「會操作」更重要
- 四層架構：入口 → 協調 → 執行 → 知識
- 費用控管是生產環境必備

**收尾**：
- 學員帶走 `sample/ai-team-agent/`
- 選擇 team-ops 或 team-dev
- 鼓勵回家改 SOUL.md 自訂角色

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
| 全班環境裝不好 | 直接用 sample 體驗，跳過 build 步驟 |
| Gemini API 額度用完 | 切到 echo 模式先繼續，或共用一個 Key |
| 50 min 講不完 | 砍「選讀」步驟，保住 ⭐ 核心 |
| 學員程度差異大 | 快的人做「進階練習」，慢的人保底完成 ⭐ |

---

## 參考文件位置

| 文件 | 位置 |
|------|------|
| 課程 A 規格 | `course-a/build-guide.md` |
| 課程 B 規格 | `course-b/build-guide.md` |
| 體驗成品 | `sample/ai-bot/` + `sample/ai-team-agent/` |
| 銜接全覽 | `shared/bridge-diagram.md` |
