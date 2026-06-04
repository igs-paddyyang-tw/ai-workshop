# Step 4：LLM CLI 大腦核心封裝 — 建置紀錄

> 日期：2026-05-29

---

## 1. 詢問時用的提詞

```
那就開始進行Step 4的更改
```

---

## 2. 遇到的問題

### 問題 A：Windows 上 asyncio.create_subprocess_exec 找不到 .cmd 檔案

**現象：** 呼叫 `gemini` 時出現 `[WinError 2] 系統找不到指定的檔案`。

**原因：** Windows 上 npm 全域安裝的 CLI 工具實際上是 `.cmd` 批次檔（如 `gemini.cmd`），`create_subprocess_exec` 無法直接執行 `.cmd` 檔案。

### 問題 B：Gemini CLI 需要信任工作目錄

**現象：** 修正問題 A 後，Gemini CLI 回報 `not running in a trusted directory`。

**原因：** Gemini CLI 有安全機制，需要明確信任工作目錄才能執行。

---

## 3. 解決方法

### 問題 A 解法

改用 `asyncio.create_subprocess_shell()` 取代 `create_subprocess_exec()`，讓 shell 自動解析 `.cmd` 檔案。

### 問題 B 解法

在呼叫子程序時設定環境變數 `GEMINI_CLI_TRUST_WORKSPACE=true`：
```python
env = os.environ.copy()
env["GEMINI_CLI_TRUST_WORKSPACE"] = "true"
proc = await asyncio.create_subprocess_shell(cmd, env=env, ...)
```

---

## 4. 結果

### 產出的檔案

```
src/skills/internal/
├── gemini_cli.py    ← v1.0（單一 Gemini 後端）
└── llm_cli.py       ← v2.0（統一 4 後端 + fallback）
```

### LLM CLI Skill 功能

| 功能 | 說明 |
|------|------|
| 四後端支援 | gemini / claude / kiro / ag |
| 自動 fallback | 指定後端不可用時依序嘗試其他 |
| 四種模式 | chat / codegen / skill_gen / evaluate |
| timeout | 可設定超時秒數（預設 30s） |
| 錯誤記錄 | 回報每個後端的嘗試結果 |

### 四種模式說明

| 模式 | 用途 | prompt 包裝 |
|------|------|------------|
| chat | 純對話 | 直接傳入 |
| codegen | 產出程式碼 | 加上「只回傳程式碼」指示 |
| skill_gen | 產出 BaseSkill | 加上 Skill 格式要求 |
| evaluate | 評估需求 | 要求判斷 reply 或 skill |

### 驗證結果

| 測試項目 | 結果 |
|---------|------|
| Skills 載入 | ✅ 3 個（echo + gemini_cli + llm_cli） |
| Gemini CLI 呼叫 | ✅ 成功回覆 |
| 回覆內容 | ✅ 「Python 是一種高階、直觀且用途廣泛的程式語言...」 |
| Backend 識別 | ✅ 正確回報 backend_used: gemini |
| Bot 整合 | ✅ /chat 指令接入 LLM，/status 顯示 LLM 狀態 |

### 測試輸出

```
--- Testing llm_cli skill ---
Status: success
Backend: gemini
Response: Python 是一種高階、直觀且用途廣泛的程式語言，以其簡潔的語法和強大的
標準庫而聞名，廣泛應用於數據科學、人工智慧、自動化及 Web 開發等領域。
```

### Bot 更新內容

- `/chat` 指令現在會呼叫 Gemini CLI 回覆，並顯示使用的後端
- `/status` 指令會動態偵測 LLM CLI 可用性
- 一般訊息（非指令）也會走 LLM 對話路徑

---

*Step 4 完成，LLM 大腦核心就緒，可進入 Step 5。*
