---
title: "修正紀錄 2026-07-07"
type: changelog
status: done
language: zh-TW
created: 2026-07-07
---

# 修正紀錄 2026-07-07

## 1. TG 回覆 ANSI 亂碼修正

**問題**：kiro-cli 回傳帶 ANSI escape codes + `> ` 引用前綴，TG 顯示亂碼。

```
修正前：[38;5;141m>  [0m嗨！有什麼我可以幫你的嗎？
修正後：👑 [admin-agent]
        嗨！有什麼我可以幫你的嗎？
```

**修改檔案**：
| 檔案 | 修改 |
|------|------|
| `src/agent/process.py` | `_execute()` 解碼後呼叫 `strip_ansi()` + `strip_tool_noise()` |
| `src/bot/handlers.py` | 回覆前再次清除殘留 ANSI + 移除 `> ` 前綴 |

---

## 2. Wiki RAG 回覆「沒有資料」修正

**問題**：知識庫搜尋有命中檔案（sources 有列出），但 Gemini RAG 只收到一行 snippet（200 字），內容不足以回答問題，導致回「目前知識庫沒有這方面的資料」。

**根因**：`_rag_answer()` 傳給 Gemini 的 context 只有 `_extract_snippet()` 的一行結果，而非完整文件。

**修改**：
- `_rag_answer()` 改為讀取完整 wiki 文件（每篇限 2000 字，最多 5 篇）
- 新增 `_read_wiki_file()` 方法從 wiki/ 目錄讀完整 .md
- 模型改用 `GEMINI_MODEL` 環境變數（不再硬碼）

**修改檔案**：`src/wiki/engine.py`

---

## 3. 同步 upstream（templates/ Web UI）

**來源**：`github.com/igs-paddyyang-tw/ai-workshop/tree/main/samples/ai-bot`

**新增**：
| 檔案 | 說明 |
|------|------|
| `templates/index.html` | 💬 Chat 聊天室（8 Agent 切換） |
| `templates/admin.html` | ⚙️ Admin 管理介面（KPI + Ingest/Lint） |
| `templates/api-docs.html` | 📖 API 文件（暗黑風格 + Try 按鈕） |
| `templates/tech-daily.html` | 科技日報模板 |

---

## 4. 文件整合

- 合併 `docs/optimization-windows-logging.md` + `docs/teaching-optimization-prompt.md` → 單一文件
- 刪除 `docs/teaching-optimization-prompt.md`

---

## 5. uvicorn reload + TG Bot 進程衝突修正

**問題**：`reload=True` 在 Windows 上 WatchFiles 偵測到變更後 spawn 新 process，TG Bot thread + logging handler 在 spawn 時搶佔 → `KeyboardInterrupt`。

**根因**：uvicorn reload 用 `multiprocessing.Process` spawn 子進程，子進程初始化呼叫 `logging.shutdown()` 清理舊 handler，此時 TG Bot thread 仍在使用同一個 log stream。

**解法**：將 TG Bot 拆成獨立子進程，不受 uvicorn reload 影響。

```
start.py（主進程）
├── 子進程: python -m src.bot.run    ← TG Bot + Agent 服務
│   └── 獨立 event loop + logging，完全隔離
└── 主 thread: uvicorn reload=True   ← FastAPI only
    └── reload 只 spawn API worker，不碰 Bot
```

**修改**：
- `start.py` — 移除 threading，改用 `subprocess.Popen` 啟動 Bot
- 新增 `src/bot/run.py` — Bot 獨立進程入口（含 Agent 常駐服務啟動）
- Ctrl+C 時 finally 區塊 terminate Bot 子進程

**結果**：`reload=True` 安全使用，改 src/ 檔案時 API 自動重載，Bot 不受影響。

---

## 6. Wiki Graph API 端點修正

**問題**：`/graph` 頁面空白，`/api/v1/graph` 回 404 → 補上端點後回傳格式與前端 `graph.html` 不符。

**修改**：重寫 `/api/v1/graph` 回傳完整知識圖譜：
- 8 個 Agent 節點（type=agent）
- 每個 Agent 的 Skills（type=skill）+ `has_skill` 連線
- 每個 Agent 的私有知識（type=wiki）+ `reads_wiki` 連線
- 全域 Wiki 頁面（type=wiki）+ 共享 tag 的 `shared_tag` 連線
- 回傳格式：`{nodes: [{id, label, type, meta}], links: [{source, target, relation}]}`

**修改檔案**：`src/server/main.py`

---

## 7. Dashboard 知識庫列表硬碼修正

**問題**：`/admin` Dashboard 的「📚 知識庫」區塊永遠只顯示 3 個硬碼檔案。

**根因**：`admin.html` 的 `loadWiki()` 直接 fallback 到硬碼陣列。

**修改**：改用 `/api/v1/wiki/pages` API 動態載入所有 wiki 頁面。

**修改檔案**：`templates/admin.html`

---

## 8. 品牌用語統一：「個體 Agent」→「專家 Agent」

**修改**：全域替換所有出現「個體 Agent」的地方。

| 檔案 | 位置 |
|------|------|
| `templates/admin.html` | 系統資訊 → 平台名稱 |
| `templates/api-docs.html` | API 描述文字 |
| `start.py` | 模組 docstring + 啟動 banner |
| `src/server/main.py` | FastAPI title |

---

## 9. Ingest 只處理根目錄修正

**問題**：Dashboard 點「⬆️ Ingest」只匯入根目錄，子資料夾被忽略。

**根因**：`WikiEngine.ingest()` 使用 `raw_dir.glob("*.md")`（只掃第一層）。

**修改**：改用 `raw_dir.rglob("*.md")`（遞迴掃描所有子資料夾）。

**修改檔案**：`src/wiki/engine.py`

---

## 10. Wiki 頁面瀏覽器「沒有找到頁面」修正

**問題**：`/wiki` 頁面左側檔案樹顯示「沒有找到頁面」，實際 wiki 目錄有 80+ 檔案。

**根因**：前端期望樹狀結構（`{type: "file"|"folder"}`），API 回傳平面陣列。

**修改**：
- `/api/v1/wiki/pages` 改回傳樹狀結構
- `/api/v1/wiki/pages/{filepath:path}` 支援子資料夾路徑

**修改檔案**：`src/server/main.py`

---

## 修改檔案總覽

| 檔案 | 變更類型 |
|------|---------|
| `start.py` | 重寫 — Bot 拆獨立子進程 + uvicorn reload 安全 |
| `src/server/main.py` | 新增+修正 — graph API + wiki/pages 樹狀結構 |
| `src/bot/run.py` | 新增 — Bot 獨立進程入口 |
| `src/agent/process.py` | 修正 — ANSI 清除 |
| `src/bot/handlers.py` | 修正 — 回覆前清除 ANSI + `> ` 前綴 |
| `src/wiki/engine.py` | 修正 — RAG 傳完整文件 + ingest rglob |
| `templates/admin.html` | 修正 — 動態 API + 品牌用語 |
| `templates/index.html` | 新增 |
| `templates/api-docs.html` | 新增 + 品牌用語修正 |
| `templates/tech-daily.html` | 新增 |
| `docs/optimization-windows-logging.md` | 重寫（整合） |

## 待確認

- [ ] #2 Wiki RAG 讀完整文件是否需要 token 上限保護
- [ ] #5 Bot 子進程在 Linux 環境的行為
- [ ] #8 品牌用語是否也要更新教學文件（QUICKSTART 系列）
