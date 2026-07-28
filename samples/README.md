# AI Workshop — 範例專案

> 兩個獨立可跑的完整專案，對應兩個課程。功能已對齊。

## 結構

```
samples/
├── ai-bot/            ← 課程 A 產出（個體 Agent）
└── ai-team-agent/     ← 課程 B 產出（Agent 團隊平台）
```

## 課程 A：個體 Agent

一個有靈魂的 AI Bot：SOUL + Skills + Wiki + Gemini 對話 + 自我成長。

```bash
cd ai-bot
pip install -r requirements.txt
cp .env.example .env
python start.py
```

| 能力 | 來自 |
|------|------|
| 有人格（SOUL.md） | 01 Agent 初始 |
| 有技能（5+ Skills） | 02 Skills 開發 |
| 有記憶（Wiki RAG + FTS5） | 03 LLM Wiki |
| 會成長（Skill 自動提案） | 04 自我成長 |

## 課程 B：Agent 團隊平台

8 Agent 並行的完整平台：PersistentDaemon + A2A + Memory + Wiki + Skills + Dashboard。

```bash
cd ai-team-agent
pip install -r requirements.txt
cp .env.example .env
cp team-ops.yaml team.yaml    # 或 team-dev.yaml
python start.py
```

| 配置 | 成員 | 場景 |
|------|------|------|
| 完整 8 人 | admin + leader + coder + qa + ai-dev + market + data + report | 全場景 |
| 研發團隊 | admin + leader + ai-dev + coder + qa | 開發+測試 |
| 營運團隊 | admin + leader + market + data + report | 市場+數據+報告 |

## 功能對比（已對齊 ✅）

| 功能 | ai-bot | ai-team-agent |
|------|--------|---------------|
| Agent 數量 | 8（Gemini dispatch 切換） | 8 並行常駐/動態 |
| src 架構 | 扁平模組（bot/agent/llm/wiki/memory） | 四層（gateway/coordinator/runtime/business） |
| 執行方式 | 單進程 Gemini Agent Loop + 按需 spawn CLI | PersistentDaemon 多進程 + MCP pipe |
| LLM 整合 | ✅ Gemini ReAct + FC + 多 Provider | kiro-cli（MCP stdio） |
| 派工機制 | Gemini 自行判斷 → dispatch_to_agent tool | leader-agent → MCP delegate_task → workers |
| 記憶系統 | ✅ FTS5 + daily_log + consolidate | ✅ FTS5 + daily_log + consolidate |
| 知識庫搜尋 | ✅ 四層（L0-L3） | ✅ 四層（L0-L3） |
| Skills 框架 | ✅ BaseSkill + Registry + Tracker | ✅ BaseSkill + Registry + Tracker |
| 自我成長 | ✅ GrowthDetector + TG 審批 | ✅ GrowthDetector + TG 審批 |
| Tier 分級啟動 | ✅ Tier 0-3 | ✅ Tier 0-4 |
| 團隊配置 | agents.yaml（角色定義） | team.yaml（進程 + 派工 + 排程） |
| EventBus | ❌ | ✅ async pub/sub + WebSocket |
| 可觀測性 | health API + memory API | ✅ 審計 + 費用 + 通知 + heartbeat |
| 熔斷器 | ❌ | ✅ Circuit Breaker |
| 部署 | python start.py | Docker Compose |
| Web UI | Jinja 6 頁 | Next.js + API |
| TG 指令 | /recall /skills /consolidate /mode | /recall /skills /consolidate /mode |
| **駕馭工程（.kiro/）** | ✅ 4 檔制 + Loop Skills | ✅ 5 檔制 + Loop Skills |
| **BRAIN.md** | ✅ 三層資源 + Output 策略 | ✅ 對齊（含品質護欄）|

## Tier 分級

### ai-bot（最高 Tier 3）

| Tier | 條件 | 能力 |
|------|------|------|
| 0 | 零設定 | Skills + Wiki + API |
| 1 | + TG Token | Bot + Inline Button |
| 2 | + Gemini Key | AI 對話 + RAG + L3 搜尋 |
| 3 | + kiro-cli | Agent 常駐 + 完整 .kiro/ |

### ai-team-agent（最高 Tier 4）

| Tier | 條件 | 能力 |
|------|------|------|
| 0 | 零設定 | Skills + Wiki + API |
| 1 | + TG Token | Bot + 通知 |
| 2 | + Gemini Key | AI 對話 + RAG |
| 3 | + kiro-cli | Agent 常駐 + MCP |
| 4 | + team.yaml | 團隊派工 + A2A + 排程 |

---

*兩個資料夾完全獨立，各自可跑。改 SOUL 改風格、改 knowledge/ 改知識、改 memory/ 改記憶、加 team.yaml 變團隊。*
