---
inclusion: always
---
# Memory — 專案狀態

> 持久化上下文，避免每次重問。定期由使用者更新。

## 專案狀態（2026-07-15）

- 架構：TG Bot gateway + Gemini Chat（ReAct + Tool Calling）+ Agent CLI 派工
- CLI Backend：agy（Antigravity CLI），透過 .env CLI_BACKEND / CLI_MODEL 切換
- LLM：Gemini 3.5 Flash（快速對話）+ Claude Sonnet 4.6（Agent CLI 深度模式）
- DB：SQLite（memory.db + sessions.db）
- 團隊：8 agents（admin/pm/ai-dev/coder/qa/data/market/report）

## 技術決策

- Agent CLI 統一由 AgentProcess 管理，每次 send() spawn 一個進程
- SOUL 注入：kiro-cli 自動讀 cwd/.kiro/；agy/claude 需手動 prepend
- 派工：Ark Agent（default）透過 dispatch_to_agent tool 自動路由

## 踩坑紀錄

- agy 不看 cwd，必須用 --add-dir 指定 workspace
- agy 首次啟動需手動完成 ToS + OAuth
- kiro-cli chat 延遲 30-120 秒，不適合意圖分類
- Gemini FC schema 需清理（移除 anyOf / title / default）
- edit_message 需 try/except（訊息未變更時會拋錯）
