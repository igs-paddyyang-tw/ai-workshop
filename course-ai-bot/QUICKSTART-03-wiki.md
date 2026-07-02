# 🚀 第三堂：LLM Wiki — 它能「記住」

## 🎯 課堂目標

完成後你能：
1. 用自然語言觸發知識匯入（不需要記 curl 指令）
2. 體驗「加入知識前後」Agent 回答品質的差異
3. 讓 Agent 學會「你教它的東西」（丟文件 → 能回答）
4. 理解自演化：每次對話都在讓 Agent 變聰明

## 📋 前置條件

- samples/ai-bot 能跑 + GEMINI_API_KEY 已設定

## 使用的 Skill

| Skill | 觸發方式 |
|-------|---------|
| `ark-wiki-engine` | 📝「匯入知識」「查知識」「Wiki 健康檢查」 |

---

## Step 1：先問一個 Agent 不會的問題（0-5 min）

**做什麼**：問一個知識庫還沒有的問題，記住這個「差」的回答  
**為什麼**：建立對比基準 — 等下加入知識後再問同一問題

📱 Telegram：
1. `/agents` → Admin
2. 問「什麼是 asyncio 的 Semaphore？怎麼用來限流？」
3. **截圖或記住這個回答**（可能很泛、沒有具體範例）

✅ 預期結果：
- Agent 用 Gemini 通用知識回答
- 沒有「📚 參考」引用
- 回答可能正確但不夠具體

💡 記住這個感覺：**這就是「沒有 Wiki」的狀態。**

---

## Step 2：匯入知識 + 再問一次（5-20 min）⭐ 核心

**做什麼**：用自然語言觸發 ingest，然後再問同一問題  
**為什麼**：體驗「加入知識後 Agent 立刻變聰明」

📝 Kiro IDE 輸入：
```
匯入 knowledge/raw/ 資料夾的所有文件到 Wiki
```

→ 觸發 ark-wiki-engine 的 ingest 功能

✅ 預期結果：
- Kiro 回報「已匯入 3 篇：agent-design-notes.md, common-errors.md, python-async-guide.md」
- `knowledge/wiki/` 出現結構化頁面

📱 Telegram 再問同一問題：
- 「什麼是 asyncio 的 Semaphore？怎麼用來限流？」

✅ 預期結果（對比 Step 1）：
- 回答更具體（有程式碼範例）
- 底部出現「📚 參考：python-async-guide」
- **明顯比 Step 1 的回答好**

💡 **這就是 RAG 的價值：有依據 → 更準確 → 不幻覺。**

---

## Step 3：教 Agent 新知識（20-35 min）

**做什麼**：用 Kiro 建一份你的知識文件，讓 Agent 學會新東西  
**為什麼**：你教它什麼，它就會什麼 — 這是「個人知識庫」的核心

📝 Kiro IDE 輸入：
```
幫我在 knowledge/raw/ 建立一份 docker-notes.md：
內容是 Docker Compose 的常用指令和除錯技巧，
包含：啟動(up)、停止(down)、看 log(logs -f)、進容器(exec)、清理(prune)
要有 frontmatter
```

→ Kiro 建立檔案

📝 Kiro IDE 輸入：
```
匯入剛建立的文件到 Wiki
```

→ ingest 觸發

📱 Telegram 驗證：
- 問「Docker Compose 怎麼看即時 log？」

✅ 預期結果：
- Agent 回答「docker compose logs -f」
- 附「📚 參考：docker-notes」

🔥 延伸（用自己的真實筆記）：

📝 Kiro IDE 輸入：
```
在 knowledge/raw/ 建立一份我們公司的 API 規範文件：
- 命名規則：kebab-case
- 版本路徑：/api/v1/
- 回傳格式：{ data, error, meta }
- 錯誤碼：400/401/403/404/500
```

📝 接著：「匯入到 Wiki」

📱 驗證：問「我們公司 API 的錯誤碼有哪些？」

---

## Step 4：Wiki 健康檢查（35-45 min）

**做什麼**：用自然語言觸發 lint，維護知識品質  
**為什麼**：知識庫不是丟了就好，要持續維護

📝 Kiro IDE 輸入：
```
幫我檢查 Wiki 的健康狀態
```

→ 觸發 ark-wiki-engine 的 lint 功能

✅ 預期結果（健康）：
- 「Wiki 健康 ✅，0 個問題」

如果有問題：
- 缺 frontmatter → 📝「幫我修復缺少 frontmatter 的頁面」
- 孤立頁面 → 📝「幫 wiki 頁面加入 [[wikilink]] 互相連結」

📝 進階操作：
```
分析 Wiki 的知識圖譜，有哪些頁面互相連結？有哪些是孤立的？
```

---

## Step 5：觀察自演化（45-50 min）

**做什麼**：看到「對話自動變成知識」的證據  
**為什麼**：Agent 不只是工具，它會「成長」

📝 Kiro IDE 輸入：
```
列出 agents/admin-agent/knowledge/raw/ 目錄的檔案，
這些是 Agent 自動記錄的對話記憶
```

✅ 預期結果：
- 看到今天的 memory 檔案（`2026-07-02_XXXX_userXXX.md`）
- 打開看：記錄了 user_id + 問題 + 回答

📝 Kiro IDE 問：
```
如果我把這些 memory 也 ingest 到 Wiki，會發生什麼？
```

✅ 理解重點：
```
你的每次對話
    → memory.py 自動記錄到 raw/
    → 定期 ingest → wiki/ 累積
    → 下次問類似問題 → 回答更準
    → Agent 越用越懂你 = 自演化
```

💡 **一人學會，永久可查。這就是知識庫的終極價值。**

---

## 📊 完成度分級

| 等級 | 達成條件 |
|------|----------|
| 🎯 保底 | ingest 成功 + wiki/ 有頁面 |
| ✅ 標準 | 體驗到「加知識前後」回答品質差異 |
| 🏆 快速 | 建自己文件 + lint + 理解自演化循環 |

## 🏠 回家練習

1. 📝 Kiro：「把我電腦上的 5 份技術筆記整理成 knowledge/raw/ 格式並匯入」
2. 📝 Kiro：「幫 Wiki 頁面建立 [[wikilink]] 連結，加強知識圖譜」
3. 思考：公司的哪些文件適合丟進 Wiki？（新人手冊？API 文件？SOP？）

---

*本堂重點：你教它什麼，它就會什麼。RAG = 有依據的回答。自演化 = 越用越聰明。*
