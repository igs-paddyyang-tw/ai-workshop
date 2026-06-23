---
title: "AI Agent 系統設計筆記"
type: system
tags: [agent, architecture, llm, design]
created: 2026-06-23
updated: 2026-06-23
status: developing
---

# AI Agent 系統設計筆記

## 四層架構

現代 AI Agent 平台採用四層設計：

```
入口層（Entry）      → Telegram / Web / API
協調層（Orchestration）→ 任務分派、依賴解析
執行層（Execution）   → Agent + Skills + LLM
知識層（Knowledge）   → Wiki + Memory + RAG
```

## 意圖路由模式

所有 Agent 的核心都是 **意圖路由**：

1. 接收使用者訊息
2. 分類意圖（關鍵字 + LLM）
3. 路由到對應 Skill 或 LLM 對話

這與 ChatGPT、Claude 內部架構的簡化版本一致。

## RAG（檢索增強生成）

RAG 解決 LLM 的「幻覺」問題：

```
使用者問題 → 搜尋知識庫 → 取得相關片段 → 注入 LLM context → 產出有依據的回答
```

關鍵元件：
- **Indexer**：將文件切片、建立索引
- **Retriever**：BM25 / 向量搜尋 / Hybrid
- **Generator**：LLM 根據 context 回答

## 多 Agent 協作

多 Agent 系統需要解決：
- **任務分解**：大任務拆成子任務
- **角色分配**：根據 Agent 能力自動匹配
- **結果整合**：子任務完成後合併產出

## 技術選型

| 元件 | 選擇 | 理由 |
|------|------|------|
| 搜尋 | SQLite FTS5 | 零依賴、嵌入式 |
| LLM | Gemini 2.5 Flash | 快速、便宜 |
| 框架 | FastAPI | [[python-async-guide]] 原生支援 |
| 部署 | Docker | 一致性 |

## 相關主題

- [[python-async-guide]] — Agent 系統大量使用非同步
- [[common-errors]] — 開發時常見問題
