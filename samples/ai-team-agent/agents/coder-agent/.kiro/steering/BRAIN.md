---
inclusion: always
---
# BRAIN — coder-agent 記憶與資源使用準則

> 繼承根 BRAIN 所有規則，以下為本角色補充。

## 品質護欄

### 核心規則

1. 所有 Python 函式必須有完整 type hints
2. 外部呼叫必須 try/except + 適當回退
3. 提交前通過 lint 檢查

### 禁止事項

1. 禁止硬編碼密碼或金鑰
2. 禁止提交含 TODO/FIXME 的程式碼
3. 禁止跳過錯誤處理

## 知識庫路徑

- 私有：`agents/coder-agent/knowledge/wiki/`
- 共用：`knowledge/shared/wiki/`

## 本 Agent 附註

- 踩坑紀錄寫入 memory/daily/
- 完成任務後必須用 reply() 回報
