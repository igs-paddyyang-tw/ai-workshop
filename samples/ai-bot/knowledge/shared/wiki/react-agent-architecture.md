---
title: "ai-bot ReAct Agent 技術架構"
type: system
status: mature
tags: [architecture, react-agent, tool-calling, gemini, agent-loop]
sources:
  - raw/react-agent-architecture.md
related: [coding-standards, communication-protocol]
aliases: [ReAct, Agent Loop, Tool Calling]
created: 2026-07-13
updated: 2026-07-13
---

# ai-bot ReAct Agent 技術架構

> 基於 Hermes ReAct Agent 架構，對齊 ai-bot 現有系統的設計藍圖。

## Agent Loop（ReAct 迴圈）

```
User message
     ↓
Build system prompt（SOUL + Skills + Memory + Tool schemas）
     ↓
┌──→ Call LLM（streaming）
│         ↓
│    Response 包含 tool_calls?
│         ├─ YES → dispatch tool → 收集結果 → append messages → loop back
│         └─ NO  → 純文字回覆 → 結束，存 session
└─────────────────────────────────────────────────────────────────────
```

### 關鍵設計

- 每輪重組 system prompt：SOUL + Skills + Memory + Context + Tool schemas
- 無限迴圈直到 LLM 不再呼叫 tool（max_iterations = 5）
- 工具結果以 function_response 格式回送 LLM
- Context Compression：超限時自動摘要中間 turns

## Tool 系統

### 內建 Tools

| Tool | 觸發時機 | 行為 |
|------|----------|------|
| save_to_wiki | 使用者要求寫入知識 | 寫入 wiki/ .md |
| recall_memory | 問「之前怎麼做的」 | FTS5 查詢 memory |
| search_wiki | 查事實/規格 | WikiEngine.query() |
| save_memory | 學到新持久事實 | append memory.md |
| execute_skill | 需要執行 Skill | 載入 SKILL.md → LLM 照做 |

### Tool Dispatch 流程

```
model response → has function_call?
├─ YES → registry.dispatch(name, args) → handler → 結果回傳 LLM → loop
└─ NO  → return text
```

## LLM Provider 抽象層

支援三個 Provider，透過 `.env` 切換：

| Provider | SDK | Function Calling 格式 |
|----------|-----|----------------------|
| Gemini | google-generativeai | function_declarations |
| OpenAI | openai | tools + tool_calls |
| Anthropic | anthropic | tools + tool_use |

切換方式：改 `.env` 的 `LLM_PROVIDER` 然後重啟。

## 檔案結構

```
src/llm/
├── provider.py              # Protocol + LLMResponse + get_default_provider()
├── agent_loop.py            # ReAct 迴圈
├── tool_registry.py         # Tool 註冊 + dispatch
├── context_builder.py       # System prompt 組裝
├── providers/
│   ├── gemini.py
│   ├── openai_provider.py
│   └── anthropic.py
└── tools/
    ├── wiki_write.py
    ├── wiki_search.py
    ├── memory_tools.py
    └── skill_executor.py
```

## 執行狀態

| Phase | 內容 | 狀態 |
|-------|------|------|
| A | agent_loop + tool_registry + gemini_chat 改寫 | ✅ 完成 |
| B | 5 個 tool handler | ✅ 完成 |
| C | handlers.py + server 對接 | ✅ 完成 |
| D | context compression | 🔄 觀察中 |
| E | web_search + delegate（交給 kiro-cli） | ⏸ 延後 |
