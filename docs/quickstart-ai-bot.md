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
│   ├── ark-wiki-engine/           ← 知識庫管理
│   ├── ark-grill-me/              ← 拷問設計
│   ├── ark-superpowers/           ← 規格書產出
│   ├── ark-skill-creator/         ← Skill 建立
│   └── ark-code-spec-validator/   ← 品質驗證
├── agents/                         ← 8 個 Agent（各有 SOUL + Skills + Wiki）
├── knowledge/shared/               ← 共用知識庫（7 篇）
├── src/                            ← Bot 程式碼
└── start.py                        ← 啟動入口
```

</details>

---

## Step 1：認識 Agent — 你是誰？你會什麼？你知道什麼？

在 Kiro IDE 對話框，像跟新同事聊天一樣問：

### 你是誰？

📝 貼到對話框：

```
你是誰？介紹一下你自己
```

✅ 預期：Agent 自我介紹 — AI Agent 開發助手，專精 Agent 架構設計、記憶系統、Skill 機制

### 你會什麼？

📝 貼到對話框：

```
你會什麼？列出你的技能
```

✅ 預期：列出技能清單

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

✅ 預期：40 篇知識（共用 7 篇 + 8 個 Agent 各自的私有知識 33 篇），包含 Ocean King 分析、Super Ace 分析、團隊角色、溝通規範等

> 💡 三問三答，你已經認識了三層架構：
> - **你是誰** = 靈魂（SOUL）
> - **你會什麼** = 能力（SKILL）
> - **你知道什麼** = 記憶（WIKI）

<details>
<summary>💻 技術補充（軟體人員）</summary>

三層對應的檔案位置：
```
SOUL  → .kiro/steering/SOUL.md（改人格 = 行為變）
SKILL → .kiro/skills/*/SKILL.md（加 Skill = 新功能）
WIKI  → knowledge/shared/wiki/*.md（加知識 = 回答更準）
```

每個 Agent 都有自己的三層：
```
agents/market-agent/
├── .kiro/steering/SOUL.md              ← 市場研究員人格
├── .kiro/skills/ark-market-research/   ← 多源搜尋 SOP
└── knowledge/wiki/                     ← Agent 專屬知識
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
  🤖 AI Agent 專家開發平台
══════════════════════════════════════════════════
  Tier 0: ✅ Skills + Wiki + API（永遠可用）
  Tier 1: ✅ Telegram Bot
  Tier 2: ✅ Gemini AI + RAG
══════════════════════════════════════════════════
  📦 Skills: 5 個
  📚 知識庫: 40 篇
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
# Tier 1: 需要 TELEGRAM_BOT_TOKEN — Bot 連線
# Tier 2: 需要 GEMINI_API_KEY — AI 推理 + 上網搜尋

# Web 介面：http://localhost:8000
```

</details>

---

## Step 3：IDE 對話 — 問問題 + 給任務

直接問，不需要指定 Agent 或路徑。像跟同事說話一樣。

### 問它知道的事

📝 貼到對話框：

```
Ocean King 跟 Super Ace 比較，哪個比較好？
```

✅ 預期：引用知識庫回答 + 附 📚 參考來源

### 請它去查新資料

📝 貼到對話框：

```
幫我查一下 2025 老虎機市場有什麼新動態
```

✅ 預期：上網搜尋 → 整理出重點摘要

### 把結果存進知識庫

📝 貼到對話框：

```
把剛才查到的結果整理成一份報告，存進知識庫
```

✅ 預期：

```
✅ 已存入知識庫：slot-market-2025.md
```

### 確認知識長了

📝 貼到對話框：

```
現在知識庫有幾篇？比剛才多了什麼？
```

✅ 預期：41 篇（原本 40 篇 + 剛才的報告）

> 💡 **完整循環：問知識 → 查新的 → 存起來 → 下次就知道了。**
> 不用記路徑、不用打指令，說話就好。

<details>
<summary>💻 技術補充（軟體人員）</summary>

**系統內部如何運作：**

使用者說「幫我查一下」時，系統自動判斷：
1. 意圖解析 → 需要外部資訊 → 路由到搜尋流程
2. web_search 工具執行 → 多源搜尋
3. 依 market-agent 的 SKILL.md SOP → 整理結構化摘要
4. 回覆使用者

使用者說「存進知識庫」時：
1. 產出 .md 存到 `knowledge/shared/raw/`
2. 自動觸發 ingest → 補 frontmatter → 存到 `knowledge/shared/wiki/`
3. 更新 index.md + log.md
4. 重建搜尋索引

**架構說明（ai-bot 系統定位）：**

ai-bot = 確定性路由外殼（L1–L3）+ ReAct 式迴圈核心（L4/Kiro）+ ReAct 沒有的記憶與成長層（memory/skills/審批）。

不是「沒用 ReAct」，而是把 ReAct 放在它該在的位置，然後補上它天生缺的三樣東西：

| 補上什麼 | 怎麼做 |
|---------|--------|
| **成本控制** | L1–L3 確定性路由先過濾，不是每句話都丟給 LLM |
| **持久記憶** | knowledge/ 知識庫（raw → wiki → 搜尋索引） |
| **程序沉澱** | SKILL.md 把成功經驗寫成 SOP，下次照做不靠猜 |

```
L1: 指令解析（/start、/agents → 確定性路由，零 LLM 成本）
L2: 意圖分類（keyword 快速路由 → 命中直接執行）
L3: Planner（LLM 判斷：知識問答 / 搜尋 / Skill 執行）
L4: ReAct 迴圈（Kiro 核心：思考 → 工具呼叫 → 觀察 → 再思考）
L5: 記憶與成長（知識沉澱 + Skill 進化 + 使用者建模）
```

```bash
# API 確認 Wiki 正常
curl -X POST http://localhost:8000/api/v1/wiki/query \
  -H "Content-Type: application/json" \
  -d '{"q":"2025 老虎機市場"}'
```

</details>

---

## Step 4：TG 對話 — 兩種使用方式

📱 Telegram 打開你的 Bot，發送 `/start`。

直接問問題，不需要特殊指令。

### 問它知道的事（引用知識庫）

📱 發送：

```
Ocean King 的優勢是什麼？
```

✅ 預期：引用知識庫回答，附 📚 參考來源

📱 再問：

```
捕魚機跟老虎機哪種比較賺錢？
```

✅ 預期：引用比較分析的知識頁面

### 請它去找新的（上網搜尋）

📱 發送：

```
最近有什麼新的捕魚機遊戲上線？
```

✅ 預期：上網搜尋 → 產出最新情報 + 附來源連結

📱 再問：

```
PG Soft 2025 年推了什麼新遊戲？
```

✅ 預期：搜尋結果 + 結構化整理

### 怎麼分辨兩種？

你不用分辨。Agent 自己判斷：

| 你問的問題 | Agent 做什麼 | 你看到的差別 |
|-----------|-------------|------------|
| 知識庫有答案的 | 查 wiki → 引用回答 | 附 📚 參考：頁面名稱 |
| 知識庫沒有的 | 上網搜尋 → 整理回答 | 附 🔗 來源：網址 |

> 💡 **像問同事：他知道的直接答，不知道的幫你查。你不用管他「怎麼找到的」。**

<details>
<summary>💻 技術補充（軟體人員）</summary>

TG 內部路由流程：
```
使用者訊息
  → L1: 是指令？（/start /agents）→ 確定性處理
  → L2: keyword 快速路由？→ 命中就直接執行
  → L3: Planner（LLM 意圖分類）
      → 知識問答 → Wiki RAG 搜尋 → 回答
      → 需要新資料 → web_search → 格式化回答
      → 觸發 Skill → 執行對應 SOP
  → L4: ReAct 迴圈（複雜任務多步推理）
  → L5: 記憶寫入（對話記錄 + 使用者偏好）
```

Agent 路由：
- 預設走 admin-agent（通用助手）
- `/agents` 可手動切換
- 系統也會根據問題內容自動路由到合適 Agent

記憶層（L5）自動運作：
- 每次對話自動記錄到 FTS5 索引
- 每 10 輪觸發使用者建模（偏好萃取）
- knowledge/wiki/ 的知識持續累積 → RAG 查詢越來越準

</details>

---

## 日常使用

| 你想做什麼 | 怎麼說 |
|-----------|--------|
| 問已有知識 | 「Ocean King 怎麼樣？」 |
| 查新資料 | 「幫我查 XXX」 |
| 存進知識庫 | 「把這份整理存起來」 |
| 改它的風格 | 「你以後回答用簡報風格」 |
| 切換專家 | TG 發 `/agents` → 選 Agent |

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
問問題 → 查新資料 → 存進知識庫 → 下次就知道了
  ↑                                    │
  └──────── 越用越聰明 ←──────────────┘
```

**全程對話操作，不需要手寫程式碼。**

> 🔗 進階課程：[01-Agent 人格設計](../course-ai-bot/QUICKSTART-01-agent.md) / [02-Skills 開發](../course-ai-bot/QUICKSTART-02-skills.md) / [03-Wiki 知識庫](../course-ai-bot/QUICKSTART-03-wiki.md)
