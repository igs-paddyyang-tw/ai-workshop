# Memory

## 專案狀態（2026-07-15）

- 架構：TG Bot gateway + Gemini Chat（ReAct + Tool Calling）+ Agent CLI 派工
- CLI Backend：agy（Antigravity CLI），透過 .env CLI_BACKEND / CLI_MODEL 控制
- LLM：Gemini 3.5 Flash（快速對話）+ Claude Sonnet 4.6（Agent CLI 深度模式 via agy）
- DB：SQLite（memory.db + sessions.db）
- 團隊：8 agents（admin/pm/ai-dev/coder/qa/data/market/report）
- Steering：每 agent 4 檔（SOUL/BRAIN/MEMORY/TEAM），已合併 USER→SOUL、GUARDRAILS→BRAIN

## 技術決策

- CLI Backend：agy 為預設，支援 kiro-cli / claude 切換
- CLI_MODEL：agy 用 claude-sonnet-4-6，kiro 用 auto
- Skills：auto_discover 掃描 src/skills/internal/
- Wiki：四層搜尋（L0 精確 + L1 BM25 + L2 語意 + L3 Rerank）
- SOUL inject：kiro-cli 自動讀 cwd/.kiro/；agy/claude 由 _inject_context() 注入 SOUL + MEMORY
- 派工：Ark Agent 透過 dispatch_to_agent tool 自動路由

## 踩坑紀錄

- venv 必要（PEP 668）
- Gemini FC schema 需清理（移除 anyOf / title / default）
- matplotlib 中文需設定字型（PingFang TC / Noto Sans CJK）
- kiro-cli chat 延遲 30-120 秒，不適合意圖分類
- edit_message 需 try/except（訊息未變更時會拋錯）
- agy 不看 cwd，必須用 --add-dir 指定 workspace
- agy 首次啟動需手動完成 ToS + OAuth（subprocess 會卡住）
- agy 安裝路徑在 %LOCALAPPDATA%\agy\bin\，不自動加 PATH
- ConversationTurn 屬性是 content 不是 text（已修）
- _inject_soul + _inject_context 重複注入問題：用標記檢測避免
