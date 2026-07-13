---
title: "ai-bot ReAct Agent 設計文件"
type: design
version: "1.0"
status: proposed
language: zh-TW
author: "paddy"
created: 2026-07-13
updated: 2026-07-13
deciders: ["paddy"]
related_spec: "docs/specs/react-agent-spec.md"
---

# ai-bot ReAct Agent — 設計文件

## 1. 概述（Overview）

為 Ark Agent 加入 ReAct（Reasoning + Acting）迴圈，讓 Gemini 對話能呼叫 Tools 執行動作。
三層架構：Agent Loop → Tool Registry → Context Builder。
LLM Provider 抽象化，支援 Gemini / OpenAI / Anthropic 切換。

## 2. 背景（Context）

- **相關 Spec**：`docs/specs/react-agent-spec.md`
- **參考設計**：`knowledge/shared/raw/react-agent-architecture.md`（Hermes 架構分析）
- **現狀**：gemini_chat.py 是 stateless 單次呼叫，無 tool calling
- **前置**：雙模式對話架構已完成（Default Gemini + Agent CLI）

## 3. 架構決策（Architecture Decisions）

### ADR-001: Agent Loop 迭代上限

**狀態**：accepted

**背景**：ReAct 迴圈可能無限跑，需要保護。

| 選項 | 優點 | 缺點 |
|------|------|------|
| A: max=5 | 安全、快速回覆、省 token | 複雜任務可能做不完 |
| B: max=20 | 複雜任務能完成 | 慢、貴、可能卡住 |
| C: max=90（Hermes） | 完全對齊 Hermes | 對 TG Bot 太慢 |

**決策**：選 A — max_iterations=5。TG 回覆需要快（< 30s），5 輪 tool call 已能完成大部分任務。

---

### ADR-002: LLM Provider 抽象方式

**狀態**：accepted

**背景**：需支持 3 家 LLM API，格式各不同。

| 選項 | 優點 | 缺點 |
|------|------|------|
| A: if/else 在 gemini_chat 裡切換 | 最快實作 | 醜、難維護 |
| B: **Protocol + 獨立 Provider 類** | 乾淨、可擴展、單一職責 | 稍多檔案 |
| C: 用 LiteLLM 統一 SDK | 不用自己寫 | 新依賴、黑箱、FC 格式差異仍需處理 |

**決策**：選 B — Protocol 介面 + 獨立 Provider。保持零外部框架依賴，完全掌控 function calling 轉換。

---

### ADR-003: Tool 寫入權限控制

**狀態**：accepted

**背景**：Agent 有寫入能力後需要限制路徑。

| 選項 | 優點 | 缺點 |
|------|------|------|
| A: 白名單路徑（硬編碼） | 簡單、安全 | 加新路徑要改程式 |
| B: **白名單 + 配置檔** | 可配置、安全 | 稍複雜 |
| C: 無限制 | 靈活 | 危險 |

**決策**：選 B — 白名單硬編碼 + BRAIN.md 紅線。初期寫死 `knowledge/shared/wiki/` + `memory/`，未來可擴展。

## 4. 系統架構（System Architecture）

### 4.1 高層架構圖

```
┌─────────────────────────────────────────────────────────────┐
│                    Ark Agent（Default 模式）                   │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  handlers.py / server/main.py                                │
│       │                                                      │
│       ▼                                                      │
│  ┌──────────────────────────────────────────────┐           │
│  │  context_builder.py                           │           │
│  │  組裝 system prompt                           │           │
│  │  (SOUL+BRAIN+USER+memory+recent+skills+tools) │           │
│  └──────────────────────┬───────────────────────┘           │
│                          │                                   │
│                          ▼                                   │
│  ┌──────────────────────────────────────────────┐           │
│  │  agent_loop.py                                │           │
│  │                                               │           │
│  │  for i in range(max_iterations):             │           │
│  │    response = provider.chat(messages, tools)  │           │
│  │    if response.function_calls:                │           │
│  │      for fc in function_calls:               │           │
│  │        result = registry.dispatch(fc)        │           │
│  │        messages.append(tool_result)          │           │
│  │    else:                                      │           │
│  │      return response.text                    │           │
│  └──────────────┬──────────────┬────────────────┘           │
│                  │              │                             │
│         ┌────────▼───┐  ┌──────▼──────────┐                 │
│         │ provider.py │  │ tool_registry.py │                 │
│         └──────┬─────┘  └──────┬──────────┘                 │
│                │               │                             │
│     ┌──────────┼─────┐  ┌─────┼──────────────────┐         │
│     ▼          ▼     ▼  ▼     ▼          ▼       ▼         │
│  Gemini    OpenAI  Anth  save  recall  search  execute      │
│  Provider  Prov.   Prov. wiki  memory  wiki    skill        │
└─────────────────────────────────────────────────────────────┘
```

### 4.2 數據流

```
使用者訊息
     ↓
context_builder → system_prompt
     ↓
agent_loop:
  messages = [system] + history + [user_msg]
  tools = registry.all_schemas()
     ↓
  ┌─→ provider.chat(messages, tools)
  │        ↓
  │   LLMResponse:
  │   ├─ function_calls 不為空
  │   │    ↓
  │   │   registry.dispatch(name, args) → handler 執行
  │   │    ↓
  │   │   messages.append({function_call})
  │   │   messages.append({function_response: result})
  │   │    ↓ loop back
  │   │
  │   └─ function_calls 為空（純文字）
  │        ↓
  │        return AgentResult(text, log, iterations)
  └─────────────────────────────────────────────────
     ↓
handlers.py:
  session.add_turn("agent", result.text)
  daily_log(conversation)
  recommend(tool_calls_count)
  reply to user
```

### 4.3 Provider 轉換層

```
統一介面：
  provider.chat(messages, system, tools) → LLMResponse

Gemini 轉換：
  messages → Content[] (parts: [{text}, {function_call}, {function_response}])
  tools → [{"function_declarations": [...]}]
  response.candidates[0].content.parts → 解析 function_call / text

OpenAI 轉換：
  messages → [{"role": "system/user/assistant/tool", "content": ...}]
  tools → [{"type": "function", "function": {...}}]
  response.choices[0].message.tool_calls → 解析

Anthropic 轉換：
  messages → [{"role": "user/assistant", "content": [...]}]
  system → 獨立 system 參數
  tools → [{"name", "description", "input_schema"}]
  response.content → 解析 tool_use block
```

## 5. 故障隔離與降級策略（Failure Isolation）

| 故障場景 | 影響 | 降級行為 |
|----------|------|----------|
| LLM API 不可用 | agent_loop 無法執行 | 回覆「API 暫時不可用」，不 crash |
| Tool handler 拋錯 | 單個 tool 失敗 | 回傳 error string 給 LLM，LLM 自行處理或換工具 |
| max_iterations 耗盡 | 任務未完成 | 回傳已完成的部分 + 「任務太複雜，建議拆分」 |
| Provider key 無效 | 初始化失敗 | start.py 啟動時檢查，告警 + 退化為無 tool 純文字 |
| save_to_wiki 寫入失敗 | 知識未存 | 回傳 error → LLM 告知使用者重試 |

## 6. 安全性考量（Security）

| 層級 | 措施 |
|------|------|
| Tool 白名單 | save_to_wiki 只能寫 `knowledge/shared/wiki/`；save_memory 只能寫 `memory/memory.md` |
| 路徑驗證 | handler 內 resolve path 後檢查是否在白名單內，防止 `../` 逃逸 |
| BRAIN.md 紅線 | prompt 層告知 LLM 不可寫 .kiro/、不可寫 secrets |
| 輸入清理 | tool args 驗證 JSON schema，非法參數回傳 error |
| Token 保護 | max_iterations=5 + total token 上限防止 API 費用失控 |

## 7. 技術棧選擇

| 用途 | 技術 | 理由 |
|------|------|------|
| LLM: Gemini | `google-generativeai` SDK | 已安裝，Function Calling 原生支持 |
| LLM: OpenAI | `openai` SDK | 業界標準，FC 格式最成熟 |
| LLM: Anthropic | `anthropic` SDK | 直接呼叫 Claude API（不走 kiro-cli） |
| Tool dispatch | 自建 ToolRegistry | 簡單、無依賴、完全掌控 |
| JSON Schema | 手寫 | tool 數量少（5-6 個），不需 code gen |

## 8. 模組設計

### 新增檔案

```
src/llm/
├── provider.py              ← Protocol + LLMResponse + get_default_provider()
├── agent_loop.py            ← ReAct 迴圈
├── tool_registry.py         ← Tool 註冊 + dispatch
├── context_builder.py       ← System prompt 組裝
├── compression.py           ← Context 壓縮（Phase D）
├── providers/
│   ├── __init__.py
│   ├── gemini.py
│   ├── openai_provider.py
│   └── anthropic.py
├── tools/
│   ├── __init__.py
│   ├── wiki_write.py
│   ├── wiki_search.py
│   ├── memory_tools.py
│   └── skill_executor.py
└── gemini_chat.py           ← backward compat wrapper
```

### 修改檔案

| 檔案 | 改動 |
|------|------|
| `src/bot/handlers.py` | L4 Default 模式改用 `agent_loop()` |
| `src/server/main.py` | API L4d 改用 `agent_loop()` |
| `.env.example` | 加 `LLM_PROVIDER`, `LLM_MODEL`, `OPENAI_API_KEY`, `ANTHROPIC_API_KEY` |

---

## 品質檢查

- [x] 至少列出 2 個替代方案（3 個 ADR 各 3 選項）
- [x] 決策理由明確
- [x] 有故障降級策略
- [x] 安全性已考量
- [x] 數據流清晰
