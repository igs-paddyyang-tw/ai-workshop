---
inclusion: always
---
# BRAIN — ai-dev-agent 記憶與資源使用準則

> 繼承根 BRAIN 所有規則，以下為本角色補充。

## 品質護欄

### 核心規則

1. Prompt 修改必須附 A/B 測試結果
2. LLM 呼叫必須有 timeout + fallback
3. RAG 配置變更記入 daily log

### 禁止事項

1. 禁止未測試就上線 Prompt 修改
2. 禁止 LLM 呼叫無成本追蹤
3. 禁止編造 API 回應格式

## 知識庫路徑

- 私有：`agents/ai-dev-agent/knowledge/wiki/`
- 共用：`knowledge/shared/wiki/`

## 本 Agent 附註

- 踩坑紀錄寫入 memory/daily/
- 完成任務後必須用 reply() 回報
