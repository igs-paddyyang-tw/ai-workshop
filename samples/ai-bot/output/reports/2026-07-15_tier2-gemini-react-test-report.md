# Tier 2 測試報告 — Gemini ReAct Agent（gemini-3.5-flash）

> 日期：2026-07-15  
> 模型：gemini-3.5-flash  
> 測試範圍：手動測試清單 #17 ~ #25

---

## 摘要

升級至 `gemini-3.5-flash` 後，ReAct Agent Loop 出現 3 個阻斷性問題，皆已修復。

| # | 問題 | 嚴重度 | 狀態 |
|---|------|--------|------|
| 1 | thought_signature 未保留 → API 400 | 🔴 Critical | ✅ Fixed |
| 2 | agent_loop 耗盡迭代無最終回覆 | 🟡 High | ✅ Fixed |
| 3 | cmd_chat 把 AgentResult 當 str | 🔴 Critical | ✅ Fixed |

---

## 問題 1：thought_signature 未保留

### 現象

```
400 INVALID_ARGUMENT: Function call is missing a thought_signature in functionCall parts.
```

第一次 `search_wiki` tool call 成功執行，但第二輪送回 API 時因缺少 `thought_signature` 被拒絕。

### 根因

Gemini 3.x 系列（thinking 模型）在回傳 `function_call` 時會附帶 `thought_signature`（加密的推理狀態）。原本的程式碼在 `_parse_response` 和 `agent_loop` 組裝 messages 時完全忽略此欄位。

### 修復（3 檔）

| 檔案 | 修改 |
|------|------|
| `src/llm/provider.py` | `FunctionCall` dataclass 新增 `thought_signature: str \| None` |
| `src/llm/providers/gemini.py` → `_parse_response` | 從 response part 抽取 `thought_signature` |
| `src/llm/providers/gemini.py` → `_convert_messages` | 還原 `thought_signature` 到 Part 物件 |
| `src/llm/agent_loop.py` | 組裝 fc_part 時帶入 `thought_signature` |

### 關鍵程式碼

```python
# provider.py
@dataclass
class FunctionCall:
    name: str
    args: dict
    id: str = ""
    thought_signature: str | None = None  # Gemini 3.x 必要

# agent_loop.py — 組裝 message
fc_part = {"function_call": {"name": fc.name, "args": fc.args}}
if fc.thought_signature:
    fc_part["thought_signature"] = fc.thought_signature

# gemini.py — 還原到 Part
part_obj = types.Part.from_function_call(name=fc["name"], args=fc.get("args", {}))
if "thought_signature" in p and p["thought_signature"]:
    part_obj.thought_signature = p["thought_signature"]
```

---

## 問題 2：5 次迭代耗盡無最終回覆

### 現象

```
⚠️ 已執行 5 個工具呼叫，但未能完成最終回覆。請嘗試簡化問題。
```

使用者問「部署流程是什麼」→ LLM 連續 5 次都呼叫 `search_wiki`，從未產出純文字回覆。

### 根因

LLM 拿到 search_wiki 結果後仍認為資訊不足，持續重查。`max_iterations=5` 耗盡後只有 fallback 錯誤訊息，沒有嘗試用已取得的資訊做回答。

### 修復

在 `agent_loop.py` 末尾新增「強制總結」機制：

```python
# Max iterations 耗盡 → 不帶 tools 再呼叫一次，強制純文字回覆
messages.append({"role": "user", "content": "你已經執行了多次工具呼叫，現在必須根據已取得的資訊直接回覆使用者。不要再呼叫任何工具，直接用繁體中文整理回答。"})

final_response = await provider.chat(
    messages=messages,
    system=system_prompt,
    tools=None,  # 不帶 tools → LLM 只能回文字
)
```

---

## 問題 3：AgentResult 當 str 使用

### 現象

```
TypeError: object of type 'AgentResult' has no len()
```

`/chat` 指令觸發後 crash。

### 根因

`cmd_chat` handler 直接把 `agent_loop()` 回傳值當字串使用（`len(reply)`），但 `agent_loop` 回傳的是 `AgentResult` dataclass。

### 修復

```python
# Before
reply = await agent_loop(text, system_prompt=system_prompt)

# After
result = await agent_loop(text, system_prompt=system_prompt)
reply = result.text or ""
```

同時修正了 keyword 參數名稱：`system=` → `system_prompt=`（對齊函式簽名）。

---

## 測試結果

修復後重新驗證：

| # | 測試項目 | 結果 |
|---|---------|------|
| 17 | 自然對話「你好」 | ✅ 2-3s 回覆 |
| 18 | Wiki Tool 觸發 | ✅ search_wiki → 📚 參考 |
| 23 | `/chat` 快問快答 | ✅ 正常回覆 |
| 24 | FC 多輪收斂 | ✅ 強制總結生效 |

---

## 踩坑總結（加入 MEMORY）

| 項目 | 教訓 |
|------|------|
| Gemini 3.x thought_signature | thinking 模型必須原封不動回傳，否則 400 |
| agent_loop 終止策略 | 耗盡迭代時應強制不帶 tools 做最終回覆 |
| AgentResult vs str | 重構 agent_loop 回傳型別後，所有 caller 都要同步更新 |
