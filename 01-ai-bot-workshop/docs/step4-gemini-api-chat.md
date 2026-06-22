# Step 4：Gemini API 對話（Bot 即時回應）

> 使用 Skill：`ark-llm-tools`
> 觸發語句：「加入 Gemini API 對話能力，Bot /chat 用 API 即時回話」

---

## 1. 詢問時用的提詞

```
加入 Gemini API 對話能力，使用 google-genai SDK，
Bot /chat 用 API 即時回話，一般文字訊息也走 AI 對話
```

---

## 2. 常見問題

### 問題 A：Windows 上 asyncio.create_subprocess_exec 找不到 .cmd 檔案

**現象：** `[WinError 2] 系統找不到指定的檔案`（僅在使用 CLI 方式時出現）。

**解法：** 本步驟使用 Gemini API SDK（不是 CLI），不會遇到此問題。如需 CLI 請見 Step 6。

### 問題 B：API Key 未設定

**現象：** `google.auth.exceptions.DefaultCredentialsError`

**解法：** 確認 `.env` 中 `GEMINI_API_KEY=` 已填入有效 Key。

---

## 3. 取得 Gemini API Key（免費）

1. 前往 https://aistudio.google.com/apikeys
2. 點擊「Create API Key」→ 複製
3. 填入 `.env`：

```bash
GEMINI_API_KEY=your_actual_api_key_here
```

> 💡 免費額度：60 req/min、1,000 req/day。Step 6 的 Gemini CLI 也共用此 Key。

---

## 4. 產出

```
src/llm/
├── __init__.py
└── gemini_chat.py       ← Gemini API 封裝（chat 專用）
```

---

## 5. 核心實作

```python
from google import genai
import os

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

async def chat(message: str, system_prompt: str = "") -> str:
    """呼叫 Gemini API 進行對話。"""
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=message,
        config={"system_instruction": system_prompt} if system_prompt else None,
    )
    return response.text
```

---

## 6. 與 Step 6 Gemini CLI 的分工

| | Step 4：Gemini API | Step 6：Gemini CLI |
|---|---|---|
| 呼叫方式 | `google-genai` Python SDK | subprocess `gemini -p` |
| 延遲 | 1-5 秒 | 5-30 秒 |
| 適用場景 | Bot /chat 即時對話 | 新聞結構化、codegen |
| 何時用 | 使用者在 TG 打字 | Workflow 自動化任務 |

---

## 7. Bot 整合

- `/chat <問題>` → 呼叫 `gemini_chat.chat()`
- 一般文字 → 呼叫 `gemini_chat.chat()`
- 顯示「🤔 思考中...」→ 1-3 秒後更新為回應

---

## 8. 驗證

```bash
python -m src.bot.main
```

| 測試項目 | 結果 |
|---------|------|
| 📱 `/chat 你是誰` | ✅ 1-3 秒收到 AI 回應 |
| 📱 直接打字「什麼是 Python」 | ✅ 收到 AI 回應 |
| `/status` 顯示 LLM 狀態 | ✅ 可用 |

---

## 9. 新增依賴

```
google-genai>=1.0.0
```

---

*Step 4 完成，AI 對話能力就緒，可進入 Step 5。*
