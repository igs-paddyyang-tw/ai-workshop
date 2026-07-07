# 🚀 第三堂：LLM Wiki — 它能「記住」

## 🎯 課堂目標

完成後你能：
1. 用 AI 搜尋能力產出知識文件並匯入系統
2. 在 IDE 驗證知識庫能被查詢
3. 在 TG 確認 Agent 真的在用你的知識回答
4. 理解「加資料 → ingest → 立即可用 = 知識成長」

## 📋 前置條件

- 已完成第一堂（samples/ai-bot 能跑 + GEMINI_API_KEY 已設定）
- Kiro IDE（含 .kiro/skills/ark-wiki-engine）

## 📂 知識庫架構

```
knowledge/
├── raw/    ← 原始素材（你丟的 / AI 搜尋產出的）
├── wiki/   ← 結構化知識（ingest 後，Bot 能搜尋）
├── index.md ← 索引目錄
└── log.md   ← 操作日誌
```

**規則**：raw/ 是原料，wiki/ 是成品。Bot 只搜尋 wiki/。

## 📖 本堂知識（2 分鐘看完）

### LLM Wiki = AI 能搜尋的知識庫
- 不是維基百科，是你自己的 Markdown 知識庫
- Bot 收到問題 → 搜尋 wiki/ → 找到相關段落 → 合成回答 + 附引用
- 有引用 = RAG（Retrieval-Augmented Generation）

### 三者的關係

| 東西 | 是什麼 | 誰用 |
|------|--------|------|
| `knowledge/wiki/*.md` | 知識檔案 | Bot 的 WikiEngine 搜尋 |
| `WikiEngine`（Python） | 搜尋引擎 | Bot runtime 自動呼叫 |
| `ark-wiki-engine`（Skill） | IDE 操作工具 | 你在 Kiro IDE 觸發 ingest/query |

### IDE vs TG 的知識流

```
你（IDE）：                        使用者（TG）：
  Kiro 讀檔案 / 跑 curl              Bot handlers.py
       ↓                                  ↓
  直接看 wiki/ 內容              WikiEngine.query() 搜尋 wiki/
       ↓                                  ↓
  確認「檔案在不在」              Gemini + Wiki context → 回答 + 📚
```

### 兩層知識庫

| 層 | 位置 | 誰能用 | 怎麼加 |
|----|------|--------|--------|
| 全域 | `knowledge/wiki/` | 所有 Agent | 你手動 ingest（本堂教的） |
| 私有 | `agents/{agent}/knowledge/wiki/` | 只有該 Agent | memory 自動累積（課程 B 展開） |

💡 **概念**：`raw/` = 原料（你丟的）→ `ingest` = 轉換 → `wiki/` = 成品（Bot 能搜尋）

---

# IDE 開發

## Step 1：確認新知識還沒有（0-10 min）

**做什麼**：確認 wiki/ 現有內容 + 建立基準（新知識查不到）

📝 Kiro IDE 輸入：
```
列出 knowledge/wiki/ 有哪些檔案
```

✅ 預期：3 篇
```
ocean-king-analysis.md
super-ace-analysis.md
fishing-vs-slot-comparison.md
```

📝 IDE 驗證（確認舊知識能查到）：
```
幫我在終端執行：
curl -X POST http://localhost:8000/api/v1/wiki/query -H "Content-Type: application/json" -d '{"q":"Ocean King"}'
```

✅ 預期：回傳 ocean-king-analysis.md 的搜尋結果

📝 IDE 驗證（確認新知識還沒有）：
```
幫我在終端執行：
curl -X POST http://localhost:8000/api/v1/wiki/query -H "Content-Type: application/json" -d '{"q":"老虎機市場趨勢"}'
```

✅ 預期：沒有結果

💡 **舊的能查到，新的查不到 → Step 2 你來加。**

---

## Step 2：用 AI 搜尋產新知識 + IDE 驗證（10-30 min）⭐ 核心

**做什麼**：Kiro 搜尋網路 → 存 raw/ → ingest → IDE 確認能查到  
**為什麼**：用 AI 搜尋能力建構知識庫 — 不是手動寫內容

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

📝 匯入到 Wiki：
```
把 knowledge/raw/slot-market-trends.md 匯入到根目錄 knowledge/wiki/
並更新 knowledge/index.md
（不是 agents/ 下的，是專案根目錄的 knowledge/wiki/）
```

📝 IDE 驗證（確認新知識能查到了）：
```
幫我在終端執行：
curl -X POST http://localhost:8000/api/v1/wiki/query -H "Content-Type: application/json" -d '{"q":"老虎機市場趨勢"}'
```

✅ 預期：回傳 slot-market-trends.md 的搜尋結果（Step 1 查不到，現在查得到）

📝 確認數量：
```
列出 knowledge/wiki/ 有哪些檔案
```

✅ 預期：4 篇（多了 slot-market-trends.md）

💡 **IDE 驗證完成**：知識庫從 3 → 4 篇，query 確認能查到。接下來確認 Agent 也能用。

💡 **跟第二堂的串接**：02 的 `ark-competitor-brief` Skill 讀 knowledge/wiki/ 產 SWOT — 你加的知識就是它的資料來源。

---

# TG 上線驗證

💡 **為什麼要在 TG 再驗一次？**
- IDE 驗證的是「檔案在不在 + API 能不能查」
- TG 驗證的是「Agent 真的走你的知識回答」（SOUL + Wiki RAG + Planner）
- TG 有 📚 引用 = **你建的系統在用你的知識庫**，不是 AI 亂猜

💻 重啟：Ctrl+C → `python start.py`

## Step 3：TG 驗證 — Agent 用你的知識回答（30-50 min）

### 3.1 驗證舊知識

📱 Telegram → Market：
1. 問「Ocean King 3 跟 Ocean King 2 有什麼差別？」
2. 問「Super Ace 的 Golden Card 怎麼觸發？」

✅ 預期：
- 回答有「📚 參考：ocean-king-analysis」
- 有具體內容（不是泛泛回答）

### 3.2 驗證新知識（你 Step 2 加的）

📱 Telegram → Market：
- 問「最近老虎機市場有什麼新趨勢？」

✅ 預期：
- 引用 slot-market-trends.md 回答
- 包含真實數據（Step 2 AI 搜尋到的）
- 有「📚 參考：slot-market-trends」

💡 **Step 1 同一問題沒有引用 → 現在有引用 = 知識成長生效。**

### 3.3 對比：Wiki 沒有的問題

📱 問「PG Soft 的 Mahjong Ways 怎麼玩？」

✅ 預期：沒有「📚 參考」→ Agent 坦白說沒有相關知識

💡 **能回答的有引用，不能的坦白說 — 這就是可信任的 AI。**

---

## 📊 完成度分級

| 等級 | 達成條件 |
|------|----------|
| 🎯 保底 | wiki/ 有 4 篇 + IDE curl query 有結果 |
| ✅ 標準 | TG 問舊知識有引用 + 問新知識也有引用 |
| 🏆 快速 | AI 搜尋產知識 + IDE 驗證 + TG 驗證 + 理解知識成長 |

## 🏠 回家練習

1. 📝 Kiro：「搜尋我們公司其他產品的競品資料，整理成 knowledge/raw/ 格式並匯入」
2. 📝 Kiro：「檢查 Wiki 健康度（lint）」
3. 思考：哪些公司文件丟進去後，新人就能自己問 Agent 找答案？

---

*本堂重點：AI 搜尋 → 存 raw → ingest → wiki → Agent 能引用 = 知識成長。*
*IDE 驗證 = 資料在系統裡。TG 驗證 = Agent 真的在用。*
