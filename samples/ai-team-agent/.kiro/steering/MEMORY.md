# Memory

## 專案狀態（2026-07-15）

- 四層架構完成：gateway / coordinator / runtime / business
- Builder（ark-agent-team-builder）產出 110 項，與本專案 src/ 零差異
- Workshop 教材 4 份（01-04），全部 50 min，已對齊四層架構
- Repo 改名：ark-kiro-skills → ark-agent-skills
- MCP stdio bridge 完成：`src/gateway/mcp_stdio.py`（轉發 tool call → FastAPI port 33333）
- Agent 結構對齊 ai-bot：8 agent 全有 BRAIN + GUARDRAILS + memory + raw + output
- knowledge/shared/ 已建立（raw 5 篇）
- docs/ 結構已建立（specs/designs/plans/one-pagers）
- **常駐化完成（Phase 1-2）**：PersistentDaemon + ManagedProcess + Health Loop
- **對話路由修正完成（2026-07-15）**：統一 MCP reply 路徑

## 技術決策

- LLM：kiro-cli spawn（複雜）+ Gemini Chat（簡單秒回）
- DB：SQLite dev / PostgreSQL prod
- TG 命名空間：src/gateway/telegram/（避免與 python-telegram-bot 衝突）
- A2A：檔案系統 SharedMemory（agent 可直接讀 knowledge/shared/）
- Process：**雙模式 — persistent（預設）+ spawn（fallback）**
- Timeout：300 秒（+ 活動偵測寬限 120 秒）
- MCP：stdio JSON-RPC bridge（需先啟動 bootstrap.py 才能用）
- **回覆路徑決策（2026-07-15）：統一為 MCP reply() tool**
  - 常駐模式：Agent 必須用 `reply()` tool 回覆，不再截取 stdout
  - Spawn 模式：直接 await 拿 stdout 結果回覆（無 MCP）
  - 移除 `_wait_for_reply` + `_push_reply`（stdout regex 截取）
  - TelegramChannel 支援多使用者 routing（`_resolve_chat_id`）
  - A2A callback 透過 `reply_to` metadata 實現
- **常駐化方案：--legacy-ui + stdin pipe（PoC 2026-07-14 驗證通過）**
  - `--legacy-ui` 是關鍵 flag：stdout 有結構化輸出
  - `stderr=STDOUT` 合併後統一讀取
  - Ready pattern: "ctrl-c to start chatting now" / "All tools are now trusted"
  - ~~結束標記: "▸ Time:" 出現在回答末尾~~（已不再使用）
  - ~~回應提取: regex `"> (.+)"`~~（已移除，改由 MCP reply 驅動）
  - Graceful stop: `/quit` → code=0
  - 參考實作: team-agent (D:\kiro-cli\projects\team-agent)

## 對話路由修正記錄（2026-07-15）

- 問題根因：三條回覆路徑打架（MCP reply / stdout 截取 / bootstrap callback）
- 修正方案：方案 A — 統一 MCP reply
- 改動 8 個檔案：
  - `persistent_daemon.py` — 移除 stdout 截取，queue worker 只送不截
  - `bootstrap.py` — 常駐模式不觸發 tg_reply_fn + TelegramChannel 配置重構
  - `chat.py` — 多使用者 routing + A2A reply_to + 移除 complete_fn
  - `messages.py` — 智慧 timeout guard + spawn 同步等待 + get_latest_pending_chat_id
  - `mcp_stdio.py` — send_to_instance 加 reply_to callback
  - 3 個 agent SOUL.md — 補 reply 指示（market/data/report）
- 修正報告：`docs/reports/chat-routing-fix-report.md`

## 常駐化搬遷記錄（2026-07-14）

- 從 team-agent 移植 6 個模組到 src/runtime/：
  - `managed_process.py` — ManagedProcess（ring buffer + pipe 保護）
  - `kiro_backend.py` — KiroBackend（命令建構 + ready/error 偵測）
  - `persistent_daemon.py` — PersistentDaemon（生命週期 + health loop + queue）
  - `heartbeat.py` — 每 30s 寫 timestamp
  - `failure_memory.py` — 錯誤模式追蹤
  - `message_overflow.py` — SQLite backpressure 持久化
- config.py 擴充：RestartPolicy / StartupConfig / persistent / auto_start
- team.yaml 新增：startup.concurrency / defaults.persistent
- 整合測試通過：啟動 → send 2 次（OK / 4）→ graceful stop ✅

## 踩坑紀錄

- WSL2 用 localhost 連（不是 WSL IP）
- venv 必要（PEP 668）
- 多 Bot instance 衝突 → pkill 只留一個
- build_team.py 無 --help flag（任何參數都當目錄名）
- generators 用 repr() 不用 json.dumps()（避免 surrogate 問題）
- 舊路徑 `src/ark_team_core/team_mcp.py` 重構後不存在 → mcp.json 全部更新為 `src/gateway/mcp_stdio.py`
- **常駐化：無 --legacy-ui 時 stdout=0 bytes（TUI 吃掉輸出）**
- **常駐化：MCP server 需要 backend API 先啟動，否則 connection closed**
- **對話路由：stdout 截取 + MCP reply 同時存在 → 雙重回覆或零回覆**
- **對話路由：TelegramChannel._chat_id 只綁一人 → 多使用者時回覆丟失**
- **對話路由：spawn 模式 fire-and-forget → 使用者收不到回覆**
