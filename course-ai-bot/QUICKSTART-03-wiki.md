# 🚀 第三堂：LLM Wiki — 它能「記住」

## 🎯 課堂目標

完成後你能：
1. 在 Kiro IDE 內完成知識庫建構 + 驗證 RAG 有效
2. 讓 Agent 學會「你教它的東西」（丟文件 → 能回答）
3. 部署到 Telegram 確認使用者也能拿到正確答案
4. 理解自演化：每次對話都在讓 Agent 變聰明

## 📋 前置條件

- samples/ai-bot 能跑 + GEMINI_API_KEY 已設定

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

## Step 1：確認 Wiki 是空的（0-5 min）

**做什麼**：確認 knowledge/wiki/ 還沒有內容  
**為什麼**：raw/ 有素材 ≠ Agent 能引用。要先 ingest 才能查到。

📝 Kiro IDE 輸入：
```
列出 knowledge/raw/ 和 knowledge/wiki/ 各有什麼檔案
```

✅ 預期：
- raw/：3 篇素材（ocean-king-analysis.md、super-ace-analysis.md、fishing-vs-slot-comparison.md）
- wiki/：空的（還沒匯入）

💡 **素材存在 ≠ 知識可用。raw/ 是原料，wiki/ 是成品。**

📝 驗證 TG 也查不到：
```
📱 TG → Market →「Ocean King 3 跟 2 有什麼差別？」
```

✅ 預期：回答泛泛（沒有「📚 參考」引用）= Wiki 還沒生效

---

## Step 2：匯入知識 + Kiro 內驗證（5-20 min）⭐ 核心

**做什麼**：匯入知識後，在 Kiro 內確認 RAG 有效  
**為什麼**：開發者先確認功能正常，再提供給使用者

📝 Kiro IDE 輸入：
```
把根目錄 knowledge/raw/ 的 3 篇 .md 檔案匯入到根目錄 knowledge/wiki/
（不是 agents/ 下的，是專案根目錄的 knowledge/）

具體操作：
1. 讀取 knowledge/raw/ 所有 .md
2. 確認有 frontmatter，沒有的話補上
3. 寫入 knowledge/wiki/
4. 更新 knowledge/index.md
```

→ Kiro 執行匯入（或提示你跑 `curl -X POST http://localhost:8000/api/v1/wiki/ingest`）

⚠️ 如果 Kiro 把檔案放到 agents/ 下 → 提醒它：「不對，要放根目錄 knowledge/wiki/，不是 agent 的私有目錄」

✅ 預期結果：
- `knowledge/wiki/` 出現 3 個 .md（ocean-king-analysis.md 等）
- `knowledge/index.md` 更新（列出 3 篇）

📝 在 Kiro 內驗證（不需要開 Telegram）：
```
再查一次「Ocean King 系列跟競品的差異」
```

✅ 預期結果：
- 找到 ocean-king-analysis.md 的相關片段
- 列出 Ocean King 2/3/4 各版本的特色差異
- **跟 Step 1 明顯不同 — 這就是 RAG 的效果**

📝 追加驗證：
```
列出 knowledge/wiki/ 目前有哪些檔案
```

✅ 預期：3 篇（ocean-king-analysis.md、super-ace-analysis.md、fishing-vs-slot-comparison.md）

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
