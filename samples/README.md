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

5 Agent 並行的完整平台：CoreDaemon + A2A + Memory + Wiki + Skills + Dashboard。

```bash
cd ai-team-agent
pip install -r requirements.txt
cp .env.example .env
cp team-ops.yaml team.yaml    # 或 team-dev.yaml
python start.py
```

| 配置 | 成員 | 場景 |
|------|------|------|
| 營運團隊 | admin + pm + market + data + report | 市場+數據+報告 |
| 研發團隊 | admin + pm + ai-dev + coder + qa | 開發+測試 |

## 功能對比（已對齊 ✅）

| 功能 | ai-bot | ai-team-agent |
|------|--------|---------------|
| Agent 數量 | 8（切換） | 5 並行常駐 |
| 執行方式 | 單進程 | CoreDaemon 多進程 |
| Runtime | kiro-cli | 多 Provider（kiro/claude/codex）+ fallback |
| 記憶系統 | ✅ FTS5 + daily_log + consolidate | ✅ FTS5 + daily_log + consolidate |
| 知識庫搜尋 | ✅ 四層（L0-L3） | ✅ 四層（L0-L3） |
| Skills 框架 | ✅ BaseSkill + Registry + Tracker | ✅ BaseSkill + Registry + Tracker |
| 自我成長 | ✅ GrowthDetector + TG 審批 | ✅ GrowthDetector + TG 審批 |
| Tier 分級啟動 | ✅ Tier 0-4 | ✅ Tier 0-4 |
| 派工 | team.yaml 選配 | ✅ /assign + TaskGraph + 狀態機 |
| EventBus | ❌ | ✅ async pub/sub + WebSocket |
| 可觀測性 | health API | ✅ 審計 + 費用 + 通知 |
| 熔斷器 | ❌ | ✅ Circuit Breaker |
| 部署 | python start.py | Docker Compose |
| Web UI | Jinja 6 頁 | Next.js + API |
| TG 指令 | /recall /skills /consolidate /mode | /recall /skills /consolidate /mode |

## Tier 分級（兩專案共用概念）

| Tier | 條件 | 能力 |
|------|------|------|
| 0 | 零設定 | Skills + Wiki + API |
| 1 | + TG Token | Bot + Inline Button |
| 2 | + Gemini Key | AI 對話 + RAG + L3 搜尋 |
| 3 | + kiro-cli | Agent 常駐 |
| 4 | + team.yaml | 團隊派工 + A2A |

---

*兩個資料夾完全獨立，各自可跑。改 SOUL 改風格、改 knowledge/ 改知識、改 memory/ 改記憶、加 team.yaml 變團隊。*
