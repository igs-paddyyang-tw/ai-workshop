# Memory

## 專案狀態（2026-07-12）

- 單 Agent 架構：gateway(TG Bot) + Gemini Chat + Skills + Wiki + Scheduler
- Builder（ark-agent-builder）可一鍵產出完整專案
- Workshop 教材對齊 ai-bot 架構

## 技術決策

- LLM：kiro-cli（深度模式）+ Gemini Chat（快速秒回）
- DB：SQLite（memory.db + sessions.db）
- Skills：auto_discover 掃描 src/skills/internal/
- Wiki：四層搜尋（L0 精確 + L1 BM25 + L2 語意 + L3 Rerank）
- Scheduler：APScheduler + YAML 定義
- Workflow：YAML 步驟（skill / condition / loop / parallel）

## 踩坑紀錄

- venv 必要（PEP 668）
- Gemini FC schema 需清理（移除 anyOf / title / default）
- matplotlib 中文需設定字型（PingFang TC / Noto Sans CJK）
- kiro-cli chat 延遲 30-120 秒，不適合意圖分類
- edit_message 需 try/except（訊息未變更時會拋錯）
