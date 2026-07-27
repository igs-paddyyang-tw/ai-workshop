# Task Plan: 任務系統統一計畫

## 背景

系統目前有兩套獨立的任務表：

| 表 | 寫入來源 | 讀取來源 | 狀態欄位值 |
|---|---------|---------|----------|
| `issues` | MCP `create_task` / `delegate_task`、`/api/issues` | MCP `list_tasks`、`/api/issues` | pending / assigned / completed / failed |
| `tasks` | `/api/tasks`、`TaskLifecycle` | `/api/board`、`/api/board` | backlog / queued / claimed / executing / blocked / completed / failed |

**問題**：MCP agent 寫 issues，/board 讀 tasks → 看板永遠是空的。

## 已完成（短期修復 A）

- ✅ `get_board()` 合併讀取 tasks + issues，issues status 映射到 board status
- 效果：`/board` COMPLETED today 從 0 → 8，看板立即可用

## 目標

消除雙表，MCP 和 Board 使用同一套 tasks 表，確保資料一致。

---

## 階段分解

### Phase 1：MCP 工具改寫 tasks 表 🔴 高優先
**現狀**：`mcp_stdio.py` 的 `_tool_create_task` / `_tool_update_task` / `_tool_list_tasks` 都打 `/api/issues`
**目標**：改打 `/api/tasks` 和 `/api/board` endpoints

- [ ] 1-1 `_tool_create_task` 改打 `POST /api/tasks`
- [ ] 1-2 `_tool_update_task` 改打 `PATCH /api/tasks/{id}/complete`（需建立此 endpoint）
- [ ] 1-3 `_tool_list_tasks` 改打 `GET /api/board`，回傳扁平化清單
- [ ] 1-4 `board.py` 補 `PATCH /api/tasks/{id}/complete` endpoint

**驗收**：MCP `create_task` 後，`/board` 立即出現該任務

---

### Phase 2：issues 表資料遷移 🟡 中優先
**現狀**：舊 issues 資料（8筆 completed）還在 issues 表，未來新任務走 tasks 表
**目標**：將 issues 資料搬到 tasks，或永久保留兩表並行

選項：
- [ ] 2-A 寫 migration SQL 將 issues → tasks（一次性遷移）
- [ ] 2-B 保留雙表，`get_board` 永久合併（維持現狀，較安全）

**建議**：選 2-B 直到確認 Phase 1 穩定後再做 2-A

---

### Phase 3：status 欄位統一 🟢 低優先
**現狀**：issues 用 `pending/assigned`，tasks 用 `backlog/queued/claimed`
**目標**：統一狀態機

- [ ] 3-1 決定最終狀態集（建議採 tasks 的 7 狀態）
- [ ] 3-2 migration 更新 issues 表的 status check constraint
- [ ] 3-3 更新所有 STATUS_MAP 引用

---

### Phase 4：廢棄 `/api/issues` 🟢 低優先
**目標**：所有任務操作統一走 `/api/tasks` / `/api/board`

- [ ] 4-1 確認沒有其他地方依賴 `/api/issues`
- [ ] 4-2 將 `/api/issues` 標記 deprecated，加 redirect
- [ ] 4-3 三個月後移除

---

## 進度狀態

| Phase | 狀態 | 完成時間 |
|-------|------|---------|
| 短期修復 A（get_board 合併） | ✅ 完成 | 2026-07-27 |
| Phase 1：MCP 改寫 tasks 表 | ✅ 完成 | 2026-07-27 |
| Phase 2：資料遷移 | ✅ 暫緩（保留雙表 fallback） | — |
| Phase 3：status 統一 | ✅ 完成 | 2026-07-27 |
| Phase 4：廢棄 /api/issues | ✅ 完成（加 Deprecation header） | 2026-07-27 |

## 約束

- Phase 1 執行前服務需重啟測試
- 不影響現有 MCP tools 的回傳格式（agent 依賴此回傳）
- 每個 Phase 完成後跑 smoke_test.py 確認
