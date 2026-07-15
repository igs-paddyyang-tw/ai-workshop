---
title: "對話路由精簡化 執行計畫"
type: plan
version: "1.0"
status: draft
language: zh-TW
author: "ark"
created: 2026-07-15
updated: 2026-07-15
related_design: "docs/designs/chat-routing-simplify-design.md"
---

# 對話路由精簡化 — 執行計畫

## 1. 摘要

將 Telegram Bot 對話路由從六層 if-else 重構為三路徑架構，引入 Ark Agent 智能派工、ProgressStack 進度回饋、Chat Trace 追蹤。分三個 Phase 遞增交付，預估總工時 3-4 天。

## 2. 里程碑（Milestones）

### Phase 1: 核心路由重構（Day 1）

| # | 任務 | 檔案 | 預估 | 依賴 | 驗收條件 |
|---|------|------|------|------|----------|
| 1 | 重寫 handle_message（三路徑：command/\@mention/自然語言） | `src/bot/handlers.py` | 2h | — | 無@→Ark Agent；@→指定agent；非白名單被擋 |
| 2 | Ark Agent 派工 Tool 註冊 | `src/llm/tools/dispatch.py`（新增） | 1.5h | T1 | `dispatch_to_agent` schema 可被 Gemini FC 呼叫 |
| 3 | /start 顯示 chat_id + /help 分段 | `src/bot/handlers.py`（cmd_start, cmd_help） | 0.5h | — | /start 含 ID；/help 分基本/進階 |
| 4 | Bot Menu 精簡 + 權限 decorator | `src/bot/main.py`（BOT_COMMANDS） | 0.5h | — | Menu 6 個；/assign 非白名單被擋 |
| 5 | .env 精簡 + Web API 也走 agent_loop | `.env.example` + `src/server/main.py` | 1h | T2 | 移除未用項；PORT=8080；/api/v1/chat 走 agent_loop |
| 6 | context_builder 追加派工規則 | `src/llm/context_builder.py` | 0.5h | T2 | system prompt 含 dispatch 指引 |
| 7 | provider.py 預設模型改 3.5-flash | `src/llm/provider.py` | 0.5h | — | 預設 gemini-3.5-flash；不可用時手動 fallback |

**Phase 1 交付物**：
- [x] 三路徑路由可運作（TG Bot 側）
- [x] dispatch_to_agent Tool 可被 Gemini FC 呼叫
- [x] 權限控制生效
- [x] Bot Menu 精簡
- [x] Web API `/api/v1/chat` 也走 agent_loop（不再用 planner）
- [x] 預設模型改 gemini-3.5-flash
- [x] .env PORT=8080, CLI_BACKEND=agy

**關鍵程式碼：handle_message**

```python
# src/bot/handlers.py — 重寫後的 handle_message

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """主對話處理：三路徑路由。

    路由：
      1. @agent-name msg → 強制指定 agent（白名單）
      2. 自然語言 → Ark Agent（Gemini ReAct + 自動派工）（白名單）
    """
    text = update.message.text.strip()
    user_id = update.effective_user.id

    # 白名單檢查
    if not _is_authorized(user_id):
        await update.message.reply_text(
            f"🔒 需要權限。\n\nChat ID：`{user_id}`",
            parse_mode="Markdown",
        )
        return

    session = session_manager.get_or_create(user_id)
    session.add_turn("user", text)

    # 👀 收到 + typing
    await _set_reaction(update.message, "👀")
    done = asyncio.Event()
    timer_task = asyncio.create_task(
        _keep_action_alive(update.message.chat_id, "typing", done, context.bot)
    )

    try:
        # @mention → 強制指定 agent
        if match := re.match(r"@([\w-]+)\s*(.*)", text, re.DOTALL):
            target = match.group(1)
            message = match.group(2).strip() or text
            reply = await agent_cli_chat(message, agent_id=target.replace("-agent", ""))
            if reply:
                reply = _clean_output(reply)
                session.add_turn("agent", reply)
                await _set_reaction(update.message, "👍")
                await update.message.reply_text(f"🤖 [{target}]\n{reply}")
            else:
                await _set_reaction(update.message, "👎")
                await update.message.reply_text(f"⚠️ {target} 不可用")
            return

        # 自然語言 → Ark Agent（ReAct + 自動派工）
        from src.llm.context_builder import build_default_system_prompt
        from src.llm.agent_loop import agent_loop
        import src.llm.tools  # 確保 tools 已註冊（含 dispatch_to_agent）

        system_prompt = await build_default_system_prompt(query=text, session=session)
        result = await agent_loop(
            user_message=text,
            system_prompt=system_prompt,
            max_iterations=5,
        )

        if result.text:
            reply = _clean_output(result.text)
            if len(reply) > 3000:
                reply = reply[-3000:]
            session.add_turn("agent", reply)
            await _set_reaction(update.message, "👍")
            full_text = f"🚀 [Ark Agent]\n{reply}"
            for i in range(0, len(full_text), 4000):
                await update.message.reply_text(full_text[i:i+4000])
        else:
            await _set_reaction(update.message, "👎")
            await update.message.reply_text("⚠️ 無法處理，請重試。")

    except Exception as e:
        log.error("handle_message error: %s", e)
        await _set_reaction(update.message, "👎")
        await update.message.reply_text(f"⚠️ 處理失敗：{type(e).__name__}")
    finally:
        done.set()
        timer_task.cancel()
```

**移除項目：**
- `KEYWORD_ROUTES` + `route()` 呼叫（`src/agent/planner.py` 不再被 TG Bot 使用）
- `_build_rich_system_prompt()`（合併到 context_builder）
- `_build_default_system_prompt()`（已獨立在 context_builder.py）
- L1-L4 六層 if-else
- Agent 模式雙分支（統一走 Ark Agent + dispatch_to_agent）
**關鍵程式碼：dispatch_to_agent Tool**

```python
# src/llm/tools/dispatch.py

SCHEMA = {
    "name": "dispatch_to_agent",
    "description": "將任務派給專業 Agent 處理。用於需要特定領域專業知識的任務。",
    "parameters": {
        "type": "object",
        "properties": {
            "target_agent": {
                "type": "string",
                "enum": ["coder-agent", "ai-dev-agent", "data-agent",
                         "market-agent", "report-agent", "qa-agent", "admin-agent"],
                "description": "目標 Agent ID"
            },
            "task_description": {
                "type": "string",
                "description": "任務描述（含使用者原始需求 + 你的分析）"
            },
            "priority": {
                "type": "string",
                "enum": ["low", "normal", "high"],
                "description": "優先級"
            }
        },
        "required": ["target_agent", "task_description"]
    }
}

async def execute(target_agent: str, task_description: str, priority: str = "normal") -> str:
    """派工給指定 Agent，回傳結果或確認。"""
    daemon = get_persistent_daemon()
    if daemon:
        ok = await daemon.send_message(target_agent, task_description)
        if ok:
            return f"✅ 已派工給 {target_agent}（{priority}）"
        return f"❌ {target_agent} 不可用"

    # Fallback: AgentProcess
    from src.agent.cli import agent_cli_chat
    result = await agent_cli_chat(task_description, agent_id=target_agent.replace("-agent", ""))
    return result or f"⚠️ {target_agent} 無回應"
```

**關鍵程式碼：/start + /help + 權限 decorator**

```python
# commands.py
async def cmd_start(update, context):
    uid = update.effective_user.id
    is_allowed = uid in context.bot_data.get("allowed_users", [])
    status = "✅ 已授權" if is_allowed else "🔒 未授權"
    await update.message.reply_text(
        f"👋 歡迎！\n\n• Chat ID：`{uid}`\n• 狀態：{status}\n\n輸入 /help 查看說明。",
        parse_mode="Markdown"
    )

HELP_TEXT = """📖 *基本指令*（所有人）
/start — 歡迎 + Chat ID
/status — 團隊狀態
/help — 本說明

🔒 *進階功能*（需白名單）
直接打字 → Ark Agent 理解意圖 → 自動派工
@agent-name msg → 強制指定 Agent
/agents — Agent 列表
/board — 任務看板
/costs — 費用統計
/assign — 手動派工
/restart — 重啟 Agent
/stop — 停止 Agent
"""

# bootstrap.py — 權限 decorator
def require_whitelist(fn):
    async def wrapper(update, context):
        uid = update.effective_user.id
        if uid not in context.bot_data.get("allowed_users", []):
            await update.message.reply_text(f"🔒 需要權限。你的 ID：{uid}")
            return
        return await fn(update, context)
    return wrapper

# Bot Menu
await tg_app.bot.set_my_commands([
    BotCommand("start", "歡迎"),
    BotCommand("status", "團隊狀態"),
    BotCommand("help", "使用說明"),
    BotCommand("agents", "Agent 列表"),
    BotCommand("board", "任務看板"),
    BotCommand("costs", "費用"),
])
```

**關鍵程式碼：.env.example 精簡**

```dotenv
# ═══ 必要 ═══
TELEGRAM_BOT_TOKEN=
GEMINI_API_KEY=

# ═══ 可選 ═══
# LLM_PROVIDER=gemini                   # gemini / openai / anthropic
# LLM_MODEL=gemini-3.5-flash            # 預設；若不可用改回 gemini-2.5-flash
# LLM_TEMPERATURE=0.7
# CLI_BACKEND=agy                        # 預設 Antigravity CLI（agy > kiro-cli > claude）
# PORT=8080                              # FastAPI Web UI + REST API
# ADMIN_CHAT_IDS=123456,789012           # TG 白名單（逗號分隔）
# LOG_LEVEL=INFO
```

> 移除項目：HOST、A2A_SECRET、各 AGENT_TOKEN、AGENT_NAME（團隊模式專用，非本次範圍）

**關鍵程式碼：Web API 也走 agent_loop**

```python
# src/server/main.py — /api/v1/chat 改寫

@app.post("/api/v1/chat")
async def api_chat(req: ChatRequest):
    """統一對話 API — 走 Ark Agent ReAct Loop（與 TG handle_message 同路徑）。"""
    text = req.message.strip()

    from src.llm.context_builder import build_default_system_prompt
    from src.llm.agent_loop import agent_loop
    import src.llm.tools  # 確保 tools 已註冊

    system_prompt = await build_default_system_prompt(query=text)
    result = await agent_loop(
        user_message=text,
        system_prompt=system_prompt,
        max_iterations=5,
    )

    reply = result.text or "⚠️ 無法回應"

    return {
        "reply": reply,
        "source": "agent_loop",
        "iterations": result.iterations,
        "tools_used": [t["tool"] for t in result.tool_calls_log],
    }
```

**關鍵程式碼：provider.py 預設模型**

```python
# src/llm/provider.py — 改一行
model = os.getenv("LLM_MODEL", "gemini-3.5-flash")  # 原本是 gemini-2.5-flash
```

---

### Phase 2: 進度回饋（Day 2）

| # | 任務 | 檔案 | 預估 | 依賴 | 驗收條件 |
|---|------|------|------|------|----------|
| 8 | ProgressStack class | `src/bot/progress.py`（新增） | 1.5h | — | init/update/complete/fail 四方法正常運作 |
| 9 | handle_message 整合 progress | `src/bot/handlers.py` | 1h | T1, T8 | 派工時顯示堆疊更新 |
| 10 | dispatch_to_agent 回調更新 progress | `src/llm/tools/dispatch.py` | 0.5h | T2, T8 | 派工/完成時 progress 有更新 |

**Phase 2 交付物**：
- [x] 收到訊息 → 👀 reaction + ProgressStack 初始化
- [x] Ark Agent 派工 → 📋 通知 + ⏳ 等待
- [x] Agent reply 成功 → ✅ 完成 + 👍 reaction
- [x] Agent 失敗/超時 → ❌ 失敗 + 👎 reaction

**關鍵程式碼：ProgressStack**

```python
# src/bot/progress.py

class ProgressStack:
    """堆疊式進度訊息，透過 edit_message 原地更新。"""

    def __init__(self, chat_id: int, bot):
        self.chat_id = chat_id
        self.bot = bot
        self.message_id: int | None = None
        self.steps: list[str] = []

    async def init(self, first_step: str):
        """發送第一條訊息，記錄 message_id。"""
        self.steps.append(f"⏳ {first_step}")
        msg = await self.bot.send_message(self.chat_id, self._render())
        self.message_id = msg.message_id

    async def update(self, step: str, complete_previous: bool = True):
        """標記上一步完成 + 新增下一步。"""
        if complete_previous and self.steps:
            last = self.steps[-1]
            if last.startswith("⏳"):
                self.steps[-1] = last.replace("⏳", "✅")
        self.steps.append(f"⏳ {step}")
        await self._edit()

    async def complete(self, final_text: str):
        """標記全部完成 + 附上最終回覆。"""
        if self.steps and self.steps[-1].startswith("⏳"):
            self.steps[-1] = self.steps[-1].replace("⏳", "✅")
        separator = "───────────────────────"
        full = self._render() + f"\n{separator}\n{final_text}"
        await self._edit(full)

    async def fail(self, error: str):
        """標記失敗。"""
        if self.steps and self.steps[-1].startswith("⏳"):
            self.steps[-1] = self.steps[-1].replace("⏳", "❌")
        self.steps.append(f"⚠️ {error}")
        await self._edit()

    def _render(self) -> str:
        return "🚀 [Ark Agent]\n\n" + "\n".join(self.steps)

    async def _edit(self, text: str | None = None):
        try:
            await self.bot.edit_message_text(
                chat_id=self.chat_id,
                message_id=self.message_id,
                text=text or self._render(),
            )
        except Exception:
            pass  # 訊息未變更時會拋錯，忽略
```

---

### Phase 3: Chat Trace（Day 3）

| # | 任務 | 檔案 | 預估 | 依賴 | 驗收條件 |
|---|------|------|------|------|----------|
| 11a | ChatTrace model + SQLite | `src/memory/chat_trace.py`（新增） | 1h | — | DB 建立 + CRUD 正常 |
| 11b | handle_message 寫入 trace | `src/bot/handlers.py` | 0.5h | T1, T11a | 每次訊息寫入 trace_id + timestamp |
| 11c | dispatch_to_agent 回調寫入 | `src/llm/tools/dispatch.py` | 0.5h | T2, T11a | 派工時寫入 target_agent |
| 11d | reply 完成寫入 | `src/llm/tools/dispatch.py` | 0.5h | T11a | Agent reply 寫入 summary + success |
| 11e | timeout 寫入 success=false | `src/bot/handlers.py` | 0.5h | T11a | 5 分鐘超時標記失敗 |
| 11f | GET /api/chat/traces endpoint | `src/server/main.py` | 0.5h | T11a | API 可查詢最近 7 天 traces |

**Phase 3 交付物**：
- [x] Chat Trace 正確記錄（直答 + 派工兩種路徑）
- [x] 7 天自動清理
- [x] REST API 可查詢

---

## 3. 風險管理（Risk Management）

| 風險 | 機率 | 影響 | 緩解策略 | 觸發條件 |
|------|------|------|----------|----------|
| Gemini API 延遲 >10s | M | M | ProgressStack 提供即時回饋，使用者不會以為卡死 | P99 延遲監控 |
| agy CLI 首次 ToS 卡住 | L | H | 文件明確標註手動完成步驟；CI 不跑 agy | 部署到新機器時 |
| edit_message 4096 字元限制 | L | L | complete() 時截斷 + 附「完整回覆太長，已精簡」 | 長回覆場景 |
| Gemini FC schema 格式不相容 | M | H | 清理 schema（移除 anyOf/title/default），已知 workaround | 換模型版本時 |
| 白名單 race condition | L | L | bot_data 為 in-memory list，單 process 無競爭 | — |

## 4. 驗證標準（Verification Criteria）

| 類別 | 指標 | 目標 | 驗證方式 |
|------|------|------|----------|
| 功能驗收 | 驗收清單全過 | 15/15 項通過 | 手動測試 |
| 路由正確 | 三路徑覆蓋 | command + @mention + 自然語言 | 手動發訊測試 |
| 權限攔截 | 非白名單被擋 | 100% | 用非白名單帳號測試 |
| 進度回饋 | ProgressStack 更新 | 每步可見 | 觀察 TG 訊息 |
| Trace 完整 | 直答 + 派工都有記錄 | 查 SQLite 驗證 | sqlite3 CLI |

### 驗收清單

- [ ] 非白名單發訊 → 回覆「需要權限 + ID」
- [ ] 白名單無 @ → Ark Agent 收到 → 自動判斷是否派工
- [ ] 簡單問題 → Ark Agent 直接回覆（不派工）
- [ ] 複雜任務 → Ark Agent 派工給對應 Agent
- [ ] @coder-agent xxx → coder-agent 直接收到
- [ ] /start → 顯示 Chat ID
- [ ] /help → 基本/進階兩段
- [ ] /status → 所有人可用
- [ ] /assign → 非白名單被擋
- [ ] Bot Menu 6 個指令
- [ ] .env.example 精簡
- [ ] 收到訊息 → 👀 reaction + ProgressStack 初始化
- [ ] Ark Agent 派工成功 → 📋 通知 + 持續 typing
- [ ] Agent reply 成功 → 👍 reaction + 停止 typing
- [ ] Chat Trace 正確記錄（直答 + 派工兩種路徑）

## 5. 回滾計畫（Rollback Plan）

| 觸發條件 | 回滾步驟 | 預估時間 | 負責人 |
|----------|----------|----------|--------|
| 路由重構導致 Bot 無法回覆 | `git checkout HEAD -- src/bot/handlers.py src/bot/main.py src/llm/provider.py .env.example` | 1 min | ark |
| Phase 2 ProgressStack 造成 TG API 頻率限制 | 關閉 progress 功能（flag off） | 1 min | ark |
| Phase 3 SQLite 寫入阻塞主線程 | 移除 trace 寫入（異步化或關閉） | 5 min | ark |

## 6. 依賴與前置條件

### 外部依賴

| 依賴 | 版本 | 用途 |
|------|------|------|
| python-telegram-bot | ≥20.0 | TG Bot Gateway |
| google-genai | latest | Gemini API SDK |
| agy (Antigravity CLI) | latest | Agent 執行引擎 |
| SQLite | 3.x（Python 內建） | Trace + Memory |
| FastAPI | ≥0.100 | REST API |

### 環境需求

- Python ≥3.11（asyncio 改善）
- `.env` 配置：TELEGRAM_BOT_TOKEN + GEMINI_API_KEY
- agy 已完成首次 ToS + OAuth（手動）
- agy 在 PATH 或 `%LOCALAPPDATA%\agy\bin\`

## 7. 移除項目

Phase 1 完成後，以下程式碼/設定應移除：

| 項目 | 檔案 | 說明 |
|------|------|------|
| `KEYWORD_ROUTES` dict | `src/agent/planner.py` | 關鍵字路由表（TG Bot 不再呼叫） |
| `route()` 呼叫 | `src/bot/handlers.py` | L3 planner 分支 |
| `_build_rich_system_prompt()` | `src/bot/handlers.py` | 改用 context_builder.py 統一組裝 |
| `_build_default_system_prompt()` | `src/bot/handlers.py` | 已獨立到 context_builder.py |
| L1-L4 六層 if-else | `src/bot/handlers.py` | 整段替換為三路徑 |
| `_search_memory()` helper | `src/bot/handlers.py` | 改用 recall tool |
| planner import in server | `src/server/main.py` | /api/v1/chat 改走 agent_loop |
| 未使用 .env 項目 | `.env.example` | HOST、A2A_SECRET 等 |
