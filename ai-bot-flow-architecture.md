# AI Bot 對話流程架構 — Workshop 教學文件

## 對話流程圖

```
使用者（Telegram）
    │ 發送文字訊息
    ▼
┌─────────────────────────────────────────────────────────┐
│ handle_message(update, context)                          │
│                                                         │
│  ① 即時回饋啟動                                          │
│     └─ 👀 Reaction + typing Timer（每 4 秒）            │
│                                                         │
│  ② ConversationPlanner.plan(text) — 六層路由             │
│     │                                                   │
│     ├─ L1: /reset → 🔄 重置                            │
│     ├─ L2: /skill_id args → Skill 直接執行              │
│     ├─ L3: keyword 命中 → Skill 執行                    │
│     │       「新聞」→ news_scraper                       │
│     │       「寫程式」→ llm_cli (codegen)                │
│     │       「echo」→ echo                              │
│     ├─ L4: keyword → 直達 team agent                    │
│     │       「測試/review」→ qa-agent                    │
│     │       「部署/docker」→ admin-agent                 │
│     ├─ L5: 深度關鍵字 → pm-agent 派工                   │
│     │       「規劃/分析/架構/重構/需求」                  │
│     └─ L6: 預設 → Gemini API 快速回答                   │
│                ↓ 失敗                                    │
│            → llm_cli CLI fallback                       │
│                                                         │
│  ③ 結案                                                 │
│     └─ ✅/❌ Reaction + 停止 Timer + 回覆結果           │
└─────────────────────────────────────────────────────────┘
```

## 三級回應速度

| 級別 | 觸發方式 | 後端 | 延遲 | 範例 |
|------|---------|------|------|------|
| ⚡ 即時 | keyword / /cmd / Gemini API | Python Skill / Gemini REST | 1-5s | 「Hi」「/echo」「今天新聞」 |
| 🔄 標準 | 一般問答（API 不可用時） | CLI subprocess（gemini/kiro/claude） | 5-30s | 「什麼是 RAG」 |
| 🧠 深度 | 深度關鍵字 / @mention agent | kiro-cli agents（multi-agent） | 30-120s | 「規劃新功能」「分析架構」 |

## Team Dispatch 觸發機制

```python
# 使用者說「規劃新功能」
text = "規劃新功能"

# Planner 偵測到深度關鍵字
_DEEP_KEYWORDS = ["規劃", "分析", "設計", "重構", "架構", ...]
# → PlanAction.TEAM_DISPATCH, agent_target="pm-agent"

# handlers.py 執行
agent = team_agents["pm-agent"]       # AgentProcess 物件
result = await agent.send(text)       # spawn kiro-cli

# kiro-cli 在 pm-agent workspace 執行
# cwd = ai-team-agent/agents/pm-agent/
# 讀取 .kiro/steering/SOUL.md（PM 角色定義）
# 可用 .kiro/skills/（8 個 Skills）
# 可存取 knowledge/（私有知識庫）
```

## 即時回饋機制

```
使用者發訊
 → [< 1 秒] 👀 Reaction（已收到）
 → [持續] typing...（每 4 秒刷新）
 → [完成]
   ├── 成功：👀 → ✅ + 回覆文字
   └── 失敗：👀 → ❌ + 錯誤摘要

特點：
• 無「收到！正在處理...」中間訊息
• typing 不斷線（Telegram 5 秒超時 → 4 秒重送）
• 結案後 Timer 自動 cancel（無資源洩漏）
```

## 檔案對應

| 功能 | 檔案 | 職責 |
|------|------|------|
| 入口 | `src/bot/main.py` | 建立 TG Application + 註冊 handlers |
| 路由 + 回覆 | `src/bot/handlers.py` | 即時回饋 + plan → 執行 → reply |
| 意圖路由 | `src/conversation/planner.py` | 六層路由邏輯（零 LLM 消耗） |
| Skill 系統 | `src/skills/registry.py` | auto_discover + invoke |
| Agent CLI | `src/skills/internal/llm_cli.py` | 多後端 CLI（Gemini/Kiro/Claude） |
| 快速路徑 | `src/llm/gemini_chat.py` | Gemini REST API 直連（2-3 秒） |
| 記憶 | `src/conversation/memory_search.py` | FTS5 跨 Session 搜尋 |
| 啟動 | `start_bot.py` | Skills + Team agents + Bot 初始化 |

---

## 與 ark-ai-bot-builder Skill 差異對照

### 相同部分（直接沿用）

| 模組 | 原版 | ai-bot | 差異 |
|------|------|--------|------|
| `base.py` | BaseSkill + SkillParam + SkillResult | ✅ 完全相同 | 無 |
| `registry.py` | auto_discover + invoke | ✅ 相同 | 移除 hot_reload（不需要） |
| `echo.py` | echo Skill | ✅ 相同 | 無 |
| Planner L1-L3 | /reset + /cmd + keyword | ✅ 相同邏輯 | 無 |
| `_QUICK_ROUTE` | news/code/echo | ✅ 相同 | 多加 `ping`, `codegen` keyword |
| `news_scraper.py` | httpx + BS4 抓取 | ✅ 相同模式 | 無 |
| `news_renderer.py` | HTML 模板渲染 | ✅ 相同模式 | 無 |

### 改進部分

| 模組 | 原版 | ai-bot | 為什麼改 |
|------|------|--------|---------|
| `llm_cli.py` | 有 evaluate + skill_gen mode | 只保留 chat + codegen | evaluate 用 Planner 取代；skill_gen 由 team ai-dev 負責 |
| `llm_cli.py` | `_clean_output` 分散各 mode | 統一 `_clean()` + `_TOOL_LOG_RE` | 集中維護 |
| `handlers.py` | 發「🤖 思考中...」等待訊息 | 👀 + typing 零訊息 | 不刷屏 |
| `handlers.py` | `wait_msg.edit_text()` 編輯回覆 | 直接 `msg.reply_text()` | 更簡潔、不需追蹤 message_id |
| `PlanAction` | EXECUTE / ANSWER / RESET | 新增 **TEAM_DISPATCH** | 支援 multi-agent |
| init_components | 只注入 registry | 注入 registry + **team_agents** | 支援 team dispatch |

### 新增部分（原版沒有）

| 功能 | 原版 | ai-bot | 設計理由 |
|------|------|--------|---------|
| `PlanAction.TEAM_DISPATCH` | ❌ | ✅ | 複雜任務派給 multi-agent |
| `_TEAM_QUICK_ROUTE` | ❌ | ✅ | 特定 keyword 直達指定 agent |
| `_DEEP_KEYWORDS` | ❌ | ✅ | 偵測深度任務自動升級 |
| `gemini_chat.py` | ❌ | ✅ | API 直連快速路徑（2-3s） |
| 即時回饋 👀/✅/❌ | ❌ | ✅ | TG 原生 Reaction 狀態可見 |
| typing Timer | ❌ | ✅ | 處理中狀態不斷線 |
| `memory_search.py` | 原版有但未整合 | ✅ 獨立可用 | FTS5 跨 Session |
| ANSI strip | ❌ | ✅ `_ANSI_RE` | kiro-cli 帶色碼 |
| 工具日誌過濾 | ❌ | ✅ `_TOOL_LOG_RE` | 過濾 web_search 等中間輸出 |
| 4000 字分段 | 截斷 + 「📎 已截斷」 | 分段完整發送 | 不丟資訊 |
| `start_bot.py` auto team | ❌ | ✅ 偵測 team.yaml | 有 team 就連，沒有也能獨立跑 |

### 移除部分

| 原版有 | ai-bot 移除 | 理由 |
|--------|------------|------|
| `evaluate` mode | ❌ | Planner 六層路由零 token 取代 |
| `skill_gen` mode | ❌ | 由 team ai-dev-agent 負責 |
| `hot_reload` | ❌ | production 重啟即可 |
| `/daily` 指令 | ❌ | keyword 路由「日報」自動觸發 |
| 6 階段漸進式產出 | ❌ | 一次到位 |
| `cmd_daily` handler | ❌ | Planner 自動路由到 news_scraper |

---

## 結論

```
原版 ark-ai-bot-builder = 單 Agent Bot（CLI 為大腦）
                        ↓ 升級
新版 ai-bot            = 三級回應 Bot
                         ⚡ Gemini API（秒回）
                         🔄 CLI subprocess（標準）
                         🧠 Multi-Agent team（深度）
```

核心差異只有一個：**加入 TEAM_DISPATCH 層**。其餘都是 UX 改善（即時回饋、output 清洗、分段發送）。
