# 🚀 第三堂：LLM Wiki — 它能「記住」

## 🎯 課堂目標

完成後你能：
1. 理解 raw/ → ingest → wiki/ 的知識轉換流程
2. 體驗 RAG 問答（有引用 vs 無引用的差異）
3. 把自己的文件丟進 Wiki 讓 Agent 能回答
4. 理解自演化循環（memory → raw → wiki → 更準）

## 📋 前置條件

- samples/ai-bot 能跑 + GEMINI_API_KEY 已設定

---

## Step 1：匯入知識（0-5 min）

**做什麼**：觸發 ingest，把 raw/ 轉為 wiki/ 結構化知識  
**為什麼**：Wiki 需要有內容，RAG 才能引用

💻 終端：
```bash
curl -X POST http://localhost:8000/api/v1/wiki/ingest
```

✅ 預期結果：
- `{"ingested": ["agent-design-notes.md", "common-errors.md", "python-async-guide.md"], "count": 3}`
- `knowledge/wiki/` 出現 3 個 .md（含 frontmatter）

⚠️ 如果 count: 0 → 確認 knowledge/raw/ 有檔案

---

## Step 2：RAG 問答對比（5-15 min）⭐ 核心

**做什麼**：問問題觀察 Agent 引用 Wiki 回答，再對比無 Wiki 的情況  
**為什麼**：體驗「有依據的回答」vs「幻覺」

📱 Telegram（有 Wiki）：
1. `/agents` → Admin → 問「什麼是 asyncio？」
2. 觀察底部是否有「📚 參考：...」

📝 Kiro IDE 輸入（移除 Wiki 做對比）：
```
幫我把 knowledge/wiki/ 下的 .md 檔案暫時移到 /tmp/wiki-backup/
```

📱 Telegram 再問同一問題 → 觀察回答變粗略、無引用

📝 Kiro IDE 輸入（還原）：
```
把 /tmp/wiki-backup/ 的檔案移回 knowledge/wiki/
```

✅ 預期結果：有 Wiki = 詳細+引用 / 無 Wiki = 簡短+無引用

---

## Step 3：丟自己的文件（15-30 min）

**做什麼**：用 Kiro 建立自己的知識文件，讓 Agent 能回答  
**為什麼**：你的筆記 → Agent 能引用回答 = 個人知識庫

📝 Kiro IDE 輸入：
```
在 knowledge/raw/ 建立 docker-notes.md，內容：
一份 Docker 常用指令筆記，包含：
- 基本操作（up/down/logs）
- 除錯技巧（exec/inspect）
要有 frontmatter（title, type, tags, created）
```

💻 觸發 ingest：
```bash
curl -X POST http://localhost:8000/api/v1/wiki/ingest
```

📱 Telegram 驗證：問「Docker 怎麼看 log？」

✅ 預期結果：Agent 引用你的筆記回答，附「📚 參考：docker-notes」

---

## Step 4：Lint 檢查（30-40 min）

**做什麼**：檢查 Wiki 健康度  
**為什麼**：知識庫需要維護品質

💻 終端：
```bash
curl http://localhost:8000/api/v1/wiki/lint
```

✅ 預期結果：`{"issues": [], "healthy": true}`

如果有 issues：
📝 Kiro IDE 輸入：
```
Wiki lint 回報問題：（貼上 issues）
幫我修復
```

---

## Step 5：觀察自演化循環（40-50 min）

**做什麼**：觀察 memory.py 自動寫入 + 理解成長循環  
**為什麼**：Agent 越用越聰明的核心機制

📝 Kiro IDE 輸入：
```
列出 agents/admin-agent/knowledge/raw/ 的檔案
```

✅ 預期結果：看到今天對話的 memory 檔案（`2026-07-02_XXXX_userXXX.md`）

📝 Kiro IDE 問：
```
解釋自演化循環：對話 → memory → raw → ingest → wiki → RAG 更準
```

✅ 理解重點：
```
對話 → memory.py 自動寫入 raw/
    → 定期 ingest → wiki/ 成長
    → 下次 RAG 更準 = 越用越聰明
```

---

## 📊 完成度分級

| 等級 | 達成條件 |
|------|----------|
| 🎯 保底 | ingest 成功 + wiki/ 有頁面 |
| ✅ 標準 | RAG 問答有引用 + 丟自己文件能被查到 |
| 🏆 快速 | 對比體驗 + lint + 理解自演化循環 |

## 🏠 回家練習

1. 📝 Kiro：「把我的技術筆記整理成 knowledge/raw/ 格式並 ingest」
2. 📝 Kiro：「幫 wiki 頁面加入 [[wikilink]] 連結」
3. 思考：公司哪些文件適合丟進 Wiki？

---

*本堂重點：RAG = 有依據的回答。自演化 = 越用越聰明。*
