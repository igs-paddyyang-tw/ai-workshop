# 長期記憶（根目錄 Kiro Session）

> 只放「下個月還會有用的事實」。上限 2000 tokens。

## 專案狀態（2026-07-28）

- 專案：ai-team-agent — 8 agent 常駐團隊平台
- 架構：gateway / coordinator / runtime / business（四層）
- 入口：Telegram Bot → leader-agent（使用者入口）
- MCP：stdio JSON-RPC bridge（mcp_stdio.py，11 tools）
- 常駐：admin-agent + leader-agent；其餘 6 個動態啟動
- 回覆路徑：Agent MCP reply() → POST /api/chat/reply → Telegram
- port：33333
- Admin Dashboard：`apps/web/`（Next.js 15 + React 18，已修復可用）

## 技術決策

- LLM：kiro-cli `auto` model
- DB：SQLite（dev）/ PostgreSQL（prod）
- 常駐模式：`--legacy-ui --trust-all-tools --require-mcp-startup` + stdin pipe
- cwd：`agents/{name}/`（kiro-cli 從 cwd 載入 .kiro/settings/mcp.json）
- Timeout：300s + 活動偵測寬限 120s
- Admin 前端：方案 A（修復現有 Next.js），保留 board.html 並存

## 今日修改摘要（2026-07-28）

- 根目錄清理：pyproject.toml name 修正、.gitignore 補齊、Docker 路徑修正、刪除空殼 tasks/
- Admin Dashboard 重構（4 Phase 全完成）：
  - 修正硬編碼 + API 路徑對齊後端
  - 新增 Kanban Board 頁面（/admin/board）
  - Queue 加批次操作（指派/取消）
  - Session 加 abort/restart 按鈕 + turns 分離 fetch
  - README 重寫、移除 AGENTS.md/CLAUDE.md
  - next build 通過（13 routes）
- React 19 升級（18 → 19.2.8，零 breaking change）
- WebSocket 修正：直接掛載 @app.websocket 繞過 include_router prefix bug
- Board columns 對齊後端 API（queued/claimed/executing/blocked/completed）
- 首頁路由：`/` redirect 到 `/board`（看板入口）
- board.html 路徑修正：parents[2] → parents[3]
- 產出 One Pager：docs/one-pagers/admin-web-dashboard.md
- 啟動測試通過：8 agents idle、API 全通、WebSocket 連通

## 使用者偏好

- 語言：繁體中文
- 風格：結論先行、精簡
- 不貼 raw stdout / stack trace
