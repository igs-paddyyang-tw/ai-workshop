# 🚀 第三堂：LLM Wiki — 它能「記住」

## 🎯 課堂目標

完成後你能：
1. 理解 raw/ → wiki/ 的 ingest 流程（原始文件如何變成可查詢知識）
2. 體驗 RAG 問答差異（有引用 vs 無引用，精準 vs 模糊）
3. 把自己的文件丟進 Wiki，讓 Agent 能根據你的知識回答
4. 理解自演化循環：對話 → memory → raw → wiki → 更準確的回答

## 📋 前置條件

- 完成第一堂，Bot + Wiki Server 能正常啟動
- Wiki Server 運行中（`http://localhost:8000`）
- 至少一份 .md 技術筆記（或使用 sample-docs/）
- 約 50 分鐘完整時間

---

## Step 1：匯入知識（0-5 min）

**做什麼**：觸發 ingest，把 raw/ 目錄的文件轉成 wiki 知識  
**為什麼**：Agent 的知識不是憑空來的，需要明確匯入

**操作**：
```bash
curl -X POST http://localhost:8000/api/v1/wiki/ingest
```

**✅ 預期結果**：回傳 `{"ingested": ["agent-design-notes.md", ...], "count": 3}`  
**⚠️ 如果不成功**：Connection refused → 確認 Wiki Server 已啟動（`python wiki_server.py`）；count: 0 → 確認 `knowledge/raw/` 有 .md 檔案  
**💡 確認**：`ls knowledge/wiki/` 應出現對應的 .md 檔案

---

## Step 2：RAG 問答（5-15 min）⭐ 核心體驗

**做什麼**：問 Agent 一個知識庫裡有的問題，觀察引用效果  
**為什麼**：親眼看到「有知識」vs「沒知識」的回答品質差異

**操作**：
1. 📱 在 Telegram 輸入 `/agents` → 選 Admin
2. 問：「什麼是 asyncio？」
3. 觀察回答底部的引用來源

**對比實驗**：
```bash
mv knowledge/wiki/*.md /tmp/wiki-backup/
# 再問同一問題，觀察差異
mv /tmp/wiki-backup/*.md knowledge/wiki/  # 還原
```

**✅ 預期結果**：有 Wiki 時回答精準 + 底部顯示「📚 參考：agent-design-notes.md」；無 Wiki 時回答模糊、無引用  
**⚠️ 如果不成功**：沒有引用標記 → 確認 Agent 有啟用 RAG 模組（檢查 agent config）

---

## Step 3：丟自己的文件（15-30 min）

**做什麼**：把你自己的技術筆記匯入 Wiki，讓 Agent 能回答  
**為什麼**：證明系統是通用的，任何知識都能讓 Agent 學會

**操作**：
```bash
# 準備你的筆記（或用範例）
cp your-notes.md knowledge/raw/
# 沒有筆記？用範例：
cp sample-docs/python-tips.md knowledge/raw/

# 重新匯入
curl -X POST http://localhost:8000/api/v1/wiki/ingest

# 問筆記裡的內容
# 例如筆記寫了 decorator 用法 → 問「怎麼寫 Python decorator？」
```

**✅ 預期結果**：Agent 能根據你的筆記內容回答，附引用來源檔名  
**⚠️ 如果不成功**：回答沒引用你的檔案 → 確認檔案格式是 .md；確認 ingest 回傳有包含該檔名

---

## Step 4：Lint 檢查（30-40 min）

**做什麼**：用 lint API 檢查 Wiki 知識庫的健康狀態  
**為什麼**：知識庫也需要維護，壞掉的連結會影響回答品質

**操作**：
```bash
curl http://localhost:8000/api/v1/wiki/lint
```

**✅ 預期結果**：回傳 `{"issues": [...], "healthy": true}` 或列出問題清單  
**⚠️ 如果不成功**：404 → 確認 API 路徑正確；issues 一堆 → 這是正常的，下一步修復  
**💡 常見問題類型**：孤立頁面（無人引用）、斷裂連結、缺少 frontmatter

---

## Step 5：自演化循環（40-50 min）

**做什麼**：觀察對話如何自動沉澱為知識  
**為什麼**：這是系統最強大的地方 — 越用越聰明

**操作**：
1. 跟 Admin Agent 聊幾輪技術問題
2. 打開 `agents/admin-agent/knowledge/raw/`
3. 觀察新出現的 memory 檔案

**✅ 預期結果**：看到今天日期的 `.md` 檔案，內含剛才對話的摘要  
**⚠️ 如果不成功**：沒有新檔案 → 確認 `memory.py` 模組有啟用（檢查 agent 啟動 log）  
**💡 完整循環**：

```
對話 → memory.py 自動寫入 raw/
     → 下次 ingest 轉入 wiki/
     → Agent 下次回答更精準
     = 自演化 🔄
```

---

## 📊 完成度分級

| 等級 | 達成條件 |
|------|----------|
| ⭐ 基礎 | 完成 Step 1-2，能 ingest 並看到 RAG 引用效果 |
| ⭐⭐ 標準 | 完成 Step 3，自己的文件成功被 Agent 引用 |
| ⭐⭐⭐ 進階 | 完成 Step 4-5，理解 lint + 自演化循環的意義 |

## 🏠 回家練習

1. 匯入 3-5 份自己的技術筆記，建立個人知識庫
2. 用 lint 修復所有 issues，達到 `healthy: true`
3. 連續使用 3 天，觀察 memory 累積後回答品質的變化
4. 思考：哪些知識適合放 Wiki？哪些不適合？界線在哪？
