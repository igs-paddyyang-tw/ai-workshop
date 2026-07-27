---
title: "測試標準與品質指標"
type: concept
tags: [testing, quality, standards, qa]
sources: [agents/qa-agent/knowledge/raw/testing-standards.md]
related: [coding-standards]
created: 2026-07-02
updated: 2026-07-14
status: developing
---
# 測試標準與品質指標

## 覆蓋率目標

- 單元測試覆蓋率：> 80%
- E2E 測試：關鍵路徑 100% 覆蓋

## 命名規則

```
test_{功能}_{場景}_{預期結果}
```

## PR 規則

- 每個 PR 必須有對應測試
- 無測試的 PR 不得合併

## 安全掃描

- 頻率：每週一次
- 工具：security_audit Skill
