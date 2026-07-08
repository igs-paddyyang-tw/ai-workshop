# AI Agent 機器人 — 簡易安裝與使用教學

> 10 分鐘下載 → IDE 對話了解系統 → Telegram 驗證 Agent 能上網產出競品分析。

---

## 前置條件

- Kiro IDE 已安裝並登入
- Python 3.12+
- Telegram Bot Token（從 @BotFather 取得）
- Gemini API Key（從 Google AI Studio 取得）

---

## Step 1：下載 ai-bot 專案

在 Kiro IDE 終端執行：

```bash
git clone https://github.com/igs-paddyyang-tw/ai-workshop.git
cd ai-workshop/samples/ai-bot
```

下載完成，你已經有了完整的 8 Agent 系統：

```
samples/ai-bot/
├── .kiro/
│   ├── steering/SOUL.md              ← 主 Agent 人格
│   └── skills/                        ← 5 個 IDE 技能（已內建）
│       ├── ark-wiki-engine/           ← 知識庫管理
│       ├── ark-grill-me/              ← 拷問設計
│       ├── ark-superpowers/           ← 規格書產出
│       ├── ark-skill-creator/         ← Skill 產出
│       └── ark-code-spec-validator/   ← 品質驗證
├── agents/                            ← 8 個 Agent（各有 SOUL + Skills + Wiki）
│   ├── admin-agent/
│   ├── market-agent/                  ← 市場研究員（能上網搜尋）
│   ├── coder-agent/
│   ├── data-agent/
│   ├── pm-agent/
│   ├── qa-agent/
│   ├── report-agent/
│   └── ai-dev-agent/
├── knowledge/shared/                  ← 共用知識庫（已預放 3 篇競品分析）
│   ├── raw/                           ← 原始素材
│   └── wiki/                          ← AI 整理後的知識頁面
├── src/                               ← Bot 程式碼
└── start.py                           ← 啟動入口
```

> 💡 **5 個 Skill 已經裝好在根目錄 `.kiro/skills/`，不需要另外下載。**

---

## Step 2：IDE 對話 — 了解三層架構

在 Kiro IDE 開啟 `samples/ai-bot/` 資料夾，進入 Chat 對話框。

### 靈魂（SOUL）— 它是誰

📝 貼到對話框：

```
列出這個專案有哪些 Agent，各自的角色和人格是什麼？
```

✅ 預期：Kiro 列出 8 個 Agent 各自的身份定位

📝 再問：

```
讀取 agents/market-agent/.kiro/steering/SOUL.md，介紹這個 Agent 的人格特質
```

✅ 預期：市場研究員 — 好奇敏銳、像調查記者、資訊必須有來源

> 💡 **SOUL.md = 改一句話，Agent 行為就變。** 不用改程式碼。

---

### 能力（SKILL）— 它會什麼

📝 貼到對話框：

```
列出根目錄 .kiro/skills/ 有哪些技能，各自做什麼用？
```

✅ 預期：5 個技能一覽

| Skill | 做什麼 |
|-------|--------|
| ark-wiki-engine | 知識庫管理（匯入/查詢/健康檢查） |
| ark-grill-me | 拷問你的設計，逼你想清楚 |
| ark-superpowers | 把決策寫成可驗證的規格書 |
| ark-skill-creator | 依規格產出新 Skill |
| ark-code-spec-validator | 驗證程式碼跟規格一致（打分數） |

📝 看 Agent 層級的 Skill：

```
列出 agents/market-agent/.kiro/skills/ 有什麼能力
```

✅ 預期：`ark-market-research`（多源搜尋 → 交叉驗證 → 洞察摘要）

> 💡 **根目錄 Skill = IDE 開發用（設計/拷問/產出）。Agent 目錄 Skill = 業務用（搜尋/分析）。**

---

### 記憶（WIKI）— 它知道什麼

📝 貼到對話框：

```
列出 knowledge/shared/wiki/ 有哪些知識頁面
```

✅ 預期：3 篇預裝知識

| 檔案 | 內容 |
|------|------|
| ocean-king-analysis.md | Ocean King 捕魚機分析 |
| super-ace-analysis.md | Super Ace 老虎機分析 |
| fishing-vs-slot-comparison.md | 捕魚機 vs 老虎機比較 |

📝 體驗知識引用：

```
讀取 knowledge/shared/wiki/ 的內容，用 market-agent 的人格回答：
「Ocean King 3 跟 Super Ace 比較，各自的優劣勢是什麼？」
```

✅ 預期：有結構的比較分析 + 引用 wiki 知識

> 💡 **raw/ = 你丟原始素材 → ingest → wiki/ = AI 整理好能查的。** 知識越多，回答越準。

---

### 三層一句話總結

```
┌─────────────────────────────────────────────┐
│                                             │
│   SOUL（靈魂）= 它是誰                      │
│   → agents/*/SOUL.md                        │
│                                             │
│   SKILL（能力）= 它會什麼                    │
│   → .kiro/skills/ + agents/*/skills/        │
│                                             │
│   WIKI（記憶）= 它知道什麼                   │
│   → knowledge/shared/wiki/                  │
│                                             │
└─────────────────────────────────────────────┘
```

---

## Step 3：啟動 Bot + TG 驗證

### 3.1 設定環境

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

📝 在 Kiro IDE 打開 `.env`，填入：

```
TELEGRAM_BOT_TOKEN=你的_Token
GEMINI_API_KEY=你的_Key
```

### 3.2 啟動

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

### 3.3 TG 驗證：Market Agent 上網產出競品分析

📱 Telegram 操作：

1. 對 Bot 發送 `/start` → 收到歡迎訊息 ✅
2. 發送 `/agents` → 出現 8 個 Agent 按鈕
3. 點選「🗺️ Market」切換到市場研究員
4. 發送：

```
幫我搜尋 2025 年老虎機市場最新動態，產出競品情報摘要
```

✅ 預期結果：

```
🗺️ 市場情報
├── 主題: 2025 老虎機市場動態
├── 發現:
│   1. [高信心] Pragmatic Play 推出 Megaways 系列...
│   2. [中信心] PG Soft 亞洲市佔率持續成長...
│   3. ...
├── 來源: Google Search + 產業新聞
└── 建議: 關注 xxx 趨勢
```

📱 再試一個（用 Wiki 知識 + 網路搜尋結合）：

```
Ocean King 系列跟 2025 年市場新進的捕魚機相比有什麼優劣？
```

✅ 預期：引用 wiki 的 Ocean King 知識 + 搜尋網路新資訊 → 整合比較

---

## 進階操作

| 你想做什麼 | 在 Kiro IDE 說 |
|-----------|---------------|
| 改 Agent 語氣 | 「把 market-agent 的 SOUL 改成像分析師簡報風格」 |
| 增加知識 | 「搜尋 PG Soft 2025 產品線，存到 knowledge/shared/raw/ 並匯入 wiki」 |
| 拷問設計 | 「拷問我的設計：我想為 market-agent 加一個自動日報功能」 |
| 產出新 Skill | 「根據拷問結果幫我寫 spec，然後建立 Skill」 |
| 驗證品質 | 「驗證 code 跟 spec 一致嗎」 |
| 切換人格 | TG 發 `/agents` → 點其他 Agent |

---

## 卡關排除

| 問題 | 解法 |
|------|------|
| Bot 無回應 | 確認 `.env` 的 TELEGRAM_BOT_TOKEN 正確 |
| Tier 2 顯示 ⬚ | 確認 GEMINI_API_KEY 正確且有額度 |
| Market 搜不到東西 | 確認網路正常 + Gemini Key 有效 |
| `ModuleNotFoundError` | `pip install -r requirements.txt` |
| 回答沒引用知識 | 確認 `knowledge/shared/wiki/` 有檔案 |

---

## 知識成長循環

Bot 上線後，持續餵它知識讓它越來越聰明：

```
你丟素材（raw/）→ AI 整理（wiki/）→ Agent 引用回答
     ↑                                      │
     └──── 你覺得缺什麼就再丟 ←────────────┘
```

📝 在 Kiro IDE 隨時說：

```
幫我搜尋「XXX」，整理成知識文件存到 knowledge/shared/raw/ 並匯入 wiki
```

知識越多 → 回答越準 → 你越信任 → 丟更多 → ♻️

---

## 總結

```
Step 1: 下載 ai-bot（clone 就有完整系統）
Step 2: IDE 對話了解 SOUL + SKILL + WIKI 三層架構
Step 3: 啟動 → TG 驗證 Market Agent 能上網產出競品分析
```

**10 分鐘，3 步，一個能上網搜尋、有知識記憶、能產出競品分析的 AI Agent 系統。**

> 🔗 進階課程：[01-Agent 人格設計](../course-ai-bot/QUICKSTART-01-agent.md) / [02-Skills 開發](../course-ai-bot/QUICKSTART-02-skills.md) / [03-Wiki 知識庫](../course-ai-bot/QUICKSTART-03-wiki.md)
