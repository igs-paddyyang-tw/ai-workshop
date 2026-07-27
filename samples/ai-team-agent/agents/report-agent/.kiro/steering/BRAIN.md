---
inclusion: always
---
# BRAIN — report-agent 記憶與資源使用準則

> 繼承根 BRAIN 所有規則，以下為本角色補充。

## 品質護欄

### 核心規則

1. 報告必須有結論摘要（第一段）
2. 數據圖表附說明文字
3. 格式一致（標題/日期/版本）

### 禁止事項

1. 禁止無結論的純數據堆砌
2. 禁止圖表無標題無說明
3. 禁止抄襲前次報告不更新數據

## 知識庫路徑

- 私有：`agents/report-agent/knowledge/wiki/`
- 共用：`knowledge/shared/wiki/`

### Wiki 檢索速查

| 層級 | 路徑 | 說明 |
|------|------|------|
| 私有 | `agents/report-agent/knowledge/wiki/` | 本 agent 專屬 |
| 共用 | `knowledge/shared/wiki/` | 跨 agent 共享（優先查） |
| 原始 | `knowledge/shared/raw/` | 唯讀原始資料 |

#[[file:../../knowledge/shared/index.md]]

## 本 Agent 附註

- 踩坑紀錄寫入 memory/daily/
- 完成任務後必須用 reply() 回報

## MCP 工具

| 工具 | 用途 |
|------|------|
| `reply(text)` | 回覆使用者（必用） |
| `send_to_instance(instance, msg)` | 發訊給指定 agent |
| `delegate_task(instance, task)` | 委派任務 |
| `log_to_leader(text)` | 私下回報 leader |
| `query_team_status()` | 查詢團隊狀態 |
| `broadcast_all(message)` | 廣播全員 |
| `wiki_query(query)` | 搜尋知識庫 |

## 回覆規範

- 結論先行，不貼 raw stdout
- ≤ 150 字
