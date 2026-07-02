---
title: "a-agent Inline Button Agent 切換 + Memory 管理"
type: onepager
status: draft
language: zh-TW
created: 2026-07-02
---

# a-agent — Inline Button Agent 切換 + Memory 管理

## 問題

目前 `/agent` 是純文字指令，切換後沒有記憶管理。需要：
1. 用 Inline Button 選 Agent（更直覺）
2. 一次只能跟一個 Agent 對話
3. 每次對話完成後 Agent 自動更新 memory
4. 記錄 user_id + 任務 + 結果

## 目標

- `/agents` 叫出 Inline Keyboard（4 個 Agent 按鈕）
- 選擇後進入該 Agent 的對話模式（直到再次 `/agents` 切換）
- Agent 完成任務後自動寫入 `agents/{name}-agent/knowledge/raw/{task}.md`
- 每個 Agent 獨立管理自己的 memory（不共用）

## 非目標

- 不做多輪併行對話（一次只能跟一個 Agent）
- 不做 Agent 之間的通訊（那是課程 B 的 A2A）
- 不做複雜的 session 過期機制

## 方案

### 互動流程

```
使用者輸入 /agents
    │
    ▼
Bot 回覆 Inline Keyboard：
┌────────────┬────────────┐
│ 🤖 Admin   │ 📰 News    │
├────────────┼────────────┤
│ 💻 Code    │ 📚 Wiki    │
└────────────┴────────────┘
    │
    ▼ 使用者點擊「📰 News」
    │
Bot 回覆：「✅ 已切換到 📰 News Agent — 科技新聞專家」
    │
    ▼ 使用者輸入「今天 AI 有什麼大事？」
    │
News Agent 執行（kiro-cli 或 Gemini + SOUL）
    │
    ▼ 回覆結果
    │
    ▼ 自動更新 memory：
    agents/news-agent/knowledge/raw/2026-07-02_user123_task.md
```

### Memory 結構

```markdown
---
user_id: 123456789
task: "查詢今日 AI 新聞"
agent: news-agent
timestamp: 2026-07-02T09:30:00+08:00
status: completed
---

## 任務

查詢今日 AI 新聞

## 結果

1. Claude Opus 5 發布 — Anthropic 新模型...
2. ...

## 學到的

- 使用者偏好 AI 領域的新聞
- HN 今日排名前 3 都是 AI 相關
```

### 需要改動的檔案

| 檔案 | 改動 |
|------|------|
| `src/bot/handlers.py` | 加 `cmd_agents`（Inline Keyboard）+ `callback_switch_agent`（按鈕回調） |
| `src/bot/main.py` | 註冊 CallbackQueryHandler |
| `src/agent/cli.py` | 加 `save_memory()`（寫入 knowledge/raw/） |
| `src/agent/session.py` | **新增** — 管理 user_id ↔ current_agent 對應 |

### src/agent/session.py（新增）

```python
"""Agent Session 管理 — 每個 user 一次只能跟一個 Agent 對話。"""
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class UserSession:
    user_id: int
    current_agent: str = "admin"
    last_task: str = ""
    last_active: str = field(default_factory=lambda: datetime.now().isoformat())


class SessionManager:
    def __init__(self):
        self._sessions: dict[int, UserSession] = {}

    def get_or_create(self, user_id: int) -> UserSession:
        if user_id not in self._sessions:
            self._sessions[user_id] = UserSession(user_id=user_id)
        return self._sessions[user_id]

    def switch_agent(self, user_id: int, agent_id: str) -> UserSession:
        session = self.get_or_create(user_id)
        session.current_agent = agent_id
        session.last_active = datetime.now().isoformat()
        return session

session_manager = SessionManager()
```

### Inline Button Handler

```python
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

async def cmd_agents(update, context):
    keyboard = [
        [
            InlineKeyboardButton("🤖 Admin", callback_data="agent:admin"),
            InlineKeyboardButton("📰 News", callback_data="agent:news"),
        ],
        [
            InlineKeyboardButton("💻 Code", callback_data="agent:code"),
            InlineKeyboardButton("📚 Wiki", callback_data="agent:wiki"),
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("選擇 Agent：", reply_markup=reply_markup)

async def callback_switch_agent(update, context):
    query = update.callback_query
    await query.answer()
    agent_id = query.data.split(":")[1]  # "agent:news" → "news"
    user_id = query.from_user.id
    session_manager.switch_agent(user_id, agent_id)
    info = AVAILABLE_AGENTS[agent_id]
    await query.edit_message_text(f"✅ 已切換到 {info['emoji']} {info['name']}\n\n{info['desc']}")
```

### Memory 寫入

```python
async def save_memory(agent_id: str, user_id: int, task: str, result: str):
    """Agent 完成任務後自動寫入 memory。"""
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M")
    filename = f"{timestamp}_user{user_id}.md"
    path = Path(f"agents/{agent_id}-agent/knowledge/raw/{filename}")
    path.parent.mkdir(parents=True, exist_ok=True)

    content = f"""---
user_id: {user_id}
task: "{task}"
agent: {agent_id}-agent
timestamp: {datetime.now().isoformat()}
status: completed
---

## 任務

{task}

## 結果

{result}
"""
    path.write_text(content, encoding="utf-8")
```

### handle_message 更新

```python
async def handle_message(update, context):
    user_id = update.effective_user.id
    session = session_manager.get_or_create(user_id)
    current = session.current_agent  # 用 session 而非 module-level 變數

    # ... 執行對話 ...

    # 完成後寫入 memory
    await save_memory(current, user_id, text, reply)
```

## 執行步驟

| # | 任務 | 工時 |
|---|------|------|
| 1 | 新增 `src/agent/session.py`（SessionManager） | 10 min |
| 2 | 新增 `src/agent/memory.py`（save_memory） | 10 min |
| 3 | 更新 `handlers.py`（Inline Button + callback + session 整合） | 20 min |
| 4 | 更新 `bot/main.py`（註冊 CallbackQueryHandler） | 5 min |
| 5 | 更新 `cli.py`（移除 module-level state，改用 session） | 10 min |
| **合計** | | **~55 min** |

## 驗收條件

- [ ] `/agents` 顯示 Inline Keyboard（4 按鈕）
- [ ] 點按鈕切換 Agent，Bot 確認切換成功
- [ ] 切換後對話使用對應 Agent 的 SOUL.md
- [ ] 對話完成後 `agents/{name}-agent/knowledge/raw/` 有新 .md 檔
- [ ] memory 檔案包含 user_id + task + result + timestamp
- [ ] 不同 user_id 各自獨立（A 切到 news，B 還在 admin）
- [ ] 一次只能跟一個 Agent 對話（不能並行）

---

*使用 ark-superpowers 框架產出。*
