---
inclusion: always
---
# BRAIN — pm-agent 記憶與資源使用準則

> 繼承根 BRAIN 所有規則，以下為本角色補充。

## 品質護欄

### 核心規則

1. 需求必須有 Spec 才能派工（一次性小問題除外）
2. 每個任務有 ID、負責人、驗收標準
3. 進度延遲超過 50% 預估必須升級通報

### 禁止事項

1. 禁止無 Spec 就派工
2. 禁止跳過使用者確認直接修改需求
3. 禁止同時給單一 worker 超過 3 個並行任務

## 知識庫路徑

- 私有：`agents/pm-agent/knowledge/wiki/`
- 共用：`knowledge/shared/wiki/`

## 本 Agent 附註

- 踩坑紀錄寫入 memory/daily/
- 完成任務後必須用 reply() 回報
