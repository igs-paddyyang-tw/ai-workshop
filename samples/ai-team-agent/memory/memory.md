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

## 今日修改摘要（2026-07-27）✅ 驗證通過

- 修復 leader-agent 不回應：config.py、persistent_daemon wrapped 訊息單行化、SOUL.md reply 優先規則
- 指揮鏈統一：leader 入口，admin 背景角色，全 8 agent TEAM.md 對齊
- MEMORY.md 全 8 agent 重寫，移除 pm-agent / 5人舊快照
- Skills 補齊：ark-wiki-engine / code-spec-validator / doc-coauthoring 全 agent；leader-agent 補 5 個核心 skills
- 駕馭工程優化（4 Phases）：BRAIN Wiki速查表+知識庫注入、SOUL 來源標記+格式規範、TEAM 可派工欄位
- 建立根目錄 memory/ 架構（memory.md / recent.md / daily/）
- 驗證：leader-agent 回覆延遲 7-8 秒，3 個測試案例全過 ✅

## 使用者偏好

- 語言：繁體中文
- 風格：結論先行、精簡
- 不貼 raw stdout / stack trace
