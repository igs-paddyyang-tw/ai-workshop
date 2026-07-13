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

### 完整架構圖

```
┌─────────────────────────────────────────────────────────────────┐
│                        ai-bot ReAct Agent                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌────────────────────────────────────────┐                     │
│  │ Layer 1: Agent Loop（核心迴圈）          │                     │
│  │                                         │                     │
│  │  src/llm/agent_loop.py                  │                     │
│  │  ┌─→ build_messages(system, history)   │                     │
│  │  │   call_gemini(messages, tools)      │                     │
│  │  │        ↓                             │                     │
│  │  │   has function_call?                │                     │
│  │  │   ├─ YES → tool_dispatch()         │                     │
│  │  │   │        append tool result      │                     │
│  │  │   │        ↑ loop back             │                     │
│  │  │   └─ NO  → return text            │                     │
│  │  └────────────────────────────────────│                     │
│  └────────────────────────────────────────┘                     │
│                         │                                        │
│                         ▼                                        │
│  ┌────────────────────────────────────────┐                     │
│  │ Layer 2: Tool Registry（工具層）         │                     │
│  │                                         │                     │
│  │  Built-in Tools:                        │                     │
│  │  ├── save_to_wiki     寫入知識庫        │                     │
│  │  ├── recall_memory    查詢記憶          │                     │
│  │  ├── search_wiki      搜尋知識庫        │                     │
│  │  ├── save_memory      寫入持久事實      │                     │
│  │  ├── list_skills      列出技能          │                     │
│  │  └── web_search       網路搜尋(未來)    │                     │
│  │                                         │                     │
│  │  Tool Schema → Gemini function_declarations                  │
│  │  Tool Result → {"role": "user", parts: [function_response]}  │
│  └────────────────────────────────────────┘                     │
│                         │                                        │
│                         ▼                                        │
│  ┌────────────────────────────────────────┐                     │
│  │ Layer 3: Context Builder（上下文組裝）    │                     │
│  │                                         │                     │
│  │  system prompt =                        │                     │
│  │    SOUL.md                              │                     │
│  │  + BRAIN.md                             │                     │
│  │  + USER.md                              │                     │
│  │  + memory.md（持久事實）                 │                     │
│  │  + recent.md（最近經驗）                 │                     │
│  │  + Skills descriptions（可觸發清單）     │                     │
│  │  + Tool usage instructions              │                     │
│  │                                         │                     │
│  │  messages[] =                           │                     │
│  │    session history                      │                     │
│  │  + user message                         │                     │
│  │  + [tool results from previous turns]   │                     │
│  └────────────────────────────────────────┘                     │
└─────────────────────────────────────────────────────────────────┘
```

### 完整檔案清單

| # | 檔案 | 類型 | 職責 |
|---|------|------|------|
| 1 | `src/llm/agent_loop.py` | 🆕 | ReAct 核心迴圈（max_iterations + tool dispatch） |
| 2 | `src/llm/tool_registry.py` | 🆕 | Tool 註冊 + dispatch + schema 生成 |
| 3 | `src/llm/tools/__init__.py` | 🆕 | 自動掃描註冊所有 tools |
| 4 | `src/llm/tools/wiki_write.py` | 🆕 | save_to_wiki handler |
| 5 | `src/llm/tools/memory_tools.py` | 🆕 | recall_memory + save_memory handler |
| 6 | `src/llm/tools/wiki_search.py` | 🆕 | search_wiki handler |
| 7 | `src/llm/gemini_chat.py` | 🔄 | 支持 tools 參數 + function_call 處理 |
| 8 | `src/llm/context_builder.py` | 🆕 | 抽出 system prompt 組裝邏輯（統一 Default + Agent） |
| 9 | `src/bot/handlers.py` | 🔄 | Default 模式改用 agent_loop |
| 10 | `src/server/main.py` | 🔄 | API 也走 agent_loop |
| 11 | `src/llm/compression.py` | 🆕 | Context 超限壓縮（Phase D） |

### 各模組介面設計

#### agent_loop.py

```python
@dataclass
class AgentResult:
    text: str                         # 最終回覆文字
    tool_calls_log: list[dict]        # 執行過的 tool 記錄
    iterations: int                   # 迭代次數
    token_usage: dict | None = None   # 累計 token

async def agent_loop(
    user_message: str,
    system_prompt: str,
    session_history: list[dict],
    tools: list[Tool] | None = None,
    max_iterations: int = 5,
    on_tool_call: Callable | None = None,
) -> AgentResult:
    """ReAct 迴圈。"""
```

#### tool_registry.py

```python
@dataclass
class Tool:
    name: str
    description: str
    parameters: dict              # JSON Schema（Gemini function_declarations 格式）
    handler: Callable             # async def handler(args: dict) -> str
    requires_approval: bool = False

    def to_gemini_schema(self) -> dict:
        return {"name": self.name, "description": self.description, "parameters": self.parameters}

class ToolRegistry:
    def register(self, tool: Tool): ...
    def get(self, name: str) -> Tool | None: ...
    def all_schemas(self) -> list[dict]: ...
    async def dispatch(self, name: str, args: dict) -> str: ...
```

#### 內建 Tools

| Tool | 觸發時機 | 行為 | 寫入路徑 |
|------|----------|------|----------|
| `save_to_wiki` | 使用者要求整理/記錄/寫入知識 | 寫入含 frontmatter 的 .md | `knowledge/shared/wiki/{slug}.md` |
| `recall_memory` | 問「之前怎麼做的」 | FTS5 查詢 | 只讀 |
| `search_wiki` | 需要查事實/規格 | WikiEngine.query() | 只讀 |
| `save_memory` | 學到新持久事實 | append 到 memory.md | `memory/memory.md` |
| `list_skills` | 問「你會什麼」 | 讀 skills registry | 只讀 |
| `web_search` | 需要即時資訊（Phase E） | 外部 API | 只讀 |

#### context_builder.py

```python
async def build_system_prompt(
    mode: str = "default",
    agent_id: str | None = None,
    query: str = "",
    session = None,
) -> str:
    """統一 system prompt 組裝。

    mode="default" → 根目錄 SOUL + BRAIN + USER + memory + recent + recall + wiki + skills + tool instructions
    mode="agent"   → agents/{agent_id}/ 的對應檔案（走 kiro-cli，此函式不會被呼叫）
    """
```

### 與現有系統對接

| 現有模組 | 改動 | 說明 |
|----------|------|------|
| `gemini_chat.py` | 🔄 改寫 | 加 `tools` + `tool_config` 參數，回傳結構化 response |
| `handlers.py` L4 | 🔄 | `agent_loop()` 取代 `gemini_chat()` |
| `server/main.py` L4d | 🔄 | 同上 |
| `daily_log.py` | 不動 | agent_loop 結束後照舊呼叫 |
| `recommend.py` | 不動 | tool_calls_log.length 可作為觸發依據 |
| `skill_manage.py` | 不動 | 審批機制不變 |
| `session.py` | 不動 | history 格式相容 |

### 執行分期

| Phase | 內容 | 預估 | 交付物 | 驗收 |
|-------|------|------|--------|------|
| **A** | agent_loop + tool_registry + gemini_chat 改寫 | 3-4h | 核心迴圈可跑 | Gemini 能呼叫 tool + 收結果 + 再回覆 |
| **B** | save_to_wiki + recall_memory + search_wiki + save_memory | 2-3h | 4 個 handler | 對話中說「把這個寫入知識庫」→ wiki 出現新 .md |
| **C** | handlers.py + server/main.py 對接 | 1-2h | 上線生效 | TG + Web UI Default 模式走 agent_loop |
| **D** | compression.py（messages 超限壓縮） | 2h | 長對話穩定 | 超 10 輪對話不爆 context |
| **E** | web_search + create_skill_proposal | 未來 | 擴展能力 | — |

**A+B+C = 一天可完成**，Ark Agent 就能在對話中主動查詢記憶、搜尋知識庫、寫入新知識。

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
