# Step 3：Gemini API 對話（10 min）

> 使用 google-genai SDK 直接呼叫 Gemini API，Bot /chat 即時 AI 對話。

---

## 1. 詢問時用的提詞

```
加入 Gemini API 對話能力，使用 google-genai SDK，
Bot /chat 用 API 即時回話，一般文字訊息也走 AI 對話
```

---

## 2. 與初階班差異

| 項目 | 初階班（Step 4） | 進階班（本步驟） |
|------|----------------|----------------|
| 方式 | Gemini CLI（子程序呼叫） | google-genai SDK（API 直接呼叫） |
| 延遲 | 5-15 秒 | 1-3 秒 |
| 依賴 | npm + gemini CLI 安裝 | pip install google-genai |
| 認證 | Gmail 登入 | API Key（環境變數） |

---

## 3. 核心實作

```python
from google import genai
import os

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

async def chat(message: str) -> str:
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=message
    )
    return response.text
```

**產出檔案：** `src/llm/gemini_chat.py`

---

## 4. 常見問題

### 問題 A：API Key 未設定

**現象：** `google.auth.exceptions.DefaultCredentialsError`

**解法：** 確認 `.env` 中 `GEMINI_API_KEY=` 已填入有效 Key。

### 問題 B：回應超時

**解法：** `gemini-2.0-flash` 模型回應通常 1-3 秒。如超過 10 秒，檢查網路連線。

---

## 5. 驗證

```
📱 Telegram /chat 你是誰 → 1-3 秒收到 AI 回應 ✅
📱 Telegram 直接打字「什麼是 Python」→ 收到 AI 回應 ✅
```

| 測試項目 | 結果 |
|---------|------|
| Gemini API 連線 | ✅ 回應正常 |
| /chat 指令 | ✅ AI 即時回覆 |
| 一般文字 | ✅ 自動走 AI 對話 |
| 回應延遲 | ✅ < 3 秒 |

---

## 6. 新增依賴

```
google-genai>=1.0.0
```

---

*Step 3 完成，AI 對話能力就緒，可進入 Step 4。*
