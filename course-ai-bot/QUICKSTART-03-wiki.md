# 🚀 第三堂：LLM Wiki — 它能「記住」

## 🎯 課堂目標

你加的知識，Agent 馬上能引用回答。

## 📋 前置條件

- 已完成第一堂（samples/ai-bot 能跑 + GEMINI_API_KEY 已設定）
- Kiro IDE（含 .kiro/skills/ark-wiki-engine）

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
  確認「API 能查到」              Gemini + Wiki context → 回答 + 📚
```

### 兩層知識庫

| 層 | 位置 | 誰能用 | 怎麼加 |
|----|------|--------|--------|
| 全域 | `knowledge/wiki/` | 所有 Agent | 你手動 ingest（本堂教的） |
| 私有 | `agents/{agent}/knowledge/wiki/` | 只有該 Agent | memory 自動累積（課程 B 展開） |

💡 `raw/` = 原料 → `ingest` = 轉換 → `wiki/` = 成品（Bot 能搜尋）

---

# IDE 開發

## Step 1：查知識 — 確認現狀（0-5 min）

**做什麼**：用 curl 確認舊知識能查到 + 新知識查不到

📝 Kiro IDE 輸入：
```
幫我在終端執行：
curl -X POST http://localhost:8000/api/v1/wiki/query -H "Content-Type: application/json" -d '{"q":"Ocean King"}'
```

✅ 預期：回傳 ocean-king-analysis.md 的搜尋結果（舊知識能查 ✅）

📝 再查一個新的：
```
幫我在終端執行：
curl -X POST http://localhost:8000/api/v1/wiki/query -H "Content-Type: application/json" -d '{"q":"老虎機市場趨勢"}'
```

✅ 預期：沒有結果（新知識還沒加 → Step 2 你來加）

---

## Step 2：增加新知識（5-25 min）⭐ 核心

**做什麼**：用 AI 搜尋產出新知識 → ingest → curl 確認能查到

📝 Kiro IDE 輸入（AI 搜尋產出知識）：
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

📝 curl 驗證（確認 ingest 成功）：
```
幫我在終端執行：
curl -X POST http://localhost:8000/api/v1/wiki/query -H "Content-Type: application/json" -d '{"q":"老虎機市場趨勢"}'
```

✅ 預期：回傳 slot-market-trends.md 的搜尋結果（Step 1 查不到 → 現在查得到 ✅）

💡 **跟第二堂的串接**：02 的 `ark-competitor-brief` Skill 讀 knowledge/wiki/ 產 SWOT — 你加的知識就是它的資料來源。

---

## Step 3：健康檢查（25-30 min）

**做什麼**：用 curl lint 確認知識庫品質正常

📝 Kiro IDE 輸入：
```
幫我在終端執行：
curl http://localhost:8000/api/v1/wiki/lint
```

✅ 健康：`{"issues": [], "healthy": true}`

⚠️ 有問題（缺 frontmatter）→ 📝「幫我修復 lint 回報的問題」→ 再 curl lint 確認

📝 確認最終數量：
```
列出 knowledge/wiki/ 有哪些檔案
```

✅ 預期：4 篇 + 全部 healthy = IDE 開發完成，Agent 可以上線

---

# TG 上線驗證

💡 **為什麼要在 TG 再驗一次？**
- IDE 驗的是「API 能查到」
- TG 驗的是「Agent 真的走你的知識回答」（SOUL + Wiki RAG + Planner）
- TG 有 📚 引用 = **你建的系統在用你的知識庫**，不是 AI 亂猜

💻 重啟：Ctrl+C → `python start.py`

## Step 4：使用知識 — Agent 引用回答（30-42 min）

### 4.1 驗證舊知識

📱 Telegram → Market：
1. 問「Ocean King 3 跟 Ocean King 2 有什麼差別？」
2. 問「Super Ace 的 Golden Card 怎麼觸發？」

✅ 預期：回答有「📚 參考：ocean-king-analysis」

### 4.2 驗證新知識（你 Step 2 加的）

📱 Telegram → Market：
- 問「最近老虎機市場有什麼新趨勢？」

✅ 預期：
- 引用 slot-market-trends.md 回答
- 有「📚 參考：slot-market-trends」
- **Step 1 查不到 → 現在 Agent 能引用 = 知識成長生效**

### 4.3 對比：Wiki 沒有的

📱 問「PG Soft 的 Mahjong Ways 怎麼玩？」

✅ 預期：沒有「📚 參考」→ 坦白說不知道

💡 **能回答的有引用，不能的坦白說 = 可信任的 AI。**

---

## Step 5：健康檢查 — TG + Admin 後台（42-50 min）

### 5.1 TG 請 Agent 檢查

📱 TG → Admin → 「幫我檢查 Wiki 健康度」

✅ 預期：Agent 回報知識庫狀態（healthy 或列出問題）

💡 不只能問問題，還能請 Agent 做維護。

### 5.2 Admin 後台總覽

🌐 瀏覽器開 http://localhost:8000/admin

✅ 看到：
- KPI 卡片：知識庫 4 篇 / Wiki 健康度 ✅
- ⬆️ Ingest 按鈕（一鍵匯入）
- 🔍 Lint 按鈕（一鍵檢查）
- 知識庫檔案列表

### 5.3 三種管理方式

| 方式 | 用途 | 場景 |
|------|------|------|
| IDE curl | 開發時快速確認 | 剛 ingest 完確認成功（Step 2-3） |
| TG 問 Agent | 隨時隨地檢查 | 不在電腦前也能管 |
| Admin 後台 | 全盤總覽 + 一鍵操作 | 管理者日常監控 |

---

## 📊 完成度分級

| 等級 | 達成條件 |
|------|----------|
| 🎯 保底 | wiki/ 有 4 篇 + curl query 有結果 |
| ✅ 標準 | TG 問舊知識+新知識都有引用 + lint healthy |
| 🏆 快速 | AI 搜尋產知識 + IDE/TG/Admin 三端驗證 |

## 🏠 回家練習

1. 📝 Kiro：「搜尋我們公司其他產品的競品資料，整理成 knowledge/raw/ 格式並匯入」
2. 📝 Kiro：「檢查 Wiki 健康度，修復所有問題」
3. 思考：哪些公司文件丟進去後，新人就能自己問 Agent 找答案？

---

*本堂重點：AI 搜尋 → 存 raw → ingest → wiki → Agent 能引用 = 知識成長。*
*IDE curl 確認 API 正常 → TG 確認 Agent 在用 → Admin 後台一鍵管理。*
