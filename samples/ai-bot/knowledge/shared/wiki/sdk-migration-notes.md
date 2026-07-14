---
title: "SDK 遷移備忘（google-genai + agy CLI）"
type: wiki
tags: ['migration', 'sdk', 'google-genai', 'agy', 'cli']
created: 2026-07-13
updated: 2026-07-13
---

# SDK 遷移備忘

## 1. Python SDK：google-generativeai → google-genai

| | 舊版 | 新版 |
|---|---|---|
| 套件名 | `google-generativeai` | `google-genai>=1.0.0` |
| import | `import google.generativeai as genai` | `from google import genai` |
| 設定 | `genai.configure(api_key=...)` | `client = genai.Client(api_key=...)` |
| 狀態 | 維護模式 | **Active**（Google 推薦） |

### 現況

- `requirements.txt` 已用 `google-genai>=1.0.0` ✅
- `src/llm/providers/gemini.py` 仍用舊版 `google.generativeai` import ⚠️
- **TODO**：遷移 GeminiProvider 到新版 `google.genai` API

### 遷移方式（未來）

```python
# 舊版
import google.generativeai as genai
genai.configure(api_key=key)
model = genai.GenerativeModel("gemini-2.5-flash")
response = await model.generate_content_async(contents)

# 新版
from google import genai
client = genai.Client(api_key=key)
response = await client.aio.models.generate_content(
    model="gemini-2.5-flash",
    contents=contents,
)
```

## 2. CLI：Gemini CLI → Antigravity CLI（agy）

| | 舊版 | 新版 |
|---|---|---|
| 指令 | `gemini` | `agy` |
| 全名 | Gemini CLI | Antigravity CLI |
| 狀態 | 將被取代 | **Active**（Google 推薦） |

### 現況

- `process.py` BACKENDS 已有 `"agy"` 定義 ✅
- `cli.py` 自動偵測優先順序：`kiro > agy > claude` ✅
- `.env` 預設 `CLI_BACKEND=kiro`（你目前主力用 kiro-cli） ✅

### agy CLI 用法

```bash
agy -p "你的問題" --dangerously-skip-permissions --add-dir <workspace>
```

## 3. 命名分層（避免混淆）

| 層 | 名稱 | 指的是 |
|----|------|--------|
| LLM Provider（API 呼叫） | `gemini` | 用 `google-genai` SDK 呼叫 Gemini API |
| CLI Backend（spawn 進程） | `agy` | 用 `agy` 指令啟動 Antigravity CLI |
| CLI Backend | `kiro` | 用 `kiro-cli` 指令啟動 Kiro CLI |
| CLI Backend | `claude` | 用 `claude` 指令啟動 Claude Code CLI |

**Provider ≠ CLI Backend**：
- Provider 是 ai-bot 自己呼叫 API（Default 模式）
- CLI Backend 是 spawn 外部進程（Agent 分身模式）
