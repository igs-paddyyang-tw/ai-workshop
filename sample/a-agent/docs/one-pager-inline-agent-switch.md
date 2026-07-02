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

## Phase 2：進階 Memory 系統

### 2.1 多輪對話記憶（Conversation History）

**問題**：目前每次對話獨立，Agent 不記得上一句。

**設計**：

```python
@dataclass
class ConversationTurn:
    role: str        # "user" | "agent"
    content: str
    timestamp: str

@dataclass
class UserSession:
    user_id: int
    current_agent: str
    history: list[ConversationTurn] = field(default_factory=list)
    max_turns: int = 10  # 保留最近 10 輪
```

**效果**：
```
使用者：「今天 AI 新聞」
Agent：「1. Claude 5 發布 2. ...」
使用者：「第一則詳細說」          ← Agent 記得上一輪
Agent：「Claude 5 是 Anthropic...」
```

**注入方式**：把 history 作為 context 傳給 kiro-cli 或 Gemini API。

### 2.2 使用者 Profile（User Persona）

**問題**：每次對話都從零開始判斷使用者偏好。

**設計**：

```
agents/{name}-agent/knowledge/raw/profiles/
└── user_{id}.md
```

```markdown
---
user_id: 123456789
first_seen: 2026-07-01
total_interactions: 42
---

## 偏好

- 語言：繁體中文
- 關注領域：AI、Python、雲端架構
- 回答風格偏好：簡潔、附程式碼
- 活躍時段：早 9-11、晚 8-10

## 常問主題

| 主題 | 次數 | 最近一次 |
|------|------|---------|
| AI 新聞 | 15 | 2026-07-02 |
| Python 問題 | 12 | 2026-07-01 |
| FastAPI | 8 | 2026-06-30 |

## 特殊備註

- 偏好用 httpx 而非 requests
- 專案用 Python 3.12 + FastAPI
- 不喜歡太長的解釋
```

**觸發時機**：每 10 次互動或每日結束時，Agent 用 LLM 更新 profile。

**讀取方式**：對話前載入 profile 作為額外 context 注入。

### 2.3 知識缺口追蹤（Knowledge Gap）

**問題**：使用者問了但 Wiki 查不到的，沒有被記錄。

**設計**：

```
agents/{name}-agent/knowledge/raw/gaps/
└── 2026-07-02_gaps.md
```

```markdown
---
date: 2026-07-02
agent: wiki-agent
---

## 知識缺口（今日查不到的問題）

| 問題 | 使用者 | 建議補充 |
|------|--------|---------|
| Docker Compose v2 差異 | user123 | 需要 docker 相關文件 |
| asyncio vs threading 比較 | user456 | 可從 python-async-guide 擴充 |
```

**用途**：
- 定期 review gaps → 補充 raw/ 文件 → ingest → Wiki 成長
- 這就是「自演化循環」的起點

### 2.4 跨 Agent 共享記憶（Shared Memory）

**問題**：user 在 news-agent 聊的，admin-agent 不知道。

**設計**：

```
knowledge/shared/
├── user_{id}_summary.md    ← 跨 Agent 的使用者摘要
└── today_highlights.md     ← 今日各 Agent 的重要發現
```

**寫入時機**：Agent 完成任務時，如果是「重要發現」就同步寫 shared。

**讀取時機**：切換 Agent 時，新 Agent 載入 shared/ 了解上下文。

**效果**：
```
User 在 news-agent 問了 AI 新聞
    → shared/user_123_summary.md 記錄「user 關注 AI」
User 切到 code-agent 問問題
    → code-agent 讀 shared → 知道 user 在看 AI 新聞
    → 回答時自然關聯「剛看到 Claude 5 的新 API，你可以這樣用...」
```

### 2.5 情緒/滿意度追蹤

**設計**：在 memory 檔案加入 LLM 自評：

```markdown
## Agent 自評

- 回答完整度：8/10
- 使用者可能滿意度：7/10（問題較廣泛，回答可能不夠聚焦）
- 改善建議：下次先確認使用者想要的深度
```

**用途**：長期追蹤 Agent 的回答品質，找出需要改善的模式。

---

## Phase 2 執行優先順序

| # | 功能 | 難度 | 價值 | 建議時機 |
|---|------|------|------|---------|
| 1 | 多輪對話記憶 | 中 | 🔴 高 | Phase 1 完成後立即 |
| 2 | 使用者 Profile | 中 | 🟡 中 | 互動 > 20 次時 |
| 3 | 知識缺口追蹤 | 低 | 🟡 中 | Wiki 穩定後 |
| 4 | 跨 Agent 共享 | 高 | 🟢 低（a-agent 場景） | 需要協作時 |
| 5 | 情緒/滿意度 | 低 | 🟢 低 | 品質優化期 |

> 注意：功能 4（跨 Agent 共享）在課程 B 的 b-agent-team 中已內建（A2A + shared_memory）。
> a-agent 的定位是「個體」，跨 Agent 共享是可選的進階功能。

---

## 完整 Memory 架構圖

```
agents/{name}-agent/
├── knowledge/
│   ├── raw/                         ← Agent 寫入
│   │   ├── 2026-07-02_0930_user123.md   ← 任務記錄（Phase 1）
│   │   ├── profiles/                     ← 使用者畫像（Phase 2.2）
│   │   │   └── user_123.md
│   │   └── gaps/                         ← 知識缺口（Phase 2.3）
│   │       └── 2026-07-02_gaps.md
│   └── wiki/                        ← ingest 產出（不手動改）
│       └── ...
│
knowledge/shared/                    ← 跨 Agent 共享（Phase 2.4）
├── user_123_summary.md
└── today_highlights.md
```

---

*使用 ark-superpowers 框架產出。*
