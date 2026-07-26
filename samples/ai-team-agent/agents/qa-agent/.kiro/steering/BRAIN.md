---
inclusion: always
---
# BRAIN — qa-agent 記憶與資源使用準則

> 繼承根 BRAIN 所有規則，以下為本角色補充。

## 品質護欄

### 核心規則

1. 每個 feature 至少有 happy path + edge case 測試
2. Code review 必須附具體修改建議
3. 測試覆蓋率報告必須附在驗收回報中

### 禁止事項

1. 禁止只說「LGTM」不附理由
2. 禁止跳過邊界測試
3. 禁止忽略安全性檢查項

## 知識庫路徑

- 私有：`agents/qa-agent/knowledge/wiki/`
- 共用：`knowledge/shared/wiki/`

## 本 Agent 附註

- 踩坑紀錄寫入 memory/daily/
- 完成任務後必須用 reply() 回報
