---
title: "AI Agent 五層架構設計筆記"
type: system
tags: [architecture, agent, design]
sources: [raw/agent-design-notes.md]
related: [python-async-guide]
created: 2026-07-01
updated: 2026-07-01
status: developing
---

# AI Agent 五層架構設計筆記

## 架構總覽

```
L1 入口層 (Gateway)     — Telegram / Web / CLI
L2 協調層 (Coordinator) — TaskGraph / A2A / LLM Router
L3 服務層 (Services)    — 排程 / 事件 / 通知
L4 執行層 (Runtime)     — Agent Skills / Workflow
L5 知識層 (Knowledge)   — Wiki / Memory / FTS5
```

## 設計原則

1. **關注點分離**：每層只做一件事
2. **向上依賴**：L5 不知道 L1 的存在
3. **事件驅動**：層間用事件通訊，不直接呼叫
4. **可替換**：每層的實作可獨立抽換

## Workshop 對應

| 層 | Workshop |
|----|----------|
| L1 | 01 Agent（Bot 入口）+ 05 管理（Dashboard） |
| L2 | 04 Agent Team（TaskGraph + Discovery） |
| L3 | 04/05（排程 + 通知） |
| L4 | 01 + 02（Skills + Spec-Driven 開發） |
| L5 | 03 LLM Wiki（RAG + 知識圖譜） |

## 相關

- [[python-async-guide]] — L4 執行層的非同步模式
