---
inclusion: always
---
# Memory — 專案狀態

> 持久化上下文，避免每次重問。定期由使用者更新。

## 專案狀態（2026-07-15）

- 架構：TG Bot gateway + Gemini Chat + Agent CLI 派工
- 語言：Python 3.12 + FastAPI
- 測試：目前無正式測試框架（待建立 pytest 基礎設施）
- CI/CD：尚未設定

## 技術決策

- 程式碼風格：PEP 8 + type hints + async/await
- 錯誤處理：所有外部呼叫必須 try/except
- 日誌：標準 logging 模組（structlog 規劃中）

## 踩坑紀錄

- ConversationTurn 屬性是 content 不是 text（已修）
- edit_message 需 try/except（訊息未變更時會拋錯）
