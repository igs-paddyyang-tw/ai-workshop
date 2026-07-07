# 🚀 第三堂：LLM Wiki — 它能「記住」

## 🎯 課堂目標

完成後你能：
1. 在 Kiro IDE 內完成知識庫建構 + 驗證 RAG 有效
2. 讓 Agent 學會「你教它的東西」（丟文件 → 能回答）
3. 部署到 Telegram 確認使用者也能拿到正確答案
4. 理解自演化：每次對話都在讓 Agent 變聰明

## 📋 前置條件

- 已完成第一堂（samples/ai-bot 能跑 + GEMINI_API_KEY 已設定）
- Kiro IDE（含 .kiro/skills/ark-wiki-engine）

## 使用的功能

| 功能 | 觸發方式 | 位置 |
|------|---------|------|
| Wiki 匯入 | 📝「匯入知識到 Wiki」或 `curl /api/v1/wiki/ingest` | 全域 knowledge/ |
| Wiki 查詢 | 📱 TG 直接問（自動查）或 `curl /api/v1/wiki/query` | 先私有再全域 |
| Wiki 檢查 | 📝「檢查 Wiki 健康度」或 `curl /api/v1/wiki/lint` | 全域 knowledge/ |

### 📂 知識庫架構（兩層）

```
knowledge/                          ← 全域（所有 Agent 共用）
├── raw/                            ← 丟文件的地方
│   ├── ocean-king-analysis.md
│   ├── super-ace-analysis.md
│   └── fishing-vs-slot-comparison.md
└── wiki/                           ← ingest 後 → TG 能查到

agents/admin-agent/knowledge/       ← 私有（只有 admin 能查到）
├── raw/                            ← memory 自動寫入的對話記錄
└── wiki/                           ← 私有 ingest 後
```

**規則**：
- TG 問問題 → 先查私有 wiki → 再查全域 wiki → 合併回答
- 全域 = 公司共用知識（競品分析、SOP）
- 私有 = Agent 的對話記憶（越聊越懂你）

---

# IDE 開發

## Step 1：確認目前知識庫狀態（0-5 min）

**做什麼**：看 wiki/ 目前有什麼 + 問一個還沒有的問題當基準  
**為什麼**：等下你加新知識後，同一問題會有不同結果 = 知識成長

📝 Kiro IDE 輸入：
```
列出 knowledge/wiki/ 有哪些檔案
```

✅ 預期：3 篇（預設的競品分析）
```
ocean-king-analysis.md
super-ace-analysis.md
fishing-vs-slot-comparison.md
```

📱 TG → Market → 問「最近老虎機市場有什麼新趨勢？」

✅ 預期：回答沒有「📚 參考」引用（因為 wiki/ 沒有市場趨勢的資料）

💡 **系統有 3 篇舊知識，但沒有「你的新知識」→ Step 3 你來加。**

---

## Step 2：理解 ingest 流程 + 驗證 Wiki 可查詢（5-20 min）⭐ 核心

**做什麼**：理解 raw/ → wiki/ 的流程，驗證現有 Wiki 能被查到  
**為什麼**：Step 3 你要加新知識，先確認機制運作正常

📝 Kiro IDE 輸入：
```
說明 knowledge/raw/ 和 knowledge/wiki/ 的關係：
- raw/ 是什麼？wiki/ 是什麼？
- ingest 做了什麼事？
- 看一下 knowledge/wiki/ocean-king-analysis.md 的 frontmatter
```

✅ 預期 Kiro 解釋：
- raw/ = 原始素材（你丟的）
- wiki/ = 結構化知識（有 frontmatter，Bot 能搜尋的）
- ingest = 把 raw/ 處理成 wiki/（補 frontmatter + 更新 index）

📝 驗證 Wiki 能被查詢（確認 Bot server 在跑）：
```
幫我在終端執行：
curl -X POST http://localhost:8000/api/v1/wiki/query -H "Content-Type: application/json" -d '{"q":"Ocean King"}'
```

✅ 預期：回傳包含 ocean-king-analysis.md 的搜尋結果

📝 追加驗證：
```
列出 knowledge/wiki/ 目前有哪些檔案
```

✅ 預期：3 篇（ocean-king-analysis.md、super-ace-analysis.md、fishing-vs-slot-comparison.md）

💡 **現有的 3 篇是預設的。接下來 Step 3 你用 AI 搜尋產出新知識加進去。**

---

## Step 3：用 AI 搜尋產出新知識（20-35 min）

**做什麼**：讓 Kiro 搜尋網路 → 整理成知識文件 → 匯入 Wiki  
**為什麼**：不是手動寫內容，而是用 AI 的搜尋能力產出知識

📝 Kiro IDE 輸入：
```
幫我搜尋 2024-2025 老虎機市場最新趨勢，
整理成一份知識文件存到 knowledge/raw/slot-market-trends.md

要求：
- 搜尋真實資料（市場規模、主要玩家、玩法趨勢）
- 用 frontmatter 格式（title, type: market-research, tags, created）
- 內容分段：市場概況 / 主要玩家 / 玩法趨勢 / 營收模式
- 附上資料來源
```

→ Kiro web search → 整理 → 存到 knowledge/raw/

📝 匯入：
```
把 knowledge/raw/slot-market-trends.md 匯入到根目錄 knowledge/wiki/
並更新 knowledge/index.md
```

📝 確認檔案存在：
```
列出 knowledge/wiki/ 目前有哪些檔案
```

✅ 預期：4 篇（多了 slot-market-trends.md）

💡 **IDE 段完成**：知識庫從 3 篇 → 4 篇。接下來去 TG 確認使用者能查到。

💡 **跟第二堂的串接**：02 開發的 `ark-competitor-brief` Skill 會讀 knowledge/wiki/ 產出 SWOT 簡報 — 你現在匯入的知識，就是那個 Skill 的資料來源。

---

# TG 上線驗證

💡 **為什麼要在 TG 再驗一次？**
- IDE 問 = Kiro 自己回答（不經過你的 Agent 系統）
- TG 問 = 真的走 Agent 運作（SOUL + Wiki RAG + Planner + Memory）
- TG 有 📚 引用 = **你建的系統在用你的知識庫回答**，不是 AI 亂猜

💻 重啟：Ctrl+C → `python start.py`

## Step 4：TG 驗證舊知識（35-42 min）

**做什麼**：問 Step 2 匯入的知識 → 確認有引用  
**為什麼**：使用者能拿到有依據的答案 = 上線 OK

📱 Telegram → Market：
1. 問「Ocean King 3 跟 Ocean King 2 有什麼差別？」
2. 問「Super Ace 的 Golden Card 怎麼觸發？」

✅ 預期：
- 回答有「📚 參考：ocean-king-analysis」
- 有具體內容（不是泛泛回答）

📱 對比：問 Wiki 沒有的
- 「PG Soft 的 Mahjong Ways 怎麼玩？」
- ✅ 預期：沒有「📚 參考」→ 坦白說不知道

---

## Step 5：TG 驗證新知識（42-50 min）

**做什麼**：問 Step 3 剛用 AI 產出的知識 → 確認也有引用  
**為什麼**：你 10 分鐘前加的東西，使用者現在就能查到 = 知識成長生效

📱 Telegram → Market：
- 問「最近老虎機市場有什麼新趨勢？」

✅ 預期：
- 引用 slot-market-trends.md 回答
- 包含真實數據（Kiro 搜尋到的）
- 有「📚 參考：slot-market-trends」

💡 **你 Step 3 用 AI 搜尋的資料 → 現在使用者在 TG 能查到了。**
**這就是知識成長：加資料 → ingest → 立即可用。**

---

## 📊 完成度分級

| 等級 | 達成條件 |
|------|----------|
| 🎯 保底 | ingest 成功 + wiki/ 有檔案 |
| ✅ 標準 | TG 問舊知識有引用 + 問新知識也有引用 |
| 🏆 快速 | 用 AI 搜尋產知識 + 雙端驗證 + 理解知識成長 |

## 🏠 回家練習

1. 📝 Kiro：「搜尋我們公司其他產品的競品資料，整理成 knowledge/raw/ 格式並匯入」
2. 📝 Kiro：「檢查 Wiki 健康度，修復所有問題」
3. 思考：哪些公司文件丟進去後，新人就能自己問 Agent 找答案？

---

*本堂重點：IDE 建構知識庫。TG 驗證上線。AI 搜尋 → 匯入 → 立即可用 = 知識成長。*
