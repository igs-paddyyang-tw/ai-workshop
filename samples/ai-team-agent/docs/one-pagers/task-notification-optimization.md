---
title: "Task 通報完整性優化"
type: onepager
status: draft
created: 2026-07-15
language: zh-TW
---

# Task 通報完整性優化

## 問題陳述

### 現況

Telegram 任務完成通知顯示不完整：

```
✅ 任務完成
📋 #?
📝
```

- Task ID 顯示 `#?`（應顯示真實 ID）
- 📝 摘要行為空（應顯示任務產出摘要）
- 缺乏 agent 名稱、耗時等輔助資訊

### 期望

```
✅ 任務完成
📋 #a1b2c3d4 — 分析 TG 訊息產出流程
🤖 admin-agent
📝 已追蹤到 notifications.py，root cause 為 scheduler emit 缺少 issue_id
```

## 根因分析

### 問題 1：`#?` — Task ID 遺失

**傳遞鏈路斷裂**：

```
Agent 呼叫 update_task(task_id, status, output)
  → mcp_stdio.py:_tool_update_task
    → PATCH /api/issues/{task_id}/complete
      → issues.py:complete_issue
        → EventBus.emit(TASK_COMPLETED, data={issue_id, output})
          → notifications.py:on_task_completed
            → data.get('issue_id', '?')  ← 此處取值
```

斷裂點有兩處：

| 來源 | 問題 |
|------|------|
| `issues.py:86` | 正常路徑，`issue_id` 有值 ✅ |
| `runtime/scheduler.py:101` | emit 時 data 只有 `agent_id` + `job_name`，**缺少 `issue_id`** ❌ |

Scheduler 的 `_emit_completed` 沒帶 `issue_id`，導致 notifications fallback 到 `'?'`。

### 問題 2：📝 摘要為空

- `mcp_stdio.py` 定義 `output` 為非必填（default `""`）
- Agent 的 SOUL.md 雖定義 `[DONE] summary=...` 格式，但：
  - MCP tool 呼叫時 Agent 可能不帶 `output` 參數
  - Scheduler emit 時根本沒有 `output` 欄位
- `notifications.py:33` 直接用 `data.get("output", "")`，空值時 📝 後無內容

### 問題 3：格式不一致

- `notifications.py:on_task_completed` 與 `formatters.py:fmt_completed` 是兩套獨立實作
- `on_task_completed` 是簡化版（缺 agent_name、耗時、費用）
- `fmt_completed` 是完整版但未被通知流程使用

## 解決方案

### 修改 1：Scheduler emit 補齊欄位

**檔案**：`src/runtime/scheduler.py`
**函式**：`_emit_completed` (第 97 行)

```python
# Before
data={"agent_id": target, "job_name": job.get("name", ""), "source": "scheduler"}

# After
data={
    "agent_id": target,
    "issue_id": job.get("issue_id", job.get("name", "")),
    "output": f"排程任務 {job.get('name', '')} 執行完成",
    "source": "scheduler",
}
```

### 修改 2：Notification 統一使用 formatters

**檔案**：`src/gateway/telegram/notifications.py`
**函式**：`on_task_completed` (第 31 行)

```python
# Before
async def on_task_completed(self, event: Event) -> None:
    data = event.data
    output = data.get("output", "")
    summary = output[:200] + "..." if len(output) > 200 else output
    text = (
        f"✅ <b>任務完成</b>\n\n"
        f"📋 #{data.get('issue_id', '?')}\n"
        f"📝 {summary}"
    )
    await self._broadcast(text, self.LEVEL_INFO)

# After
async def on_task_completed(self, event: Event) -> None:
    data = event.data
    issue_id = data.get("issue_id", "")
    output = data.get("output", "")
    agent_id = data.get("agent_id", "")

    lines = ["✅ <b>任務完成</b>", ""]
    if issue_id:
        title = data.get("title", "")
        lines.append(f"📋 #{issue_id}" + (f" — {title}" if title else ""))
    if agent_id:
        lines.append(f"🤖 {agent_id}")
    if output:
        summary = output[:200] + "..." if len(output) > 200 else output
        lines.append(f"📝 {summary}")
    else:
        lines.append("📝 （無摘要）")

    await self._broadcast("\n".join(lines), self.LEVEL_INFO)
```

### 修改 3：issues API emit 時補帶 title

**檔案**：`src/gateway/api/issues.py`
**函式**：`complete_issue` (第 86 行)

```python
# Before
await bus.emit(Event(type=event_type, data={"issue_id": issue_id, "output": body.output}, source="api"))

# After
issue = await fetch_one(conn, "SELECT * FROM issues WHERE id=?", (issue_id,))
await bus.emit(Event(
    type=event_type,
    data={
        "issue_id": issue_id,
        "title": issue["title"] if issue else "",
        "assignee": issue.get("assignee", "") if issue else "",
        "output": body.output,
    },
    source="api",
))
```

### 修改 4：MCP update_task 增加 output 提示

**檔案**：`src/gateway/mcp_stdio.py`
**位置**：update_task tool schema (第 91 行)

將 `output` 的 description 改為更明確的提示：

```python
"output": {
    "type": "string",
    "description": "產出摘要（必填，簡述完成了什麼）",
    "default": "",
},
```

> 注：MCP schema 層面維持 optional 以向下相容，但透過 description 提示 Agent 填寫。

### 修改 5：Agent SOUL.md 強化規範

各 Agent 的 SOUL.md `Output Marker` 章節補充：

```markdown
## 回報規範
- 呼叫 `update_task` 時 **必須** 填寫 `output` 欄位
- output 格式：一句話摘要（≤ 100 字），說明做了什麼
- 禁止空值或僅填 "done"
```

## 影響範圍

| 檔案 | 修改幅度 | 風險 |
|------|---------|------|
| `src/runtime/scheduler.py` | +2 行 | 低 — 新增欄位 |
| `src/gateway/telegram/notifications.py` | ~15 行重寫 | 低 — 向下相容 |
| `src/gateway/api/issues.py` | +3 行 | 低 — 多一次 DB 查詢 |
| `src/gateway/mcp_stdio.py` | 1 行 description | 極低 |
| `agents/*/SOUL.md` | 補充規範文字 | 無風險 |

## 執行步驟

| # | 步驟 | 負責 | 預估 |
|---|------|------|------|
| 1 | 修改 `notifications.py` 統一格式 | coder | 15 min |
| 2 | 修改 `issues.py` emit 補帶 title | coder | 10 min |
| 3 | 修改 `scheduler.py` 補齊欄位 | coder | 10 min |
| 4 | 更新 MCP tool description | coder | 5 min |
| 5 | 更新各 Agent SOUL.md 規範 | admin | 15 min |
| 6 | 手動觸發 update_task 驗證 TG 訊息格式 | qa | 10 min |

## 驗收標準

1. **Task ID 可見**：TG 通知中 `#` 後顯示真實 8 字元 ID（非 `?`）
2. **摘要非空**：📝 行有實質內容（≥ 5 字），或明確顯示「（無摘要）」
3. **格式統一**：所有 TASK_COMPLETED 事件（API / Scheduler 觸發）使用相同格式
4. **向下相容**：舊版 Agent 未帶 output 時不 crash，顯示 fallback 文字
5. **可驗證**：執行 `update_task(task_id="test123", status="completed", output="測試摘要")` 後 TG 收到正確格式通知

## 備註

- `formatters.py:fmt_completed` 是完整版卡片（含耗時、費用），未來可考慮合併到 notification 流程
- 長期建議：建立 `NotificationTemplate` 抽象層，統一管理所有 TG 訊息模板
- 相關追蹤：progress_parser 的 `[DONE] summary=` 標記目前僅供日誌，未回寫到 event data
