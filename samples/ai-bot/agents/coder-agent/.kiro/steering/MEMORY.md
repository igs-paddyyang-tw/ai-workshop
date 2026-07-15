---
inclusion: always
---
# Memory — 專案狀態

> 持久化上下文，避免每次重問。定期由使用者更新。

## 專案狀態（2026-07-15）

- 架構：TG Bot gateway + Gemini Chat（ReAct + Tool Calling）+ Agent CLI 派工
- 語言：Python 3.12 + FastAPI + python-telegram-bot
- DB：SQLite（memory.db + sessions.db）
- 非同步：全 async/await（asyncio + aiohttp）

## 技術決策

- LLM Provider：google-genai SDK（Gemini），統一透過 src/llm/provider.py
- Tool Calling：Gemini Function Calling（自動 schema 清理）
- 記憶系統：FTS5 全文搜尋 + daily log + memory.md 蒸餾
- Wiki：四層搜尋（L0 精確 + L1 BM25 + L2 語意 + L3 Rerank）

## 踩坑紀錄

- venv 必要（PEP 668）
- matplotlib 中文需設定字型（PingFang TC / Noto Sans CJK）
- ConversationTurn 屬性是 content 不是 text
- Gemini FC schema 需清理（移除 anyOf / title / default）
