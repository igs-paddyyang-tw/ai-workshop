# AI Agent 機器人 — 簡易安裝與使用教學

> 10 分鐘在 Kiro IDE 裡建好一個有人格、有能力、有記憶的 AI Bot，部署到 Telegram 馬上能用。

---

## 前置條件

- Kiro IDE 已安裝並登入
- Python 3.12+
- Telegram Bot Token（從 @BotFather 取得）
- Gemini API Key（從 Google AI Studio 取得）

---

## 開始：打開 Kiro IDE 對話

啟動 Kiro IDE，開啟你的專案資料夾，進入 Chat 對話框。

---

## Phase 1：給它靈魂（SOUL）

複製以下整段文字，貼到對話框送出：

```
1. 幫我建立 .kiro/steering/SOUL.md，角色是「遊戲產業 AI 助手」，擅長競品分析、市場趨勢、玩法設計，回答簡潔有條理，用繁體中文。
2. 幫我下載 https://github.com/igs-paddyyang-tw/ai-workshop/tree/main/samples/ai-bot 的完整專案結構到當前目錄
3. 建立 .env 檔案，內容留空讓我填：TELEGRAM_BOT_TOKEN= 和 GEMINI_API_KEY=
```

> 💡 一段話 3 件事：建立人格 → 下載 Bot 骨架 → 準備環境設定。
>
> ✏️ 角色描述換成你想要的，例如：
> - 「專業客服，親切有禮，回答附上文件連結」
> - 「資深後端工程師，擅長 Python，回答精準附程式碼」
> - 「行銷企劃專家，語氣活潑，擅長文案和市場分析」
>
> 改這段就好：`角色是「___」，擅長___，回答時___。`

完成後你的專案有了 **靈魂**：

```
your-project/
├── .kiro/steering/SOUL.md    ← Agent 人格（決定語氣和風格）
├── .env                       ← Token 和 Key（你要填）
├── src/                       ← Bot 程式碼
└── start.py                   ← 啟動入口
```

| 產出 | 用途 |
|------|------|
| `SOUL.md` | 改一句話 → Bot 行為就變（不用改程式碼） |
| `.env` | 放你的 Token 和 Key |

---

## Phase 2：給它能力（SKILL）

貼到對話框送出：

```
1. 幫我下載 https://github.com/igs-paddyyang-tw/ark-agent-skills/blob/main/ark-wiki-engine/SKILL.md 放到 .kiro/skills/ark-wiki-engine/SKILL.md
2. 幫我下載 https://github.com/igs-paddyyang-tw/ark-agent-skills/blob/main/ark-web-scraper/SKILL.md 放到 .kiro/skills/ark-web-scraper/SKILL.md
3. 幫我下載 https://github.com/igs-paddyyang-tw/ark-agent-skills/blob/main/ark-grill-me/SKILL.md 放到 .kiro/skills/ark-grill-me/SKILL.md
```

> 💡 SKILL.md = Agent 的 SOP。有了它，Agent 就知道「遇到什麼需求要按什麼步驟做」。

完成後你的專案有了 **能力**：

```
.kiro/skills/
├── ark-wiki-engine/SKILL.md    ← 知識庫管理（ingest/query/lint）
├── ark-web-scraper/SKILL.md    ← 網頁抓取（搜尋+整理資訊）
└── ark-grill-me/SKILL.md       ← 拷問設計（釐清需求）
```

| Skill | 一句話 |
|-------|--------|
| ark-wiki-engine | 讓 Agent 能記住你的知識、能引用回答 |
| ark-web-scraper | 讓 Agent 能搜尋網路、抓取資料 |
| ark-grill-me | 讓 Agent 能拷問你的想法，幫你想清楚 |

---

## Phase 3：給它記憶（WIKI）

貼到對話框送出：

```
1. 幫我用 ark-wiki-engine 建立 knowledge/ 知識庫目錄結構（含 raw/ wiki/ schema.md index.md log.md）
2. 幫我在 knowledge/raw/ 建立一份「老虎機市場趨勢 2024-2025」的範例知識文件（搜尋真實資料）
3. 把 knowledge/raw/ 的檔案匯入 knowledge/wiki/
```

> 💡 raw/ = 你放原始素材（AI 只讀不改）→ ingest → wiki/ = AI 整理好的知識頁面。

完成後你的專案有了 **記憶**：

```
knowledge/
├── raw/                          ← 你丟素材的地方（唯讀）
│   └── slot-market-trends.md     ← 範例：老虎機市場趨勢
├── wiki/                          ← AI 整理後的知識頁面
│   └── slot-market-trends.md     ← 有 frontmatter 的結構化版本
├── schema.md                      ← 知識庫規則
├── index.md                       ← 索引目錄
└── log.md                         ← 操作日誌
```

---

## Phase 4：啟動 Bot

### 填入 Token

打開 `.env`，填入你的 Token 和 Key：

```
TELEGRAM_BOT_TOKEN=你的_Telegram_Bot_Token
GEMINI_API_KEY=你的_Gemini_API_Key
```

### 啟動

在 Kiro IDE 終端執行：

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python start.py
```

### 確認成功

看到以下訊息 = 成功：

```
══════════════════════════════════════════════════
  🤖 AI Agent Bot
══════════════════════════════════════════════════
  🧠 SOUL: ✅ 已載入
  📦 Skills: 已註冊
  📚 知識庫: ✅ 已載入
  🤖 Bot: @your_bot_name 已連線
══════════════════════════════════════════════════
```

📱 **Telegram 驗證**：對你的 Bot 發送 `/start` → 收到歡迎訊息 = ✅ 成功

---

## 使用方式

### 問知識庫有的問題

```
老虎機市場最近有什麼趨勢？
```

✅ 預期：有引用 📚 的回答（來自你的 wiki/）

### 增加新知識

在 Kiro IDE 對話框說：

```
幫我搜尋「2025 捕魚機遊戲市場分析」，整理成知識文件存到 knowledge/raw/ 並匯入 wiki
```

→ Agent 搜尋 → 整理 → 匯入 → 下次問就能引用

### 拷問你的設計

```
拷問我的設計：我想做一個「每日遊戲新聞」自動推播功能
```

→ Agent 一次問一題，幫你想清楚需求

### 切換人格

在 Kiro IDE 修改 `.kiro/steering/SOUL.md` → Bot 重啟後行為就變。

---

## 三層架構一句話

```
┌─────────────────────────────────────────────┐
│                                             │
│   SOUL（靈魂）= 它是誰                      │
│   改人格 → 行為就變                          │
│                                             │
│   SKILL（能力）= 它會什麼                    │
│   加 SKILL.md → 新功能就有                   │
│                                             │
│   WIKI（記憶）= 它知道什麼                   │
│   丟素材 + ingest → 知識就長                 │
│                                             │
└─────────────────────────────────────────────┘
```

**全程在 Kiro IDE 對話框操作，不需要手寫程式碼。**

---

## 進階操作

| 你想做什麼 | 在 Kiro IDE 說 |
|-----------|---------------|
| 改 Bot 語氣 | 「把 SOUL.md 改成幽默風格」 |
| 加新能力 | 「幫我建立一個『每日報表』Skill」 |
| 加新知識 | 「搜尋 XXX 存到 raw/ 並匯入 wiki」 |
| 檢查知識品質 | 「檢查 knowledge/wiki/ 健康度」 |
| 產出規格書 | 「拷問我的設計，然後幫我寫 spec」 |
| 驗證品質 | 「驗證 code 跟 spec 一致嗎」 |

---

## 卡關排除

| 問題 | 解法 |
|------|------|
| Bot 無回應 | 確認 `.env` 的 TELEGRAM_BOT_TOKEN 正確 |
| 回答沒引用知識 | 確認 `knowledge/wiki/` 有檔案 + 重啟 Bot |
| `ModuleNotFoundError` | 執行 `pip install -r requirements.txt` |
| Gemini 403 | 確認 GEMINI_API_KEY 正確且有額度 |
| port 被佔用 | `python start.py --port 8001` |

---

## 總結

```
Phase 1: SOUL（靈魂）→ 它是誰
Phase 2: SKILL（能力）→ 它會什麼
Phase 3: WIKI（記憶）→ 它知道什麼
Phase 4: 啟動 → Telegram 馬上能用
```

**10 分鐘，4 個 Phase，一個有人格、有能力、有記憶的 AI Bot。**

---

## 知識成長循環

Bot 上線後，持續餵它知識：

```
你丟素材（raw/）→ AI 整理（wiki/）→ Agent 引用回答
     ↑                                      │
     └──── 你覺得缺什麼就再丟 ←────────────┘
```

知識越多 → 回答越準 → 你越信任 → 丟更多 → ♻️

> 🔗 完整課程：[QUICKSTART-01 Agent](../course-ai-bot/QUICKSTART-01-agent.md) / [QUICKSTART-02 Skills](../course-ai-bot/QUICKSTART-02-skills.md) / [QUICKSTART-03 Wiki](../course-ai-bot/QUICKSTART-03-wiki.md)
