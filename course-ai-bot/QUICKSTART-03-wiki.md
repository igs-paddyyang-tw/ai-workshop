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
查詢「Super Ace 的 Golden Card 機制怎麼運作」
```

✅ 預期：匹配到 super-ace-analysis.md 中 Golden Card → Wild 轉換的說明

---

## Step 3：用 AI 產出新知識（20-35 min）

**做什麼**：讓 Kiro 搜尋網路 → 整理成知識文件 → 匯入 Wiki  
**為什麼**：不是手動寫內容，而是用 AI 的搜尋能力產出知識 — 這才是正確的工作方式

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

→ Kiro 會：
1. 跑 web search 抓真實資料
2. 整理成結構化 .md
3. 存到 knowledge/raw/slot-market-trends.md

📝 確認產出：
```
打開 knowledge/raw/slot-market-trends.md，確認有 frontmatter 和實際數據
```

📝 匯入：
```
把 knowledge/raw/slot-market-trends.md 匯入到根目錄 knowledge/wiki/
並更新 knowledge/index.md
```

📝 驗證能查到：
```
搜尋 knowledge/wiki/ 中關於「老虎機市場」的內容
```

✅ 預期結果：
- 找到 slot-market-trends.md 的內容
- 包含真實的市場數據（不是你手寫的）

💡 **這才是正確的知識建構流程**：AI 搜尋 → 整理 → 存檔 → ingest → 可查詢

📝 加碼（如果有時間）：
```
再搜尋「捕魚機遊戲 2024 最新動態」，
整理成 knowledge/raw/fishing-game-2024.md 並匯入
```

💡 **到這裡，開發者端確認完成 — 知識庫有效、查詢正確。**

💡 **跟第二堂的串接**：02 開發的 `ark-competitor-brief` Skill 會讀 knowledge/wiki/ 產出 SWOT 簡報 — 你現在匯入的知識，就是那個 Skill 的資料來源。

---

# TG 上線驗證

💻 **上線前先在 IDE 確認**：

📝 Kiro IDE 輸入：
```
搜尋根目錄 knowledge/wiki/ 中包含「Ocean King」的檔案，
列出匹配的內容片段
```

✅ 確認：有找到 ocean-king-analysis.md 的內容 → OK，可以上線

💻 重啟：Ctrl+C → `python start.py`

## Step 4：Telegram 驗證 — 使用者能拿到答案（35-45 min）

**做什麼**：切到 Telegram，確認「真實使用者」也能拿到有引用的答案  
**為什麼**：Kiro 驗證 = 開發 OK。Telegram 驗證 = 上線 OK、第三方可用。

📱 Telegram：
1. `/agents` → Admin
2. 問「Ocean King 3 跟 Ocean King 2 有什麼差別？」
3. 問「Super Ace 的 Golden Card 怎麼觸發？」

✅ 預期結果：
- 回答詳細 + 底部有「📚 參考：ocean-king-analysis」
- Super Ace 問題引用「super-ace-analysis」
- **使用者體驗 = 有依據、不幻覺、可信任**

📱 對比測試：問一個 Wiki 沒有的問題
- 「PG Soft 的 Mahjong Ways 怎麼玩？」
- 觀察：回答沒有「📚 參考」→ Agent 誠實表示沒有相關知識

💡 **能回答的有引用，不能的坦白說 — 這就是可信任的 AI。**

---

## Step 5：自演化觀察 — 私有記憶成長（45-50 min）

**做什麼**：觀察 memory 自動記錄到私有知識庫 + 理解兩層成長  
**為什麼**：全域知識你手動加，私有知識 Agent 自動累積 — 雙線成長

📝 Kiro IDE 輸入：
```
列出 agents/admin-agent/knowledge/raw/ 的檔案
```

✅ 預期結果：
- 看到今天對話的 memory 檔案（如 `2026-07-06_1030_user123.md`）
- 這是 Agent 自動記錄的（你沒手動丟，它自己寫的）

📝 Kiro IDE 問：
```
解釋兩層知識庫的成長循環：
- 全域：我丟文件 → ingest → 所有 Agent 能引用
- 私有：每次對話 → memory 自動記 → ingest 後只有該 Agent 能引用
這兩層怎麼讓系統越用越聰明？
```

✅ 理解重點：
```
全域知識（你手動加）：
  丟文件 → knowledge/raw/ → ingest → wiki/ → 全 Agent 引用

私有記憶（Agent 自動累積）：
  對話 → memory → agents/{agent}/knowledge/raw/
      → ingest → agents/{agent}/knowledge/wiki/
      → 只有該 Agent 引用（越聊越懂你）

雙線成長 = 自演化
```

---

## 📊 完成度分級

| 等級 | 達成條件 |
|------|----------|
| 🎯 保底 | Kiro 內 ingest 成功 + 查詢有結果 |
| ✅ 標準 | Kiro 驗證 + Telegram 使用者也能拿到有引用的答案 |
| 🏆 快速 | 建自己文件 + 雙端驗證 + 理解自演化循環 |

## 🏠 回家練習

1. 📝 Kiro：「建立一份我們公司其他產品線的競品分析，匯入 Wiki」
2. 📝 Kiro：「檢查 Wiki 健康度，修復所有問題」
3. 思考：哪些公司文件丟進去後，新人就能自己問 Agent 找答案？（產品 spec？設計規範？營運 SOP？）

---

*本堂重點：IDE 開發知識庫。TG 驗證上線。自演化 = 越用越聰明。*
