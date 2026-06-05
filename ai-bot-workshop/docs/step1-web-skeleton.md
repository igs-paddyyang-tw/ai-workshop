# Step 1：Web 專案骨架與 Skill 系統

> 使用 Skill：`ark-webapp-generator`
> 觸發語句：「建立 ai-bot Web 專案，首頁使用 quickstart.html」

---

## 1. 詢問時用的提詞

```
建立 ai-bot Web 專案，首頁使用 quickstart.html，
包含 health check API 和 Skill 自動發現機制
```

---

## 2. 常見問題

### 問題 A：PowerShell 不支援 `&` 串接指令

**現象：** 使用 `mkdir a & mkdir b` 語法時 PowerShell 報錯。

**原因：** PowerShell 使用 `;` 作為指令分隔符，`&` 是 CMD 語法。

**解法：** 改用 `;` 分隔，或用 `New-Item -ItemType Directory -Path <路徑> -Force`。

---

## 3. 產出結構

```
ai-bot/
├── src/
│   ├── __init__.py
│   ├── skills/
│   │   ├── base.py              ← BaseSkill + SkillParam + SkillResult
│   │   ├── registry.py          ← SkillRegistry（auto_discover + invoke）
│   │   ├── internal/
│   │   │   ├── __init__.py
│   │   │   ├── echo.py          ← 最小範例 Skill
│   │   │   ├── wiki_manager.py  ← 知識庫管理 Skill
│   │   │   └── cost_tracker.py  ← LLM 成本追蹤 Skill
│   │   └── external/
│   ├── agent/
│   │   ├── verifier.py          ← CodeVerifier（自動 pytest）
│   │   ├── error_handler.py     ← 結構化錯誤分類
│   │   └── event_log.py         ← JSONL 操作日誌
│   └── server/
│       ├── main.py              ← FastAPI + lifespan
│       ├── api/
│       │   └── chat.py          ← POST /api/v1/chat
│       └── static/
│           └── index.html       ← quickstart.html（首頁）
├── knowledge/                   ← 長期知識庫
├── tests/
├── requirements.txt
├── .env.example
└── README.md
```

---

## 4. Skill 系統架構

```
BaseSkill（介面）
    │
    ├── echo.py          ← 範例 Skill（驗證系統）
    ├── llm_cli.py       ← Step 4 加入
    ├── news_scraper.py  ← Step 5 加入
    └── news_renderer.py ← Step 6 加入

SkillRegistry（auto_discover）
    → 掃描 skills/internal/ 目錄
    → 自動載入所有 BaseSkill 子類別
    → 提供 invoke(skill_id, params) 統一呼叫介面
```

---

## 5. 核心元件

| 元件 | 檔案 | 用途 |
|------|------|------|
| BaseSkill | `src/skills/base.py` | 所有 Skill 的抽象介面（skill_id / name / execute） |
| SkillRegistry | `src/skills/registry.py` | 自動掃描載入 Skill，提供 invoke() |
| EchoSkill | `src/skills/internal/echo.py` | 最小範例，回傳輸入內容 |
| FastAPI Server | `src/server/main.py` | Web 入口，掛載 API 路由 + 靜態檔案 |
| Chat API | `src/server/api/chat.py` | POST /api/v1/chat |

---

## 6. 驗證

```bash
python -m src.server.main
```

| 端點 | 方法 | 預期結果 |
|------|------|---------|
| `http://localhost:8000/` | GET | ✅ 顯示 quickstart.html 頁面 |
| `http://localhost:8000/health` | GET | ✅ `{"status": "ok"}` |
| `http://localhost:8000/api/v1/skills` | GET | ✅ 列出已載入 Skills |
| `http://localhost:8000/api/v1/chat` | POST | ✅ Echo Skill 正確回應 |

---

## 7. 安裝的依賴

```
fastapi>=0.110.0
uvicorn[standard]>=0.29.0
python-dotenv>=1.0.0
pydantic>=2.0.0
```

---

*Step 1 完成，Web 骨架與 Skill 系統就緒，可進入 Step 2。*
