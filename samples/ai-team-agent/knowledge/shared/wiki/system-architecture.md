---
title: "AI Bot 系統設計架構"
type: system
status: mature
tags: [architecture, fastapi, telegram, agent-process, wiki-engine]
sources:
  - docs/archive/system-architecture.md
related: [react-agent-architecture, team-roles, communication-protocol, coding-standards]
aliases: [系統架構, ai-bot architecture, 平台架構]
created: 2026-07-07
updated: 2026-07-13
---

# AI Bot 系統設計架構

## 一句話定位

個人 AI Agent 專家開發平台 — 打造各種 Agent 專家 + 管理知識庫。

## 系統架構圖

```
┌───────────────────────────────────────────────────────────┐
│                    使用者介面                               │
│  Chat | Dashboard | Wiki | Graph | Builder | API Docs     │
├───────────────────────────────────────────────────────────┤
│              FastAPI (port 8000)                            │
│  /api/v1/chat | /api/v1/wiki/* | /api/v1/graph | /health  │
├───────────────────────────────────────────────────────────┤
│              Telegram Bot（獨立子進程）                      │
│  handlers.py → Planner L1-L4 → 回覆 + Reaction            │
├───────────────────────────────────────────────────────────┤
│                    核心服務層                               │
│  AgentProcess(8) | WikiEngine | Memory | Gemini Chat      │
├───────────────────────────────────────────────────────────┤
│                    資料層                                   │
│  knowledge/(全域) | agents/(私有) | .kiro/skills/          │
└───────────────────────────────────────────────────────────┘
```

## 啟動架構

```
python start.py
├── 主進程：uvicorn（FastAPI，port 8000）
│   └── Web UI 6 頁 + API endpoints
└── 子進程：python -m src.bot.run
    ├── TG Bot polling
    ├── AgentProcess × 8
    └── 獨立 event loop
```

## 對話路由（Planner L1-L4）

| 層級 | 觸發 | 行為 |
|------|------|------|
| L1 | /reset | 清空 session |
| L2 | /skill_id args | 直接執行 Skill |
| L3 | keyword 匹配 | Planner 路由表 |
| L4a | CLI 可用 | AgentProcess.send() |
| L4b | Wiki 查詢 | WikiEngine.query() |
| L4c | 記憶搜尋 | memory 注入 context |
| L4d | Gemini | SOUL + context 回覆 |

## Tier 分級

| Tier | 條件 | 能力 |
|------|------|------|
| 0 | 零設定 | Skills + Wiki + API + Web UI |
| 1 | + TG Token | Bot + 8 Agent |
| 2 | + Gemini Key | AI 對話 + RAG |
| 3 | + kiro-cli | 8 Agent 常駐（完整 .kiro/） |

## Web UI（6 頁）

| 頁面 | URL | 功能 |
|------|-----|------|
| Chat | / | 8 Agent 切換 + 對話 |
| Dashboard | /admin | KPI + Ingest/Lint |
| Wiki | /wiki | 樹狀側欄 + 搜尋 + 渲染 |
| Graph | /graph | 三層力導向圖譜 |
| Builder | /builder | SOUL 編輯 + 知識綁定 |
| API Docs | /api-docs | 暗黑風 + Try 按鈕 |

## 8 個 Agent

詳見 [[team-roles]]

## 知識庫查詢

詳見 [[react-agent-architecture]]、WikiEngine 兩層 RAG（私有→全域→合併）
