# AI Agent 機器人 — 簡易安裝與使用教學

> 10 分鐘建好一個有人格、有能力、有記憶的 AI Agent 系統，能上網搜尋產出競品分析。

---

## 前置條件

- Kiro IDE 已安裝並登入
- Python 3.12+
- Telegram Bot Token（從 @BotFather 取得）
- Gemini API Key（從 Google AI Studio 取得）

---

## 開始：初始化（一次貼完，AI 全部跑完）

啟動 Kiro IDE，開啟一個空資料夾，進入 Chat 對話框。

複製以下整段文字，貼到對話框送出：

```
1. 幫我下載 https://github.com/igs-paddyyang-tw/ai-workshop/tree/main/samples/ai-bot 的完整專案到當前目錄
2. 打開 .env.example 複製成 .env，讓我填 Token
3. 安裝 Python 套件（pip install -r requirements.txt）
```

> 💡 一段話 3 件事：下載專案 → 準備環境設定 → 安裝套件。
>
> AI 全部跑完後，你的資料夾就是完整的 8 Agent 系統。

完成後的專案結構：

```
your-project/
├── .kiro/steering/SOUL.md         ← 主 Agent 人格
├── .kiro/skills/                   ← 5 個技能（已內建）
├── agents/                         ← 8 個 Agent（各有人格+能力+知識）
│   ├── market-agent/              ← 市場研究員（能上網搜尋）
│   ├── admin-agent/               ← 通用助手
│   ├── coder-agent/               ← 程式開發
│   ├── data-agent/                ← 數據分析
│   ├── pm-agent/                  ← 產品企劃
│   ├── qa-agent/                  ← 品質測試
│   ├── report-agent/              ← 報告產出
│   └── ai-dev-agent/             ← AI 開發
├── knowledge/shared/wiki/          ← 共用知識庫（預裝 3 篇競品分析）
├── src/                            ← Bot 程式碼
├── .env                            ← 你的 Token（要填）
└── start.py                        ← 啟動入口
```

| 已內建 | 說明 |
|--------|------|
| 5 個 IDE 技能 | 知識庫管理、拷問設計、規格書、Skill 產出、品質驗證 |
| 8 個 Agent | 各有不同人格和專長，TG 可切換 |
| 3 篇知識 | Ocean King、Super Ace、捕魚機 vs 老虎機比較 |

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

目錄重點：
- `.kiro/skills/` — 5 個根目錄 Skill（IDE 開發用）：ark-wiki-engine、ark-grill-me、ark-superpowers、ark-skill-creator、ark-code-spec-validator
- `agents/*/` — 每個 Agent 有自己的 `.kiro/steering/SOUL.md` + `.kiro/skills/` + `knowledge/`
- `knowledge/shared/` — 所有 Agent 共用的知識庫（raw/ → wiki/）
- `.kiro/steering/SOUL.md` — 三層架構：靈魂（SOUL）= 人格、能力（SKILL）= SOP、記憶（WIKI）= 知識庫

</details>

---

## Step 1：IDE 對話 — 了解 Agent 系統

在 Kiro IDE 對話框貼：

```
這個專案有哪些 Agent？各自是什麼角色？能做什麼？
```

✅ 預期：Kiro 列出 8 個 Agent，各自的身份和專長

📝 再問：

```
這個系統的三層架構是什麼？SOUL、SKILL、WIKI 分別是什麼意思？
```

✅ 預期：

| 層 | 是什麼 | 改了會怎樣 |
|----|--------|-----------|
| SOUL（靈魂） | Agent 的人格定義 | 改語氣/風格 → 行為馬上變 |
| SKILL（能力） | Agent 的 SOP 流程 | 加 Skill → 新功能就有 |
| WIKI（記憶） | Agent 的知識庫 | 加知識 → 回答更準 |

📝 看看知識庫有什麼：

```
知識庫裡目前有哪些內容？
```

✅ 預期：3 篇 — Ocean King 分析、Super Ace 分析、捕魚機 vs 老虎機比較

<details>
<summary>💻 技術補充（軟體人員）</summary>

```
# Agent 人格定義檔
agents/market-agent/.kiro/steering/SOUL.md

# Agent 專屬技能
agents/market-agent/.kiro/skills/ark-market-research/SKILL.md

# 共用知識庫
knowledge/shared/wiki/ocean-king-analysis.md
knowledge/shared/wiki/super-ace-analysis.md
knowledge/shared/wiki/fishing-vs-slot-comparison.md

# 根目錄 5 個 IDE Skill
.kiro/skills/ark-wiki-engine/SKILL.md      → 知識庫 ingest/query/lint
.kiro/skills/ark-grill-me/SKILL.md         → 拷問設計
.kiro/skills/ark-superpowers/SKILL.md      → 規格書產出
.kiro/skills/ark-skill-creator/SKILL.md    → 新 Skill 建立
.kiro/skills/ark-code-spec-validator/SKILL.md → 品質驗證打分
```

</details>

---

## Step 2：啟動機器人

📝 在 Kiro IDE 對話框貼：

```
幫我啟動 Bot（執行 python start.py）
```

或直接在終端：

```bash
python start.py
```

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

⚠️ Tier 1 顯示 ❌ → 確認 TELEGRAM_BOT_TOKEN 正確
⚠️ Tier 2 顯示 ⬚ → 確認 GEMINI_API_KEY 正確

<details>
<summary>💻 技術補充（軟體人員）</summary>

```bash
# 完整啟動流程
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python start.py

# 3 個 Tier 說明：
# Tier 0: 純本地功能（Skills + Wiki + API）— 永遠可用
# Tier 1: 需要 TELEGRAM_BOT_TOKEN — Bot 連線
# Tier 2: 需要 GEMINI_API_KEY — AI 推理 + RAG 搜尋

# Web 介面同時啟動：http://localhost:8000
```

</details>

---

## Step 3：IDE 對話 — Market Agent 上網搜尋

📝 在 Kiro IDE 對話框貼：

```
用 market-agent 的人格和能力，上網搜尋 2025 年老虎機市場最新動態，產出競品情報摘要
```

✅ 預期：Market Agent 上網搜尋 → 產出結構化情報

```
🗺️ 市場情報
├── 主題: 2025 老虎機市場動態
├── 發現:
│   1. [高信心] Pragmatic Play 推出新系列...
│   2. [中信心] PG Soft 亞洲市佔持續成長...
├── 來源: Google Search + 產業新聞
└── 建議: 關注 xxx 趨勢
```

📝 試試結合知識庫：

```
用 market-agent 搜尋最新資料，比較 Ocean King 系列跟 2025 年新進捕魚機的優劣
```

✅ 預期：引用 wiki 裡的 Ocean King 知識 + 搜尋網路新資料 → 整合比較分析

> 💡 **IDE 驗證 = 秒回、不重啟。確認 Agent 搜得到、引用得到 → 再去 TG 體驗。**

<details>
<summary>💻 技術補充（軟體人員）</summary>

Market Agent 的搜尋流程：
1. 讀取 `agents/market-agent/.kiro/steering/SOUL.md`（人格）
2. 讀取 `agents/market-agent/.kiro/skills/ark-market-research/SKILL.md`（SOP）
3. 執行 web_search 工具 → 多源搜尋
4. 查詢 `knowledge/shared/wiki/`（RAG 知識召回）
5. 依 SKILL.md 的輸出格式組裝情報摘要

```bash
# 也可以用 API 確認 Wiki 搜尋正常
curl -X POST http://localhost:8000/api/v1/wiki/query \
  -H "Content-Type: application/json" \
  -d '{"q":"Ocean King"}'
```

</details>

---

## Step 4：TG 對話 — Market Agent 產出競品分析

📱 Telegram 操作：

1. 對 Bot 發送 `/start` → 收到歡迎訊息 ✅
2. 發送 `/agents` → 出現 8 個 Agent 按鈕
3. 點選「🗺️ Market」切換到市場研究員
4. 發送：

```
幫我搜尋 2025 年老虎機市場最新動態，產出競品情報摘要
```

✅ 預期：跟 IDE 一樣的結構化情報（但這次是 Telegram 介面）

📱 再試結合 Wiki：

```
Ocean King 跟 2025 年新進的捕魚機比，有什麼優劣？
```

✅ 預期：引用知識庫 + 網路搜尋 → 整合比較（附 📚 參考來源）

> 💡 **IDE = 你的工作台。TG = 使用者的介面。** 兩邊問同一個問題，得到同等品質的回答。

<details>
<summary>💻 技術補充（軟體人員）</summary>

TG 對話流程（內部）：
1. 使用者訊息 → Bot 接收
2. Planner 判斷意圖 → 路由到 market-agent
3. 載入 SOUL.md（人格）+ SKILL.md（SOP）
4. Gemini + web_search + Wiki RAG → 產出回答
5. Telegram 回傳

切換 Agent 機制：`/agents` 指令 → InlineKeyboard → 切換 session 的 active_agent

</details>

---

## 日常使用

| 你想做什麼 | 在 Kiro IDE 說 |
|-----------|---------------|
| 增加知識 | 「搜尋 XXX，整理成知識存到 knowledge/shared/raw/ 並匯入 wiki」 |
| 改 Agent 語氣 | 「把 market-agent 的 SOUL 改成分析師簡報風格」 |
| 拷問設計 | 「拷問我的設計：我想加一個每日新聞推播功能」 |
| 產出新 Skill | 「根據拷問結果寫 spec，然後建立 Skill」 |
| 檢查知識品質 | 「檢查 knowledge/shared/wiki/ 健康度」 |

| 你想做什麼 | 在 Telegram 說 |
|-----------|---------------|
| 切換 Agent | `/agents` → 點按鈕 |
| 問知識庫 | 直接問問題（會自動引用 wiki） |
| 請 Market 搜尋 | 切到 Market → 「搜尋 XXX」 |

---

## 卡關排除

| 問題 | 解法 |
|------|------|
| Bot 無回應 | 確認 `.env` 的 TELEGRAM_BOT_TOKEN 正確 |
| Tier 2 顯示 ⬚ | 確認 GEMINI_API_KEY 正確且有額度 |
| Market 搜不到東西 | 確認網路正常 + Gemini Key 有效 |
| 回答沒引用知識 | 確認 `knowledge/shared/wiki/` 有檔案 |
| `ModuleNotFoundError` | `pip install -r requirements.txt` |

---

## 知識成長循環

Bot 上線後，持續餵它知識讓它越來越聰明：

```
你丟素材（raw/）→ AI 整理（wiki/）→ Agent 引用回答
     ↑                                      │
     └──── 你覺得缺什麼就再丟 ←────────────┘
```

📝 隨時在 Kiro IDE 說：

```
幫我搜尋「XXX」，整理成知識文件存到 knowledge/shared/raw/ 並匯入 wiki
```

知識越多 → 回答越準 → 你越信任 → 丟更多 → ♻️

---

## 總結

```
初始化：一次貼完，下載 + 設定 + 安裝
Step 1：IDE 對話了解 Agent 系統（SOUL + SKILL + WIKI）
Step 2：啟動機器人
Step 3：IDE 對話 Market Agent 上網搜尋產出競品
Step 4：TG 對話 Market Agent 驗證同樣結果
```

**全程對話操作，不需要手寫程式碼。**

> 🔗 進階課程：[01-Agent 人格設計](../course-ai-bot/QUICKSTART-01-agent.md) / [02-Skills 開發](../course-ai-bot/QUICKSTART-02-skills.md) / [03-Wiki 知識庫](../course-ai-bot/QUICKSTART-03-wiki.md)
