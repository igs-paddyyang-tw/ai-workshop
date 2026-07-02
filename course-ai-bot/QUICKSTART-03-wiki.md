# 🚀 第三堂：LLM Wiki — 它能「記住」

## 🎯 課堂目標

完成後你能：
1. 在 Kiro IDE 內完成知識庫建構 + 驗證 RAG 有效
2. 讓 Agent 學會「你教它的東西」（丟文件 → 能回答）
3. 部署到 Telegram 確認使用者也能拿到正確答案
4. 理解自演化：每次對話都在讓 Agent 變聰明

## 📋 前置條件

- samples/ai-bot 能跑 + GEMINI_API_KEY 已設定

## 使用的 Skill

| Skill | 觸發方式 |
|-------|---------|
| `ark-wiki-engine` | 📝「匯入知識」「查知識」「Wiki 健康檢查」 |

---

# 前半段：Kiro IDE 開發 + 驗證（開發者視角）

## Step 1：建立基準 — 沒知識時的回答（0-5 min）

**做什麼**：在 Kiro 內問一個問題，記住「差」的回答  
**為什麼**：建立對比基準，等下加知識後看差異

📝 Kiro IDE 輸入：
```
用 wiki_query 查詢「asyncio Semaphore 怎麼用來限流」，
目前 Wiki 有什麼相關內容？
```

✅ 預期結果：
- 「Wiki 中沒有找到相關內容」或只有模糊匹配
- 記住這個狀態：**知識庫是空的，Agent 無法引用。**

---

## Step 2：匯入知識 + Kiro 內驗證（5-20 min）⭐ 核心

**做什麼**：匯入知識後，在 Kiro 內確認 RAG 有效  
**為什麼**：開發者先確認功能正常，再提供給使用者

📝 Kiro IDE 輸入：
```
匯入 knowledge/raw/ 的所有文件到 Wiki
```

→ 觸發 ark-wiki-engine ingest

✅ 預期結果：
- 「已匯入 3 篇：agent-design-notes.md, common-errors.md, python-async-guide.md」

📝 在 Kiro 內驗證（不需要開 Telegram）：
```
再查一次「asyncio Semaphore 怎麼用來限流」
```

✅ 預期結果：
- 找到 python-async-guide 的相關片段
- 有具體的程式碼範例和說明
- **跟 Step 1 明顯不同 — 這就是 RAG 的效果**

📝 追加驗證：
```
查詢「常見的 Bot 錯誤怎麼排查」
```

✅ 預期：匹配到 common-errors.md 的內容

---

## Step 3：建自己的知識 + Kiro 內驗證（20-35 min）

**做什麼**：建一份自己的文件，匯入後在 Kiro 確認能查到  
**為什麼**：確認「教它新東西」的流程可行

📝 Kiro IDE 輸入：
```
在 knowledge/raw/ 建立 docker-notes.md：
Docker Compose 常用指令筆記，包含：
- 啟動：docker compose up -d
- 停止：docker compose down
- 看 log：docker compose logs -f
- 進容器：docker exec -it <name> bash
- 清理：docker system prune
要有 frontmatter（title, type, tags, created）
```

📝 匯入：
```
匯入剛建立的文件到 Wiki
```

📝 在 Kiro 內驗證：
```
查詢「Docker 怎麼看即時 log」
```

✅ 預期結果：
- 回傳「docker compose logs -f」相關內容
- 來源標記 docker-notes

📝 再試一個：
```
查詢「Docker 怎麼清理空間」
```

✅ 預期：匹配到 docker system prune

💡 **到這裡，開發者端確認完成 — 知識庫有效、查詢正確。**

---

# 後半段：Telegram 上線驗證（使用者 / 第三方視角）

## Step 4：Telegram 驗證 — 使用者能拿到答案（35-45 min）

**做什麼**：切到 Telegram，確認「真實使用者」也能拿到有引用的答案  
**為什麼**：Kiro 驗證 = 開發 OK。Telegram 驗證 = 上線 OK、第三方可用。

📱 Telegram：
1. `/agents` → Admin
2. 問「什麼是 asyncio 的 Semaphore？」
3. 問「Docker 怎麼看 log？」

✅ 預期結果：
- 回答詳細 + 底部有「📚 參考：python-async-guide」
- Docker 問題也能回答 + 引用「docker-notes」
- **使用者體驗 = 有依據、不幻覺、可信任**

📱 對比測試：問一個 Wiki 沒有的問題
- 「Kubernetes 怎麼設定 HPA？」
- 觀察：回答沒有「📚 參考」→ Agent 誠實表示沒有相關知識

💡 **能回答的有引用，不能的坦白說 — 這就是可信任的 AI。**

---

## Step 5：自演化觀察（45-50 min）

**做什麼**：觀察 memory 自動記錄 + 理解成長循環  
**為什麼**：不只是「丟文件進去」，Agent 會自己從對話中學習

📝 Kiro IDE 輸入：
```
列出 agents/admin-agent/knowledge/raw/ 的檔案
```

✅ 預期結果：
- 看到今天對話的 memory 檔案
- 打開看：記錄了 user_id + 問題 + Agent 的回答

📝 Kiro IDE 問：
```
如果我把這些 memory 定期 ingest 到 Wiki，
Agent 會越來越了解使用者常問什麼、偏好什麼。
這個循環怎麼設定自動化？
```

✅ 理解重點：
```
使用者對話 → memory 自動記錄
    → 定期 ingest → Wiki 成長
    → 下次回答更精準
    → Agent 越用越聰明 = 自演化

這就是「學完帶走後，系統會自己成長」的核心價值。
```

---

## 📊 完成度分級

| 等級 | 達成條件 |
|------|----------|
| 🎯 保底 | Kiro 內 ingest 成功 + 查詢有結果 |
| ✅ 標準 | Kiro 驗證 + Telegram 使用者也能拿到有引用的答案 |
| 🏆 快速 | 建自己文件 + 雙端驗證 + 理解自演化循環 |

## 🏠 回家練習

1. 📝 Kiro：「把我的 5 份技術筆記整理成 knowledge/raw/ 格式並匯入」
2. 📝 Kiro：「檢查 Wiki 健康度，修復所有問題」
3. 思考：公司哪些文件丟進去後，新人就能自己問 Agent 找答案？

---

*本堂重點：Kiro 驗證 = 開發 OK。Telegram 驗證 = 上線 OK。自演化 = 越用越聰明。*
