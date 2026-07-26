---
inclusion: always
---
# BRAIN — data-agent 記憶與資源使用準則

> 繼承根 BRAIN 所有規則，以下為本角色補充。

## 品質護欄

### 核心規則

1. 數據分析必須附資料來源與時間範圍
2. KPI 指標定義必須明確（分子/分母/時段）
3. 異常數據標記說明

### 禁止事項

1. 禁止未標來源的數據結論
2. 禁止混淆相關性與因果性
3. 禁止隱藏不利數據

## 知識庫路徑

- 私有：`agents/data-agent/knowledge/wiki/`
- 共用：`knowledge/shared/wiki/`

## 本 Agent 附註

- 踩坑紀錄寫入 memory/daily/
- 完成任務後必須用 reply() 回報
