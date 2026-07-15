---
inclusion: always
---
# Memory — 專案狀態

> 持久化上下文，避免每次重問。定期由使用者更新。

## 專案狀態（2026-07-15）

- 架構：TG Bot gateway + Gemini Chat + Agent CLI 派工
- 外部搜尋：Web Search tool（透過 Gemini Function Calling）
- 知識庫：knowledge/shared/wiki/（共用）+ agents/market-agent/knowledge/wiki/（私有）

## 技術決策

- 資訊來源分級：A（官方）> B（專業部落格）> C（社群）
- 輸出位置：output/reports/（一次性）或 knowledge/wiki/（持久化知識）

## 踩坑紀錄

- Web Search 結果需交叉驗證，單一來源不可標為「確認」
