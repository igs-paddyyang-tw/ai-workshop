# Step 1：Web 專案骨架與 Skill 系統 — 建置紀錄

> 日期：2026-05-29

---

## 1. 詢問時用的提詞

```
請按照建置七步驟幫我做一個可執行的計畫
```

（由 AI 產出 EXECUTION-PLAN.md 後，依 Step 1 內容逐步執行）

```
直接進行Step 1的內容
```

---

## 2. 遇到的問題

### 問題 A：PowerShell 不支援 `&` 串接指令

**現象：** 使用 `mkdir a & mkdir b` 語法建立多個目錄時，PowerShell 報錯「不允許使用 & 符號字元」。

**原因：** PowerShell 使用 `;` 作為指令分隔符，`&` 是 CMD 語法。

### 問題 B：無其他阻礙

Step 1 的依賴（FastAPI、uvicorn、pydantic）在環境中已預先安裝，建置過程順利。

---

## 3. 解決方法

### 問題 A 解法

改用 PowerShell 語法 `New-Item -ItemType Directory -Path <路徑> -Force`，多個指令用 `;` 分隔。

---

## 4. 結果

### 產出的專案結構

```
ai-bot/
├── src/
│   ├── __init__.py
│   ├── skills/
│   │   ├── __init__.py
│   │   ├── base.py              ← BaseSkill + SkillParam + SkillResult
│   │   ├── registry.py          ← SkillRegistry（auto_discover + invoke）
│   │   ├── internal/
│   │   │   ├── __init__.py
│   │   │   └── echo.py          ← 範例 Skill（驗證系統）
│   │   └── external/
│   │       └── __init__.py
│   ├── agent/
│   │   ├── __init__.py
│   │   ├── verifier.py          ← CodeVerifier（自動 pytest）
│   │   ├── error_handler.py     ← 結構化錯誤分類
│   │   └── event_log.py         ← JSONL 操作日誌
│   └── server/
│       ├── __init__.py
│       ├── main.py              ← FastAPI + lifespan
│       ├── api/
│       │   ├── __init__.py
│       │   └── chat.py          ← POST /api/v1/chat
│       └── static/
│           └── index.html       ← quickstart.html（首頁）
├── knowledge/
├── tests/
│   └── __init__.py
├── requirements.txt
├── .env
└── README.md
```

### API 驗證結果

| 端點 | 方法 | 結果 |
|------|------|------|
| `http://localhost:8000/` | GET | ✅ 顯示 quickstart.html 頁面 |
| `http://localhost:8000/health` | GET | ✅ `{"status": "ok"}` |
| `http://localhost:8000/api/v1/skills` | GET | ✅ 列出 Echo Skill |
| `http://localhost:8000/api/v1/chat` | POST | ✅ Echo Skill 正確回應 |

### 核心元件說明

| 元件 | 檔案 | 用途 |
|------|------|------|
| BaseSkill | `src/skills/base.py` | 所有 Skill 的抽象介面（skill_id / name / execute） |
| SkillRegistry | `src/skills/registry.py` | 自動掃描 internal/ 載入 Skill，提供 invoke() 統一呼叫 |
| EchoSkill | `src/skills/internal/echo.py` | 最小範例，回傳輸入內容 |
| FastAPI Server | `src/server/main.py` | Web 入口，掛載 API 路由 + 靜態檔案 |
| Chat API | `src/server/api/chat.py` | POST /api/v1/chat，接收訊息並路由到 Skill |
| EventLog | `src/agent/event_log.py` | JSONL 格式操作日誌 |
| ErrorHandler | `src/agent/error_handler.py` | 例外分類（network/timeout/auth/parse） |
| CodeVerifier | `src/agent/verifier.py` | 自動執行 pytest 驗證 |

### 安裝的依賴

```
fastapi>=0.110.0
uvicorn[standard]>=0.29.0
python-dotenv>=1.0.0
pydantic>=2.0.0
```

---

*Step 1 完成，Web 骨架與 Skill 系統就緒，可進入 Step 2。*
