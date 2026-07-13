---
title: "ai-bot ReAct Agent 技術架構"
type: raw
tags: [architecture, react, agent-loop, tool-calling, hermes]
created: 2026-07-13
source: "Hermes 官方文件 + ai-bot 內部設計"
---

# ai-bot ReAct Agent 技術架構

> 基於 Hermes ReAct Agent 架構分析，對齊 ai-bot 現有系統的設計藍圖。

## 1. Agent Loop（ReAct 迴圈）

```
User message
     ↓
Build system prompt（SOUL + Skills + Memory + Tool schemas）
     ↓
┌──→ Call LLM（streaming）
│         ↓
│    Response 包含 tool_calls?
│         ├─ YES → dispatch 每個 tool → 收集結果 → append 到 messages → ↑ loop back
│         └─ NO  → 純文字回覆 → 結束，存 session
└─────────────────────────────────────────────────────────────────────
```

### 關鍵設計

- **每輪重組 system prompt**：SOUL + 載入的 Skills + Memory + Context files + Tool JSON schemas
- **無限迴圈**直到 LLM 不再呼叫 tool（有 `max_iterations` 保護，預設 90）
- 工具結果以 `{"role": "tool"}` 格式回送 LLM，LLM 可以基於結果再呼叫工具或直接回答
- **Context Compression**：超過 85% token 時自動摘要中間 turns

## 2. Tool 系統

Hermes 的 tool 是自注冊函式：

```python
registry.register(
    name="write_file",
    toolset="filesystem",
    schema={...},          # OpenAI function-calling schema
    handler=handle_write_file,
    check_fn=lambda: True,
)
```

### Tool 載入機制

`model_tools.py` 在 import 時自動掃描 `tools/*.py`，AST 偵測哪些有 `registry.register()` 呼叫。

### Tool Dispatch 流程

```
model response → handle_function_call() → registry.dispatch(name, args) → handler
結果回傳 LLM：{"role": "tool", "tool_call_id": "xxx", "content": "結果字串"}
```

### Agent-level Tools（直接由 agent loop 攔截，不經 registry dispatch）

| Tool | 用途 |
|------|------|
| `memory` | 寫 memory.md / USER.md |
| `todo` | 任務管理 |
| `session_search` | 跨 session 搜尋 |
| `delegate_task` | 子 agent 派工 |

## 3. Skill 系統

**Skill 不是程式碼，是 SKILL.md 文件**（Markdown 指令文件）：

```
skills/
├── research/
│   └── arxiv/
│       ├── SKILL.md          ← 主要指令（agent 讀了就知道怎麼做）
│       └── scripts/          ← 輔助腳本（agent 用 terminal tool 執行）
│           └── search_arxiv.py
```

### Skill 核心哲學

- **Skill = instructions + 現有 tools 組合**，不是新的 Python handler
- 用 `write_file` + `terminal` + `web_extract` 等既有 tool 完成任務
- **Progressive Disclosure**：常用流程放前面，省 token
- **Self-improving**：agent 對話中學到好流程 → `skill_manage(action='create')` → 自動產出新 SKILL.md

## 4. 寫入知識庫的具體機制

Hermes 用 `write_file` tool 直接寫：

```
Model response:
  tool_calls: [{
    name: "write_file",
    arguments: {
      "path": "/project/knowledge/wiki/ocean-king-vs-super-ace.md",
      "content": "# Ocean King vs Super Ace\n\n..."
    }
  }]
     ↓
registry.dispatch("write_file", args)
     ↓
handler 直接 open(path, 'w').write(content)
     ↓
結果回傳 LLM："File written successfully"
```

**沒有額外的 wiki API**——就是 filesystem tool + system prompt 裡告訴 LLM「知識要寫到哪個路徑」。

## 5. ai-bot 對齊 Hermes 的改造路徑

### 現狀

```
User → gemini_chat(prompt) → 純文字 → 回覆
```

`gemini_chat.py` 是 stateless 單次呼叫，沒有 tool calling loop。

### 目標

```
User → agent_loop(prompt, tools=[save_to_wiki, recall, ...])
     ↓
Gemini response 有 function_call?
├─ YES → 執行 tool → 結果回傳 → 再呼叫 Gemini → ...
└─ NO  → 純文字 → 回覆
```

### 最小改動方案

| 檔案 | 改動 |
|------|------|
| `src/llm/gemini_chat.py` | 支持 `tools` 參數 + `function_call` 回應處理（Gemini API 原生支持 `function_declarations`） |
| `src/llm/agent_loop.py`（新增） | ReAct 迴圈（max 5 iterations）：呼叫 Gemini → 偵測 FC → 執行 → 再呼叫 |
| `src/llm/wiki_write.py`（新增） | `save_to_wiki(title, slug, content, tags)` handler |
| `src/bot/handlers.py` | Default 模式改用 `agent_loop()` 取代直接 `gemini_chat()` |

### 流程對比

```
改造前：
  handlers.py → gemini_chat(text, system=prompt) → 純文字

改造後：
  handlers.py → agent_loop(text, system=prompt, tools=[save_to_wiki, recall_memory, ...])
                     ↓
                Gemini API（帶 function_declarations）
                     ↓
                有 function_call → dispatch → 收集結果 → 再呼叫
                     ↓
                無 function_call → 回覆
```

這樣 Gemini 對話中就能主動或被要求時寫入 `knowledge/shared/wiki/`。

## 6. ai-bot 與 Hermes 架構對照表

| 概念 | Hermes | ai-bot 對應 |
|------|--------|------------|
| Agent Loop | `agent_loop.py`（無限迴圈 + max_iter） | `src/llm/agent_loop.py`（待建，max 5） |
| System Prompt | SOUL + Skills + Memory + Tool schemas | SOUL + BRAIN + memory.md + recent + recall + wiki + skills |
| Tool Registry | `registry.register()` + AST 掃描 | `src/skills/registry.py` + function_declarations |
| Skill | SKILL.md（指令文件） | `.kiro/skills/*/SKILL.md`（相同概念） |
| Memory | `MEMORY.md` / `USER.md`（agent-level tool） | `memory/memory.md`（BRAIN 規則約束） |
| Session | turns 累積 + compression | `session.py` history + max_turns |
| Tool: write_file | filesystem tool | `save_to_wiki` handler |
| Tool: terminal | 執行 shell | 未開放（安全考量） |
| Self-improving | `skill_manage(action='create')` | `src/memory/recommend.py`（自動推薦 → 審批） |
| Context Compression | 85% 時摘要 | `prepare_context.py`（recent.md 截斷） |
