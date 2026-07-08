# AI Agent 機器人 — 簡易安裝與使用教學

> 10 分鐘建好一個有人格、有能力、有記憶的 AI Agent 系統，能上網搜尋產出競品分析。

---

## 前置條件

- Kiro IDE 已安裝並登入
- Python 3.12+
- Telegram Bot Token（從 @BotFather 取得）
- Gemini API Key（從 Google AI Studio 取得）

---

## 初始化（一次貼完，AI 全部跑完）

啟動 Kiro IDE，開啟一個空資料夾，進入 Chat 對話框。

複製以下整段文字，貼到對話框送出：

```
1. 幫我下載 https://github.com/igs-paddyyang-tw/ai-workshop/tree/main/samples/ai-bot 的完整專案到當前目錄
2. 打開 .env.example 複製成 .env，讓我填 Token
3. 安裝 Python 套件（pip install -r requirements.txt）
```

> 💡 一段話 3 件事：下載專案 → 準備環境設定 → 安裝套件。

📝 填入你的 Token — 打開 `.env`：

```
TELEGRAM_BOT_TOKEN=你的_Token
GEMINI_API_KEY=你的_Key
```

> ✏️ 沒有 Token？Telegram 搜尋 @BotFather → `/newbot` → 取得 Token。
> Gemini Key 到 https://aistudio.google.com 申請。

<details>
<summary>💻 技術補充（軟體人員）</summary>

```bash
git clone https://github.com/igs-paddyyang-tw/ai-workshop.git
cd ai-workshop/samples/ai-bot
cp .env.example .env
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

專案結構：
```
samples/ai-bot/
├── .kiro/steering/SOUL.md         ← 主 Agent 人格
├── .kiro/skills/                   ← 5 個 IDE 技能（已內建）
│   ├── ark-wiki-engine/           ← 知識庫管理（ingest/query/lint）
│   ├── ark-grill-me/              ← 拷問設計
│   ├── ark-superpowers/           ← 規格書產出
│   ├── ark-skill-creator/         ← Skill 建立
│   └── ark-code-spec-validator/   ← 品質驗證
├── agents/                         ← 8 個 Agent（各有 SOUL + Skills + Wiki）
├── knowledge/shared/               ← 共用知識庫（預裝 3 篇競品分析）
├── src/                            ← Bot 程式碼
└── start.py                        ← 啟動入口
```

</details>

---

## Step 1：認識 Agent — 你是誰？你會什麼？你知道什麼？

在 Kiro IDE 對話框，依序問三個問題：

### 你是誰？

📝 貼到對話框：

```
你是誰？介紹一下你自己
```

✅ 預期：Agent 自我介紹 — 通用 AI 助手，簡潔直接，善於歸納重點

### 你會什麼？

📝 貼到對話框：

```
你會什麼？列出你的技能
```

✅ 預期：列出 5 個技能

| 技能 | 做什麼 |
|------|--------|
| 知識庫管理 | 匯入素材、查詢知識、健康檢查 |
| 拷問設計 | 逼你想清楚需求再動手 |
| 規格書產出 | 把決策寫成可驗證的文件 |
| Skill 產出 | 依規格建立新能力 |
| 品質驗證 | 打分數，確認做的跟規格一致 |

### 你知道什麼？

📝 貼到對話框：

```
你知道什麼？知識庫裡有哪些資料？
```

✅ 預期：3 篇預裝知識 — Ocean King 分析、Super Ace 分析、捕魚機 vs 老虎機比較

> 💡 三問三答，你已經認識了三層架構：
> - **你是誰** = SOUL（靈魂）
> - **你會什麼** = SKILL（能力）
> - **你知道什麼** = WIKI（記憶）

<details>
<summary>💻 技術補充（軟體人員）</summary>

```
# 人格定義
.kiro/steering/SOUL.md                          ← 主 Agent
agents/market-agent/.kiro/steering/SOUL.md      ← Market Agent

# 技能定義（Markdown SOP）
.kiro/skills/ark-wiki-engine/SKILL.md
.kiro/skills/ark-grill-me/SKILL.md
agents/market-agent/.kiro/skills/ark-market-research/SKILL.md

# 知識庫
knowledge/shared/wiki/ocean-king-analysis.md
knowledge/shared/wiki/super-ace-analysis.md
knowledge/shared/wiki/fishing-vs-slot-comparison.md
```

</details>

---

## Step 2：啟動機器人

📝 在 Kiro IDE 對話框貼：

```
幫我啟動 Bot（執行 python start.py）
```

或直接在終端：`python start.py`

✅ 看到以下 = 成功：

```
══════════════════════════════════════════════════
  🤖 課程 A — 個體 Agent
══════════════════════════════════════════════════
  Tier 0: ✅ Skills + Wiki + API（永遠可用）
  Tier 1: ✅ Telegram Bot
  Tier 2: ✅ Gemini AI + RAG
══════════════════════════════════════════════════
  📦 Skills: 5 個
  📚 知識庫: 3 篇
  🧠 SOUL: ✅ 已載入
  🤖 Bot: @your_bot_name 已連線
══════════════════════════════════════════════════
```

⚠️ Tier 1 ❌ → 確認 TELEGRAM_BOT_TOKEN
⚠️ Tier 2 ⬚ → 確認 GEMINI_API_KEY

<details>
<summary>💻 技術補充（軟體人員）</summary>

```bash
python3 -m venv .venv && source .venv/bin/activate
python start.py

# Tier 說明：
# Tier 0: 純本地（Skills + Wiki + API）— 永遠可用
# Tier 1: 需要 TELEGRAM_BOT_TOKEN
# Tier 2: 需要 GEMINI_API_KEY — AI 推理 + 上網搜尋

# Web 介面：http://localhost:8000
```

</details>

---

## Step 3：IDE 給任務 — 產出競品報告

### 3.1 請 Market Agent 搜尋 + 產出報告

📝 貼到對話框：

```
用 market-agent 的角色，上網搜尋 2025 年老虎機市場最新動態，
產出一份競品分析報告，存成 knowledge/shared/raw/slot-market-2025.md
```

✅ 預期：Market Agent 上網搜尋 → 整理成結構化報告 → 存到 raw/

### 3.2 匯入知識庫

📝 貼到對話框：

```
把 knowledge/shared/raw/slot-market-2025.md 匯入 wiki
```

✅ 預期：

```
✅ 匯入完成：1 篇
• slot-market-2025.md → knowledge/shared/wiki/slot-market-2025.md
```

### 3.3 確認 Agent 能引用新知識

📝 貼到對話框：

```
2025 年老虎機市場有什麼新趨勢？
```

✅ 預期：引用剛才產出的報告回答（附 📚 參考來源）

> 💡 **完整循環：搜尋 → 產出報告 → 存 raw → 匯入 wiki → Agent 能引用。**
> 知識庫又長了一篇，以後問市場問題回答更準。

<details>
<summary>💻 技術補充（軟體人員）</summary>

Market Agent 搜尋流程：
1. 讀取 `agents/market-agent/.kiro/steering/SOUL.md`（人格：像調查記者）
2. 讀取 `agents/market-agent/.kiro/skills/ark-market-research/SKILL.md`（SOP：多源搜尋→交叉驗證→摘要）
3. 執行 web_search → 多源搜尋
4. 依 SOP 產出結構化報告（含來源標注）
5. 存檔到 `knowledge/shared/raw/`

匯入流程（ark-wiki-engine）：
1. 讀取 raw/ 的 .md
2. 自動補 frontmatter（title/type/tags/created/updated）
3. 存到 wiki/
4. 更新 index.md + log.md
5. 重建搜尋索引

```bash
# API 確認
curl -X POST http://localhost:8000/api/v1/wiki/query \
  -H "Content-Type: application/json" \
  -d '{"q":"2025 老虎機市場"}'
```

</details>

---

## Step 4：TG 對話 — 兩種使用方式

📱 Telegram 打開你的 Bot：

1. 發送 `/start` → 收到歡迎訊息 ✅
2. 發送 `/agents` → 點選「🗺️ Market」

### 案例 A：問知識庫（引用已有知識）

📱 發送：

```
Ocean King 跟 Super Ace 比較，各自優劣是什麼？
```

✅ 預期：引用 wiki 裡的知識 → 結構化比較 → 附 📚 參考來源

> 💡 這是問「它已經知道的」— 回答快、有依據。

### 案例 B：上網搜尋（即時找新資料）

📱 發送：

```
幫我搜尋 PG Soft 2025 年有什麼新遊戲上線
```

✅ 預期：Market Agent 上網搜尋 → 產出情報摘要（含來源連結）

> 💡 這是問「它不知道的」— Agent 自己去網路找 → 產出新情報。

### 兩種的差異

| | 案例 A（問知識庫） | 案例 B（上網搜尋） |
|---|---|---|
| 來源 | knowledge/wiki/ | 網路即時搜尋 |
| 速度 | 快（本地查詢） | 較慢（要上網） |
| 標記 | 📚 參考：wiki 頁面 | 🔗 來源：網址 |
| 適合 | 問已整理的知識 | 找最新動態 |

<details>
<summary>💻 技術補充（軟體人員）</summary>

TG 內部流程：
1. 使用者訊息 → Planner 判斷意圖
2. 意圖 = 知識問答 → Wiki RAG 搜尋 `knowledge/shared/wiki/` → 回答
3. 意圖 = 需要最新資料 → web_search 工具 → 搜尋 → 格式化回答
4. Market Agent 的 SOUL 決定回答風格（資訊必須有來源）

Agent 切換：`/agents` → InlineKeyboard → 切換 session.active_agent
每個 Agent 讀自己的 SOUL.md，所以回答風格不同。

</details>

---

## 日常使用

| 你想做什麼 | 在 Kiro IDE 說 |
|-----------|---------------|
| 增加知識 | 「搜尋 XXX，產出報告存到 raw/ 並匯入 wiki」 |
| 改 Agent 語氣 | 「把 market-agent 改成簡報風格」 |
| 拷問設計 | 「拷問我的設計：我想加一個每日推播功能」 |
| 產出新 Skill | 「根據拷問結果寫 spec，然後建立 Skill」 |

| 你想做什麼 | 在 Telegram 說 |
|-----------|---------------|
| 切換 Agent | `/agents` → 點按鈕 |
| 問知識庫 | 直接問（會引用 wiki） |
| 找新資料 | 「搜尋 XXX」 |

---

## 卡關排除

| 問題 | 解法 |
|------|------|
| Bot 無回應 | 確認 TELEGRAM_BOT_TOKEN 正確 |
| 搜不到東西 | 確認網路正常 + GEMINI_API_KEY 有效 |
| 回答沒引用知識 | 確認 `knowledge/shared/wiki/` 有檔案 |
| `ModuleNotFoundError` | `pip install -r requirements.txt` |

---

## 知識成長循環

```
搜尋新資料 → 產出報告（raw/）→ 匯入 wiki → Agent 能引用
     ↑                                          │
     └──────── 你覺得缺什麼就再搜 ←────────────┘
```

**全程對話操作，不需要手寫程式碼。**

> 🔗 進階課程：[01-Agent 人格設計](../course-ai-bot/QUICKSTART-01-agent.md) / [02-Skills 開發](../course-ai-bot/QUICKSTART-02-skills.md) / [03-Wiki 知識庫](../course-ai-bot/QUICKSTART-03-wiki.md)
