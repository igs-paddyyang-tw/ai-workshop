# 長期記憶（根目錄 Kiro Session）

> 只放「下個月還會有用的事實」。上限 2000 tokens。

## 專案狀態（2026-07-27）

- 專案：ai-team-agent — 8 agent 常駐團隊平台
- 架構：gateway / coordinator / runtime / business（四層）
- 入口：Telegram Bot → leader-agent（使用者入口）
- MCP：stdio JSON-RPC bridge（mcp_stdio.py，11 tools）
- 常駐：admin-agent + leader-agent；其餘 6 個動態啟動
- 回覆路徑：Agent MCP reply() → POST /api/chat/reply → Telegram
- port：33333

## 技術決策

- LLM：kiro-cli `auto` model
- DB：SQLite（dev）/ PostgreSQL（prod）
- 常駐模式：`--legacy-ui --trust-all-tools --require-mcp-startup` + stdin pipe
- cwd：`agents/{name}/`（kiro-cli 從 cwd 載入 .kiro/settings/mcp.json）
- Timeout：300s + 活動偵測寬限 120s

## 今日修改摘要（2026-07-27）✅ 全部完成

- 修復 leader-agent 不回應：config.py、persistent_daemon wrapped 訊息、SOUL.md reply 優先規則
- 指揮鏈統一：leader 入口，admin 背景角色，全 8 agent TEAM.md 對齊
- MEMORY.md 全 8 agent 重寫，Skills 補齊（共用 + leader 核心）
- 駕馭工程優化（4 Phases）：BRAIN/SOUL/TEAM 全面強化
- 建立根目錄 memory/ 架構
- 任務系統統一：MCP tools 改寫 tasks 表，看板正確，/api/issues Deprecated
- SharedMemory base 改為 data/：runtime 資料不再污染 knowledge/
- knowledge/ 整理：三層合一，knowledge/shared/ 為唯一來源（raw 20 + wiki 26 個檔案）

## 使用者偏好

- 語言：繁體中文
- 風格：結論先行、精簡
- 不貼 raw stdout / stack trace
