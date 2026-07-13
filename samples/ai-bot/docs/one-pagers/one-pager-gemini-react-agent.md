---
title: "Gemini ReAct Agent + 寫檔能力 + Memory/Wiki 規範釐清"
type: one-pager
status: draft
language: zh-TW
created: 2026-07-13
upgraded_to: null
---

# Gemini ReAct Agent — One Pager

## 問題與目標

**問題**：
1. Default 模式（Gemini）是 stateless 單次呼叫，無法執行任何動作（寫檔、查檔）
2. 對話記錄寫錯位置（admin-agent/knowledge/raw/ 而非 memory/）
3. Memory 和 Wiki 的分工混亂——對話記錄不該進 knowledge，知識不該堆在 memory
4. 使用者明確要求「存進知識庫」時，Gemini 無能力寫檔

**目標**：
- Gemini 對話加入 ReAct（Reason + Act）迴圈，具備讀寫檔能力
- 釐清 Memory vs Wiki vs Output 三區職責，全系統統一
- 使用者說「寫成報告」「存進知識庫」時，Gemini 能實際執行

**成功長怎樣**：
- 使用者對話中要求產出報告 → Gemini 呼叫 write_file → 檔案落地 → 回覆確認
- 對話記錄自動進 memory/daily/，不進 wiki
- Wiki 只有使用者明確要求或人工 ingest 才會寫入

---

## 一、Memory / Wiki / Output 三區職責

### 定義表

| 區域 | 路徑 | 內容性質 | 誰寫 | 生命週期 |
|------|------|----------|------|----------|
| **Memory** | `memory/daily/`、`memory/memory.md`、`memory/recent.md` | 「經歷過的事」：對話記錄、決策、踩坑 | 系統自動（每次對話後） | 永久保留 |
| **Wiki** | `knowledge/shared/wiki/`、`knowledge/{project}/wiki/` | 「查得到的知識」：事實、規格、分析報告 | 使用者明確要求時 | 永久保留 |
| **Output** | `output/{category}/` | 「產出的交付物」：報告、匯出檔、暫存 | Gemini tool / Skill | 可清理 |

### 明確規則

```
✅ Memory 該放什麼：
  - 每次對話摘要（daily log）
  - 持久事實（memory.md）：環境慣例、使用者偏好
  - 最近經驗（recent.md）

❌ Memory 不放什麼：
  - 結構化知識文章（那是 Wiki）
  - 產出的報告（那是 Output）

✅ Wiki 該放什麼：
  - 事實性文章（競品分析、技術規格、SOP）
  - 使用者明確說「存進知識庫」的內容

❌ Wiki 不放什麼：
  - 逐字對話記錄（那是 Memory）
  - 暫時性產出（那是 Output）

✅ Output 該放什麼：
  - 報告（HTML/MD）
  - Skill 執行產出的檔案
  - 匯出資料（CSV/JSON）
  - 暫存草稿

❌ Output 不放什麼：
  - 需要被 recall 搜尋到的內容（那該進 Memory 或 Wiki）
```

### Output 目錄結構

```
output/
├── reports/          ← 報告類（競品分析、市場報告、週報）
│   ├── 2026-07-13_ocean-king-vs-super-ace.md
│   └── 2026-07-13_ocean-king-vs-super-ace.html
├── skills/           ← Skill 執行產出（news 彙整、翻譯結果）
│   └── 2026-07-13_news-digest.md
├── exports/          ← 匯出資料（CSV、JSON）
│   └── 2026-07-13_user-stats.csv
└── drafts/           ← 草稿（未完成的文件）
    └── new-feature-spec.md
```

**檔名規範**：`{date}_{slug}.{ext}`（如 `2026-07-13_ocean-king-analysis.md`）

---

## 二、Gemini ReAct Agent 架構

### 核心迴圈

```
使用者訊息
     │
     ▼
組裝 system prompt（SOUL + BRAIN + Memory + Wiki context + Tools schema）
     │
     ▼
┌─→ 呼叫 Gemini API（帶 function_declarations）
│        │
│        ├── response 有 function_call?
│        │        │
│        │        ▼
│        │   執行 tool handler
│        │   收集結果（成功/失敗）
│        │        │
│        │        ▼
│        │   結果作為 function_response 回傳 Gemini
│        │        │
│        │        └──────── loop back ─────────────┘
│        │
│        └── response 是純文字?
│                 │
│                 ▼
│            回覆使用者
│            寫 daily log（Memory）
│            結束
└────────────────────────────────────────────────
     ↑ max 5 iterations（防止無限迴圈）
```

### 與 Hermes 架構對照

| Hermes 概念 | 我們的對應 | 說明 |
|-------------|-----------|------|
| `run_agent.py` AIAgent | `src/llm/agent_loop.py` | ReAct 迴圈主體 |
| `registry.register()` | `src/tools/registry.py` | Tool 自注冊 |
| `handle_function_call()` | `agent_loop._dispatch_tool()` | FC → handler |
| `SOUL.md` + prompt_builder | `_build_default_system_prompt()` | 組裝 system prompt |
| `MEMORY.md` + `USER.md` | `memory/memory.md` | 持久事實 |
| `write_file` tool | `tools/write_file.py` | 寫檔 handler |
| Skill (SKILL.md) | `src/skills/internal/` | 可執行的流程 |

### 差異：我們不做

- ❌ 不做 session compression（對話不長，Gemini 128k context 夠用）
- ❌ 不做 subagent delegation（Default 模式不派工，派工走 /agents 切到 CLI）
- ❌ 不做 streaming（TG Bot 場景，整段回覆即可）
- ❌ 不做 model failover（單一 Gemini provider）

---

## 三、Tool 清單

### 3 個 Tools

| Tool | 用途 | 可操作路徑 |
|------|------|-----------|
| `read_file` | 讀取專案內檔案 | 全專案（排除 `.env`、`.kiro/`） |
| `write_file` | 寫入/覆寫檔案 | `knowledge/*/wiki/`、`knowledge/*/raw/`、`output/` |
| `list_files` | 列出目錄內容 | 全專案（排除 `.env`、`.kiro/`、`venv/`） |

### Tool Schema（Gemini function_declarations 格式）

```python
TOOLS = [
    {
        "name": "read_file",
        "description": "讀取專案內的檔案內容。用於查看知識庫文章、報告、設定檔等。",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "相對於專案根目錄的檔案路徑，如 knowledge/shared/wiki/overview.md"
                }
            },
            "required": ["path"]
        }
    },
    {
        "name": "write_file",
        "description": "寫入檔案。僅在使用者明確要求產出報告、存入知識庫、匯出資料時使用。不可用於修改程式碼或設定。",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "相對路徑。允許範圍：output/reports/、output/skills/、output/exports/、output/drafts/、knowledge/shared/wiki/、knowledge/shared/raw/"
                },
                "content": {
                    "type": "string",
                    "description": "檔案完整內容（Markdown 或 HTML）"
                }
            },
            "required": ["path", "content"]
        }
    },
    {
        "name": "list_files",
        "description": "列出指定目錄下的檔案清單。用於確認知識庫或 output 裡有什麼。",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "相對路徑，如 knowledge/shared/wiki 或 output/reports"
                }
            },
            "required": ["path"]
        }
    }
]
```

### 路徑安全規則

```python
# 可讀（read_file / list_files）
READABLE_PATHS = ["knowledge/", "output/", "agents/", "docs/", "memory/"]
BLOCKED_READ = [".env", ".kiro/", "venv/", "src/", "__pycache__"]

# 可寫（write_file）
WRITABLE_PATHS = [
    "output/reports/",
    "output/skills/",
    "output/exports/",
    "output/drafts/",
    "knowledge/shared/raw/",
]
# 所有其他路徑 → 拒絕並回傳錯誤訊息
# 注意：knowledge/shared/wiki/ 不可直接寫入，需先進 raw/ 再由 ingest 匯入
```

### write_file 使用時機（寫入 System Prompt）

```
## 寫檔規則

- 只有使用者明確要求時才呼叫 write_file：
  「存進知識庫」「寫成報告」「匯出」「產出文件」
- 對話記錄由系統自動處理，不需你寫
- 寫入前告訴使用者你要寫什麼、寫到哪裡
- 寫入後回覆確認：「✅ 已寫入 output/reports/xxx.md」
```

---

## 四、對話記錄流向修正

### 修正前（有 Bug）

```
Default 對話 → save_memory("admin", ...) → agents/admin-agent/knowledge/raw/ ← 錯誤！
```

### 修正後

```
Default 對話 → write_daily_log("_default", ...) → memory/daily/2026-07-13.md  ← 正確
Agent 對話  → write_daily_log("{agent}", ...) → agents/{agent}-agent/memory/daily/  ← 正確
```

| 模式 | 對話記錄寫入位置 | 寫入格式 |
|------|-----------------|----------|
| Default（Gemini） | `memory/daily/{date}.md` | daily log 摘要 |
| Agent（kiro-cli） | `agents/{name}-agent/memory/daily/{date}.md` | daily log 摘要 |

**移除 `save_memory()` 對 `knowledge/raw/` 的寫入**——對話記錄不是「知識」。

---

## 五、BRAIN.md 補充規範（所有 Agent 通用）

以下段落要加入根目錄和所有 Agent 的 BRAIN.md：

```markdown
## Memory vs Wiki 分工（嚴格區分）

| 問自己 | 答案 | 寫到 |
|--------|------|------|
| 「這是我經歷的事嗎？」 | 是 | memory/ |
| 「這是可重複引用的知識嗎？」 | 是 | knowledge/wiki/ |
| 「這是要交付的產出嗎？」 | 是 | output/ |
| 「使用者有說要存知識庫嗎？」 | 沒有 | 不寫 wiki |

### 紅線補充
- 對話記錄 **只進 memory**，絕不進 knowledge/
- knowledge/wiki/ **只有使用者明確要求**才寫入
- output/ 的內容**不會被 recall 搜尋到**（查知識用 wiki，查經驗用 memory）
```

---

## 六、執行計畫

| # | 階段 | 任務 | 交付物 | 預估 |
|---|------|------|--------|------|
| 1 | 基礎設施 | 建立 `output/` 目錄結構（reports/skills/exports/drafts/） | 目錄 + .gitkeep | 5 min |
| 2 | Tool registry | 新建 `src/tools/registry.py`：Tool 定義 + path 驗證 + dispatch | registry.py | 30 min |
| 3 | Tool handlers | 新建 `src/tools/handlers.py`：read_file / write_file / list_files | handlers.py | 30 min |
| 4 | Agent Loop | 新建 `src/llm/agent_loop.py`：ReAct 迴圈（max 5 iter） | agent_loop.py | 45 min |
| 5 | Gemini FC 改造 | 改 `src/llm/gemini_chat.py`：支援 tools + function_call 解析 | gemini_chat.py 修改 | 30 min |
| 6 | handlers 整合 | 改 `src/bot/handlers.py`：Default 模式用 agent_loop 取代 gemini_chat | handlers.py 修改 | 30 min |
| 7 | 對話記錄修正 | 移除 save_memory → knowledge/raw；改寫 daily_log 到 memory/ | handlers.py + daily_log.py | 20 min |
| 8 | BRAIN.md 更新 | 根目錄 + 8 個 Agent 的 BRAIN.md 加入 Memory/Wiki 分工規範 | 9 個 BRAIN.md | 20 min |
| 9 | System Prompt 注入 | Default system prompt 加入 Tool 使用規則（何時寫/不寫） | handlers.py | 15 min |
| 10 | 驗收測試 | TG 對話 →「幫我比較 X 和 Y，寫成報告」→ 確認 output/ 有檔 | 手動測試 | 15 min |

**總計 ~4 小時**

---

## 七、風險與緩解

| 風險 | 影響 | 緩解 |
|------|------|------|
| Gemini FC 回傳格式不穩定 | tool 執行失敗 | 用 try/except + 重試一次 + fallback 純文字回覆 |
| ReAct 迴圈死循環 | API 費用暴增 | max 5 iterations 硬上限 |
| write_file 寫到不該寫的地方 | 資料破壞 | path 白名單校驗，不在白名單直接拒絕 |
| output/ 檔案越積越多 | 磁碟滿 | 未來加 TTL 清理（本階段不做） |
| 使用者不知道能要求寫檔 | 功能沒人用 | /start 歡迎訊息加提示；SOUL.md 加能力說明 |

---

## 八、驗收條件

- [ ] Gemini 對話中說「寫成報告」→ 呼叫 write_file → `output/reports/` 有檔案
- [ ] Gemini 對話中說「存進知識庫」→ 呼叫 write_file → `knowledge/shared/wiki/` 有檔案
- [ ] 一般對話（沒要求寫檔）→ 不呼叫 write_file → wiki 不新增
- [ ] 對話結束 → daily log 寫入 `memory/daily/`（不寫 knowledge/raw/）
- [ ] read_file 能讀 knowledge/ 和 output/ 下的檔案
- [ ] read_file 不能讀 .env（回傳拒絕訊息）
- [ ] write_file 不能寫 src/、.kiro/、memory/（回傳拒絕訊息）
- [ ] ReAct 迴圈最多 5 次就停（即使 Gemini 持續呼叫 tool）
- [ ] 8 個 Agent 的 BRAIN.md 都有 Memory/Wiki 分工規範
- [ ] `output/` 下有 reports/skills/exports/drafts/ 四個子目錄

---

## 附錄：Gemini API Function Calling 格式參考

```python
# Request
{
    "contents": [...],
    "tools": [{
        "function_declarations": [
            {"name": "write_file", "description": "...", "parameters": {...}}
        ]
    }]
}

# Response（有 function_call 時）
{
    "candidates": [{
        "content": {
            "role": "model",
            "parts": [{
                "functionCall": {
                    "name": "write_file",
                    "args": {"path": "output/reports/xxx.md", "content": "..."}
                }
            }]
        }
    }]
}

# 回傳結果給 Gemini
{
    "contents": [...之前的, model_response,
        {
            "role": "user",
            "parts": [{
                "functionResponse": {
                    "name": "write_file",
                    "response": {"result": "✅ 已寫入 output/reports/xxx.md (1234 bytes)"}
                }
            }]
        }
    ]
}
```
