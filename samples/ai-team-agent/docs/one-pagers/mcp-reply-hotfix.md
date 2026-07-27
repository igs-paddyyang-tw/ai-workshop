---
title: "MCP Reply 鏈路修復"
type: onepager
status: completed
created: 2026-07-27
updated: 2026-07-27
language: zh-TW
author: admin-agent
priority: P0
upgraded_to: null
---

# MCP Reply 鏈路修復

## 問題

Agent 透過 MCP `reply()` tool 呼叫 `POST /api/chat/reply` 時回傳 **404 Not Found**，導致所有 Agent 無法回覆使用者。診斷發現共 7 個問題，其中 2 個為核心 blocker。

## 根因分析

| # | 問題 | 嚴重度 | 根因 |
|---|------|--------|------|
| 1 | Chat Router 未註冊 | P0 | `chat.py` 定義了 router 但 `router.py` 從未 import/include |
| 2 | sync/async 混用 | P0 | `bootstrap.py` 在 async handler 中用 sync `get_db()` 配 async `fetch_one()` |
| 3 | DB 連線洩漏 | P1 | `_on_complete_with_db` 取得 conn 後未 close() |
| 4 | UTF-8 surrogate 編碼 | P1 | mcp_stdio.py stdin/stdout 在 Windows 混入 surrogate 字元 |
| 5 | allowed_users 為空 | P2 | team.yaml 未填 Telegram user_id，任何人可觸發 Bot |
| 6 | 私有屬性直接存取 | P3 | `get_status()` 用 `_output_count` 非 property |
| 7 | 殘留測試 task | P3 | DB 有無主 pending task (b8177d1e) |

## 方案

### 修改清單

**router.py**（2 行）：
```python
from gateway.api.chat import router as chat_router
app.include_router(chat_router, prefix="/api/chat", tags=["chat"])
```

**bootstrap.py**（3 個 function）：
- `_on_complete_with_db`: `get_db()` → `await get_async_db()` + `await conn.close()`
- `_on_failed_with_db`: 同上
- `_on_task_assigned`: 同上

**mcp_stdio.py**（main_loop 前加）：
```python
import io
sys.stdin = io.TextIOWrapper(sys.stdin.buffer, encoding='utf-8', errors='replace')
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace', write_through=True)
```

**team.yaml**：填入實際 `allowed_users`

**persistent_daemon.py**：`_output_count` → `output_count`

## 計畫

| 步驟 | 預估 | 驗收條件 |
|------|------|---------|
| 1. 註冊 chat router | 5 min | curl /api/chat/reply 不再 404 |
| 2. 修 sync/async | 10 min | assign issue 不 crash |
| 3. 修 UTF-8 surrogate | 10 min | 中文 reply 不報 surrogate error |
| 4. 收尾（allowed_users + 清理） | 5 min | smoke test 36 passed 不退步 |
| **合計** | **~30 min** | |

## 風險

| 風險 | 緩解 |
|------|------|
| chat prefix 衝突 | 確認 /api/chat 無其他佔用 |
| async 改寫 race condition | WAL mode + 短生命週期 conn |
| surrogate replace 遮蔽錯誤 | 用 replace 非 ignore，保留可見 `?` |

## 成功指標

- MCP reply() → TG 收到回覆（E2E）
- Drift Score 維持 ≥ 97/100
- smoke_test 36 passed

---

## 品質檢查

- [x] 問題陳述明確
- [x] 目標與非目標可區分（修 bug，不重構）
- [x] 方案可執行（含具體程式碼）
- [x] 風險已列出
- [x] 成功指標可衡量
