---
inclusion: always
---
# Memory

## 專案狀態（2026-07-27 14:49 更新）

- 四層架構完成：gateway / coordinator / runtime / business
- 8 agent 常駐，**pm-agent → leader-agent 更名完成 ✅**
- MCP stdio bridge：`src/gateway/mcp_stdio.py`（JSON-RPC over stdin/stdout）
- 對話路由：統一 MCP `reply()` tool（常駐模式）/ 同步 stdout（spawn 模式）
- **Chat Router 已註冊 ✅**（修復 /api/chat/* 404 問題）
- **bootstrap.py async 修正 ✅**（sync/async 混用 + DB leak 修復）
- **mcp_stdio.py UTF-8 surrogate guard ✅**（Windows io.TextIOWrapper）
- knowledge/shared/ 已建立（wiki 6 篇 + raw 2 篇）
- docs/ 結構已建立（specs/designs/plans/one-pagers/reports/tests）
- **Drift Score 97/100 ✅**（smoke_test 36 passed，API 100%，依賴 0 violations）
- `chat_trace.py` 新增對話軌跡追蹤（SQLite，7 天清理）
- TG 任務通知修復：`#?` → 真實 issue_id + title + agent_id + output 摘要
- kiro-cli defaultModel 改為 `auto`（`claude-opus-4.6` 已下架）
- agent.json `file://` 路徑修正：`.kiro/` → `../`（kiro-cli 從 json 所在目錄解析）
- **.kiro 主入口重構 ✅**：`admin-agent.json` → `ai-team-agent.json`（通用 orchestrator，解除與子 agent 身分重疊）
- **子 agent pm-agent 引用清除 ✅**：admin/market/data 的 SOUL.md 全部對齊 leader-agent + 8 人團隊

## 技術決策

- LLM：kiro-cli `auto` model（`claude-opus-4.6` 已下架，勿用）
- DB：SQLite dev / PostgreSQL prod
- Process：**雙模式 — persistent（預設）+ spawn（fallback）**
- 常駐模式：`--legacy-ui --trust-all-tools --require-mcp-startup` + stdin pipe
- MCP：stdio JSON-RPC bridge（需先啟動 bootstrap.py 才能用）
- cwd：`agents/{name}/`（kiro-cli 從 cwd/.kiro/settings/mcp.json 載入 MCP）
- Timeout：300 秒 + 活動偵測寬限 120 秒
- 回覆路徑：Agent 用 MCP `reply(text, summary)` → POST /api/chat/reply → TG

## 對話路由設計（2026-07-15 定案）

### 常駐模式
```
User(TG) → handle_message → daemon.send_message → stdin pipe → Agent
  → Agent 呼叫 MCP reply() → mcp_stdio → POST /api/chat/reply → TG
```

### Spawn 模式（fallback）
```
User(TG) → handle_message → await agent.send(msg)
  → fork kiro-cli --no-interactive msg → stdout → reply_text → TG
```

### 關鍵元件
- `persistent_daemon.py` — queue worker 只送 stdin，不截 stdout
- `mcp_stdio.py` — JSON-RPC bridge，11 tools（reply/send_to_instance/delegate_task...）
- `chat.py` — TelegramChannel 多使用者 routing + A2A reply_to
- `messages.py` — 智慧 timeout guard（300s + 活動偵測）

## MCP 修復記錄（2026-07-15）

### 根因鏈（三層疊加）
1. **cp950 UnicodeEncodeError** — tool description 含中文/Unicode（≤80字）→ `sys.stdout.write()` 用 Windows cp950 編碼 → crash → stderr traceback
2. **stderr 輸出** — kiro-cli 把 MCP server 的 stderr 任何輸出視為 Transport closed → 判定 server 失敗
3. **UTF-8 BOM** — PowerShell `Set-Content -Encoding UTF8` 預設加 BOM → kiro-cli JSON parser 報 "expected value at line 1 column 1"

### 修正
- `json.dumps(ensure_ascii=True)` — 所有 stdout JSON 用 ASCII 序列化
- logging 改 `NullHandler`（不寫 stderr）
- 移除所有 `print(..., file=stderr)`
- 8 個 mcp.json 移除 UTF-8 BOM
- mcp.json 用相對路徑 + `py` command（和原始 git 版本一致）

### 排查過程中的錯誤方向（已恢復）
- ~~cwd 改為 instances/~~ → 改回 `agents/{name}/`
- ~~MCP reply 路徑 A（移除 stdout 截取）~~ → 正確方向，保留
- ~~Workspace trust 問題~~ → 排除（mcp_enabled=true 但 server crash）
- ~~啟動順序 race condition~~ → 排除（hub 先起 3 秒後才 spawn agent）
- ~~--legacy-ui 不支援 MCP~~ → 排除（ark-team-agent 證明可以）

## 踩坑紀錄（精簡版）

| 問題 | 原因 | 修正 |
|------|------|------|
| MCP server versions 空 | cp950 encode error → stderr → Transport closed | ensure_ascii=True |
| mcp.json parse 失敗 | UTF-8 BOM | 用 Python write_bytes 寫入（無 BOM） |
| MCP tools 不載入 | stderr 有 debug log 輸出 | NullHandler，不寫 stderr |
| Agent 不用 reply tool | MCP server 未成功載入 | 修好上面三個 |
| reply 後 kiro-cli crash | Agent reply 後試圖再生成 → API 失敗 | wrapped msg 加「回覆後不要做其他動作」|
| stdout 截取 + MCP 重複回覆 | 兩條路徑並存 | 移除 _wait_for_reply，統一 MCP |
| spawn 模式 fire-and-forget | asyncio.create_task 不等結果 | 改 await agent.send() |
| TelegramChannel 單使用者 | _chat_id 只綁一人 | _resolve_chat_id 多使用者 routing |
| instances/ 殘留 | cwd 改為 working_directory 後不再需要 | 刪除 + .gitignore |
| 常駐模式無 --legacy-ui 時 stdout=0 | TUI 吃掉輸出 | 必須帶 --legacy-ui |
| venv 必要 | PEP 668 | 用 .venv |
| PowerShell Set-Content 加 BOM | Windows 預設行為 | 用 Python 寫檔 |
| TG 通知顯示 #? | scheduler emit 缺 issue_id；issues emit 缺 title | 三處補欄位（scheduler/issues/notifications）|
| PATCH /persistent 用裸 dict body | FastAPI 不接受無 Content-Type dict | 改 PersistentToggleRequest Pydantic model |
| agent.json file:// 路徑錯誤 | kiro-cli 從 json 所在目錄（.kiro/agents/）解析，非 cwd | `file://.kiro/` → `file://../` |
| claude-opus-4.6 不可用 | 模型已下架，kiro-cli 收到錯誤靜默退出，不呼叫 reply | cli.json `chat.defaultModel: "auto"` |
| cli.json BOM（再次觸發） | PowerShell Set-Content 寫入時加 UTF-8 BOM | Python `write_bytes()` 寫入（無 BOM）|
| Chat Router 未註冊（404） | chat.py 有 router 但 router.py 沒 include | 加 import + include_router |
| bootstrap sync/async 混用 | get_db() sync conn 配 async fetch_one | 統一 get_async_db + await |
| MCP reply surrogate error | Windows stdin/stdout 混入 cp950 surrogate | io.TextIOWrapper(errors='replace') |

## 參考實作

- `D:\kiro-cli\projects\ark-team-agent` — 完整 MCP team agent（已驗證可跑）
- `D:\kiro-cli\projects\ai-team-agent` — GitHub 版（spawn 模式，無常駐）
