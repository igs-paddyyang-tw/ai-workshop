# 🚀 第三堂：LLM Wiki — 它能「記住」

## 🎯 課堂目標

你加的知識，Agent 馬上能引用回答。

## 📋 前置條件

- 已完成第一堂（samples/ai-bot 能跑 + GEMINI_API_KEY 已設定）
- Kiro IDE（含 .kiro/skills/ark-wiki-engine）

## 📖 本堂知識（2 分鐘看完）

### LLM Wiki = 你的 AI 筆記本
- 你丟筆記進去 → Agent 能引用回答（不用靠猜）
- 有引用 📚 = 有依據 / 沒引用 = Agent 在猜
- 跟 Google 的差別：Google 搜全世界，Wiki 只搜你自己的資料

### 三個動作

| 動作 | 做什麼 | 類比 |
|------|--------|------|
| Ingest | 把文件丟進 Wiki | 把筆記放進書架 |
| Query | 問問題，Wiki 找答案 | 翻書架找相關的 |
| Lint | 檢查品質 | 確認書有沒有目錄和標籤 |

### 兩種驗證方式

| 方式 | 誰用 | 做什麼 |
|------|------|--------|
| 📝 IDE 對話 | 所有人 | 問 Kiro 問題，看有沒有引用 |
| 💻 curl API | 軟體人員 | 直接打 API 確認系統回傳 |

💡 `raw/` = 你丟的原始文件 → `ingest` = 放進書架 → `wiki/` = Agent 能翻的書

---

# IDE 開發

## Step 1：查知識 — 確認現狀（0-5 min）

**做什麼**：先問一個 Wiki 有的問題 + 一個沒有的問題，建立基準

📝 Kiro IDE 輸入（所有人）：
```
讀取 agents/market-agent/.kiro/steering/SOUL.md，
用 market-agent 的人格回答：「Ocean King 3 跟 Ocean King 2 有什麼差別？」
```

✅ 預期：Kiro 能回答（因為它會讀 wiki/ 的檔案）

📝 再問一個 Wiki 沒有的：
```
用 market-agent 的人格回答：「最近老虎機市場有什麼新趨勢？」
```

✅ 預期：回答比較泛（Wiki 沒有這份資料）→ Step 2 你來加

💻 軟體人員加做（確認 API 正常）：
```
幫我在終端執行：
curl -X POST http://localhost:8000/api/v1/wiki/query -H "Content-Type: application/json" -d '{"q":"Ocean King"}'
```

✅ 預期：回傳搜尋結果（確認 Bot server 和 WikiEngine 正常運作）

---

## Step 2：增加新知識（5-20 min）⭐ 核心

**做什麼**：用 AI 搜尋產出新知識 → 匯入 Wiki → 確認能查到

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

📝 匯入到 Wiki（所有人）：
```
把 knowledge/raw/slot-market-trends.md 匯入到 knowledge/wiki/
（確認放在根目錄的 knowledge/wiki/，不是 agents/ 下面）
並更新 knowledge/index.md
```

📝 確認能查到（所有人）：
```
用 market-agent 的人格回答：「最近老虎機市場有什麼新趨勢？」
```

✅ 預期：現在能回答了（Step 1 同一問題答不好 → 現在有引用）

💻 軟體人員加做：
```
curl -X POST http://localhost:8000/api/v1/wiki/query -H "Content-Type: application/json" -d '{"q":"老虎機市場趨勢"}'
```

💡 **跟第二堂的串接**：02 的 `ark-competitor-brief` Skill 讀 knowledge/wiki/ 產 SWOT — 你加的知識就是它的資料來源。

---

## Step 3：健康檢查（20-25 min）

**做什麼**：確認知識庫品質正常

📝 Kiro IDE 輸入（所有人）：
```
幫我檢查 knowledge/wiki/ 的所有檔案，
看看有沒有缺少 frontmatter 的（title / type / tags / created）
```

✅ 預期：Kiro 回報全部正常，或列出有問題的檔案

🌐 或開 Admin 後台（所有人）：
- http://localhost:8000/admin → 點「🔍 Lint」按鈕 → 看結果

💻 軟體人員加做：
```
curl http://localhost:8000/api/v1/wiki/lint
```

✅ 健康：`{"issues": [], "healthy": true}`

📝 確認最終數量：
```
列出 knowledge/wiki/ 有哪些檔案
```

✅ 預期：4 篇 + 全部健康 = 可以上線

---

# TG 上線驗證

💡 **為什麼要在 TG 再驗一次？**
- IDE = Kiro 自己回答（不經過 Agent 系統）
- TG = 真的走 Agent 運作（SOUL + Wiki RAG + Planner）
- TG 有 📚 引用 = **你建的系統在用你的知識庫**

💻 重啟：Ctrl+C → `python start.py`

## Step 4：使用知識 — Agent 引用回答（25-40 min）

### 4.1 驗證舊知識

📱 Telegram → Market：
1. 問「Ocean King 3 跟 Ocean King 2 有什麼差別？」

✅ 預期：回答有「📚 參考：ocean-king-analysis」

### 4.2 驗證新知識（你 Step 2 加的）

📱 Telegram → Market：
- 問「最近老虎機市場有什麼新趨勢？」

✅ 預期：引用 slot-market-trends.md + 有 📚 參考

💡 **Step 1 同問題答不好 → 現在有引用 = 知識成長生效**

### 4.3 對比：Wiki 沒有的

📱 問「PG Soft 的 Mahjong Ways 怎麼玩？」

✅ 預期：沒有 📚 → 坦白說不知道

💡 **能回答有引用，不能的坦白說 = 可信任的 AI。**

---

## Step 5：Admin 後台看全貌（40-45 min）

**做什麼**：開 Admin 後台確認一切正常

🌐 瀏覽器開 http://localhost:8000/admin

✅ 看到：
- 知識庫：4 篇 + ✅ 健康
- Agent 列表：8 個在線
- ⬆️ Ingest / 🔍 Lint 按鈕可用

🌐 也可以開 http://localhost:8000/wiki 看 Wiki 瀏覽器

💡 **三種管理方式**：IDE 對話 / TG 問 Agent / Admin 後台 — 看你方便用哪個。

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
