---
title: "AI Agent 專家開發平台 — 執行計劃"
type: spec
status: approved
created: 2026-07-07
---

# 願景

一個人就能打造各種 AI Agent 專家，管理自己的知識庫，帶走直接用。

# 核心價值

1. **建 Agent** — 填 SOUL + 綁知識 + 預覽對話 → 5 分鐘建一個專家
2. **管知識** — 丟文件 / AI 搜尋 → ingest → Agent 馬上能引用
3. **用 Agent** — TG + Web Chat 兩端都能用
4. **帶走** — clone repo 就是完整平台，改 SOUL 改知識直接用在業務

# 平台架構（5 頁）

```
http://localhost:8000
├── /          💬 Chat        — 跟 Agent 對話
├── /admin     ⚙️ Dashboard   — 看狀態 + Ingest/Lint
├── /wiki      📖 Wiki        — 瀏覽 + 搜尋 + 看內容
├── /builder   🏗️ Builder     — 建 Agent + SOUL + 知識綁定 + 預覽
└── /api-docs  📡 API         — 開發者用
```

# 完成狀態

## ✅ 已完成

| 功能 | 頁面 | 說明 |
|------|------|------|
| Agent 對話 | Chat | 8 Agent 切換 + Wiki RAG + Gemini |
| Dashboard | Dashboard | 5 KPI + Agent 列表 + Ingest/Lint + 系統資訊 |
| Wiki 瀏覽器 | Wiki | 檔案列表 + 搜尋 + Markdown 內容顯示 |
| Agent Builder | Builder | SOUL 編輯 + 知識綁定 + 預覽對話 |
| API 文件 | API Docs | 暗黑風格 + Try 按鈕 |
| TG Bot | — | Planner L1-L4 + Reaction + 標頭 + typing |
| 知識庫 | — | 兩層（全域+私有）+ 中文 bigram + RAG |
| Agent 服務 | — | AgentProcess 常駐 8 Agent（kiro/gemini/claude） |
| Memory | — | 自動記錄 + 搜尋注入 Gemini context |
| Kiro Skills | — | 5 個內建（grill-me/superpowers/skill-creator/validator/wiki-engine） |

## 🔲 可選優化（不影響使用）

| 功能 | 說明 | 何時做 |
|------|------|--------|
| SOUL 模板庫 | 預設 10+ 產業模板（客服/分析/設計...） | 需要時 |
| Agent 匯出 | 把建好的 Agent 打包成 .zip | 需要時 |
| Wiki lint 自動修復 | 點一下自動補 frontmatter | 需要時 |
| Docker 部署 | docker-compose.prod.yml | 要上線時 |
| 排程 ingest | 每天自動 ingest raw/ → wiki/ | 課程 B |
| 多 Agent 協作 | pm-agent 派工 + TaskGraph | 課程 B |

# 技術架構

```
┌─────────────────────────────────────────────────┐
│                   Web UI（5 頁）                  │
│  Chat | Dashboard | Wiki | Builder | API Docs   │
├─────────────────────────────────────────────────┤
│              FastAPI + Templates                  │
│  /api/v1/chat | /wiki/query | /wiki/ingest      │
├─────────────────────────────────────────────────┤
│         Bot Runtime（handlers.py）                │
│  Planner L1-L4 | WikiEngine | Memory | Gemini   │
├──────────┬──────────┬───────────────────────────┤
│ AgentProcess │ WikiEngine  │ Gemini/CLI fallback │
│ 8 Agent 常駐 │ 兩層 RAG    │ SOUL + context      │
├──────────┴──────────┴───────────────────────────┤
│              knowledge/                          │
│  raw/ → ingest → wiki/（全域）                   │
│  agents/*/knowledge/（私有 memory）              │
├─────────────────────────────────────────────────┤
│           .kiro/skills/（5 個 IDE Skill）         │
│  grill-me | superpowers | skill-creator          │
│  code-spec-validator | wiki-engine               │
└─────────────────────────────────────────────────┘
```

# 使用流程

## 建一個新 Agent 專家

```
1. 開 /builder
2. 填 SOUL（身份/語氣/格式/邊界）
3. 勾選要綁定的知識庫頁面
4. 預覽對話 → 確認行為正確
5. 存檔 → TG + Web 馬上能用
```

## 加入新知識

```
1. 📝 Kiro「搜尋 XXX，整理成 knowledge/raw/ 格式」
2. 📝 Kiro「匯入到 Wiki」（或開 /admin 點 Ingest 按鈕）
3. 📱 TG 問 → 有 📚 引用 = 知識生效
```

## 日常使用

```
📱 TG 問問題 → Agent 用你的知識回答
🌐 Web Chat 問 → 同樣效果
⚙️ Dashboard 看狀態 → Lint 確認健康
📖 Wiki 瀏覽 → 看知識庫有什麼
```

# 設計原則

| 原則 | 做法 |
|------|------|
| 個人使用 | 不需要登入、不需要權限管理 |
| 帶走能用 | clone + .env + python start.py 就跑 |
| 改 SOUL 改行為 | 不用改程式碼 |
| 改知識改回答 | 丟文件 + ingest 就生效 |
| 5 分鐘建一個 Agent | Builder 表單 + 預覽 |
