# Memory

## 專案狀態（2026-07-13）

- 單 Agent 架構：gateway(TG Bot) + Gemini Chat + Skills + Wiki + Scheduler
- Builder（ark-agent-builder）可一鍵產出完整專案
- Workshop 教材對齊 ai-bot 架構
- CLI Backend 抽象化：支援 kiro-cli / agy / claude，透過 .env CLI_BACKEND 切換

## 技術決策

- LLM：Agent CLI（深度模式，預設 agy）+ Gemini Chat（快速秒回）
- CLI Backend：agy（Antigravity CLI）為預設，支援 kiro-cli / claude 切換
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
- agy 不看 cwd，必須用 --add-dir 指定 workspace（不是 --dir）
- agy 用 -p "prompt" 觸發 non-interactive（不是位置參數）
- agy 首次啟動需手動完成 ToS 同意 + OAuth（subprocess 會卡住）
- agy 安裝路徑在 %LOCALAPPDATA%\agy\bin\，不自動加 PATH
