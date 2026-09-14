---
title: "課程 A — 個體 Agent 建置完整指南"
type: guide
created: 2026-07-02
language: zh-TW
---

# 課程 A — 個體 Agent 建置完整指南

> 一個專案，三堂課（Phase 1-3），Step 0-10。
> 從零到「有人格 + 有技能 + 有記憶」的完整 Agent。

**操作位置圖示：**
- 📝 = AI IDE 聊天框（Kiro CLI / Cursor）
- 📱 = Telegram Bot 對話
- 💻 = 終端機

---

## ✅ 先體驗成品？

```bash
cd ai-workshop/samples/ai-bot
python3 -m venv .venv && source .venv/bin/activate
pip install './ark_bot_agent-<版本>-py3-none-any.whl[search,skills]'
cp .env.example .env       # 填你自己的 TELEGRAM_BOT_TOKEN
python start.py
```

| Phase | sample 中對應 |
|-------|-------------|
| 1 Agent | `agents.yaml` + `bot.yaml` + `.kiro/steering/SOUL.md` |
| 2 Skills | `agents/*/.kiro/skills/ark-*/SKILL.md` |
| 3 Wiki | `knowledge/shared/`（wiki / raw / schema / index / log） |

> 🔴 **這個專案裡沒有 runtime 程式碼。** TG polling / Web UI / 記憶 / 四層搜尋
> 都在 `ark_bot_agent` wheel 裡。你維護的是**設定與人格**。

---

## 建置步驟總覽

```
── Phase 1：Agent 初始（第一堂）─────────────────
Step 0: 環境準備 + Skills 取得
Step 1: 裝 ark_bot_agent wheel（ark-agent-bot-builder 產骨架）
Step 2: ark-agent-init → .kiro/steering 人格 + 多 CLI 入口
Step 3: SOUL.md 八段式設計 ⭐

── Phase 2：Skills 開發（第二堂）─────────────────
Step 4: 拷問設計（ark-grill-me）
Step 5: 產出 Spec（ark-superpowers）
Step 6: 實作 Skill（ark-skill-creator）
Step 7: 驗證 Code ↔ Spec（ark-code-spec-validator）

── Phase 3：知識庫（第三堂）─────────────────────
Step 8: 匯入知識（Ingest）
Step 9: RAG 問答
Step 10: Wiki 健康檢查 + 圖譜
```

| Phase | 核心 Skills | 學什麼 |
|-------|-----------|--------|
| 1 | `ark-agent-bot-builder` + `ark-agent-init` | Bot 有靈魂 |
| 2 | `ark-grill-me` + `ark-superpowers` + `ark-code-spec-validator` | Skill 有品質 |
| 3 | `ark-wiki-engine` | 知識會成長 |

> 💡 **三層分工**：① builder 定架構（裝 wheel + 設定檔）→ ② agent-init 給人格
> → ③ skill 給工具。三者各管一層，不重疊。

---

# Phase 1：Agent 初始（第一堂）

> 目標：Bot 能回話、有人格、有意圖路由。

## Step 0：環境準備

```bash
git clone https://github.com/igs-paddyyang-tw/ark-agent-skills .kiro/skills/
```

| 項目 | 最低需求 |
|------|---------|
| Python | 3.12+ |
| Git | 已安裝 |
| Telegram Bot Token | @BotFather 取得 |
| Gemini API Key | https://aistudio.google.com/apikeys（免費） |

## Step 1：產骨架 + 裝套件（ark-agent-bot-builder）

📝 Kiro IDE 輸入：

```
用 ark-agent-bot-builder 幫我建一個 bot workspace：my-agent
```

它產出的是**設定骨架**，不是架構：

```
my-agent/
├── start.py          ← 一行 run_bot()
├── agents.yaml       ← 有誰（專案根哨兵）
├── bot.yaml          ← 怎麼跑
├── .env              ← 機密
├── requirements.txt  ← 只列 wheel
├── knowledge/shared/{wiki,raw}/   ← 🔴 Wiki 引擎讀這層
├── memory/daily/                  ← 🔴 套件記憶落點
├── artifacts/reports/             ← 🔴 產出落點
└── agents/<name>-agent/
```

💻 裝套件：

```bash
cd my-agent
python3 -m venv .venv && source .venv/bin/activate
pip install './ark_bot_agent-<版本>-py3-none-any.whl[search,skills]'
python -c "import ark_bot_agent; print(ark_bot_agent.__version__)"   # 驗版號
```

> 🔴 **extras 不可省**，也 **不要看 pip 輸出判斷有沒有裝到** —— 驗 import。

## Step 2：補上人格與多 CLI 入口（ark-agent-init）

📝 Kiro IDE 輸入：

```
用 ark-agent-init 為 my-agent 的 manager 與各 agent 產 .kiro/steering 人格
```

產出：
```
my-agent/.kiro/
├── steering/SOUL.md     ← 下一步要修改（本堂核心）
├── steering/AGENTS.md   ← 全域規範（多 CLI 共用 SSOT）
├── steering/CODE.md     ← 程式碼規範
├── steering/MEMORY.md
├── steering/USER.md
├── settings/mcp.json
└── prompts/route-message.md
```

> 💡 **多 CLI 共用**：`AGENTS.md` 是單一真相來源，`CLAUDE.md` 連結過去。
> 不同 CLI 讀不同檔名（Kiro 讀 `.kiro/steering/`、Claude Code 讀 `CLAUDE.md`、
> Codex / Cursor 讀 `AGENTS.md`）—— 各自維護三份必漂移。

## Step 3：系統提詞設計（SOUL.md）⭐ 本堂核心

> SOUL.md 決定了 Agent「是誰」。

### 八段式格式

編輯 `my-agent/.kiro/steering/SOUL.md`：

```markdown
## 身份      — 我是誰
## 人格      — 我的性格特質
## 能力      — 我能做什麼
## 邊界      — 我不做什麼
## 工作流程   — 收到訊息怎麼處理
## 輸出格式   — 回覆的風格
## 成長規則   — 如何更新知識
## 禁制      — 絕對不可做的事
```

### 驗證

```bash
cd my-agent && pip install -r requirements.txt
cp .env.example .env  # 填入 TELEGRAM_BOT_TOKEN + GEMINI_API_KEY
python start.py
```

📱 Telegram：
- `/start` → 看到歡迎訊息（受 SOUL 影響）
- `/agents` → Inline Button 選 Agent
- 直接打字 → AI 對話（SOUL 風格）
- `/mode` → 查看執行模式

> 🎉 Phase 1 完成！Agent 有了靈魂。

---

# Phase 2：Skills 開發（第二堂）

> 目標：用 Spec-Driven 方式開發新 Skill，有品質保障。

## Step 4：拷問設計（ark-grill-me）

📝 在 Kiro 聊天框輸入：

```
拷問我的設計：重構 market-agent 的新聞爬蟲 Skill，
加入多來源併發 + 失敗重試 + 結構化 JSON 輸出
```

AI 會一次問一個問題（8-15 題），你回答後產出「決策摘要」。

### 重點

- 主動參與，不要被動 OK
- 質疑推薦答案
- 太細的說「之後再決定」

## Step 5：產出 Spec（ark-superpowers）

📝 拿到決策摘要後：

```
根據以上決策摘要，幫我寫 spec
```

產出 `docs/specs/news-scraper-spec.md`，包含目標、需求、驗收條件。

## Step 6：實作 Skill（ark-skill-creator）

📝 輸入：

```
建立新 Skill：科技新聞爬蟲，根據 docs/specs/news-scraper-spec.md 實作
```

產出：
```
agents/market-agent/.kiro/skills/ark-news-scraper/
├── SKILL.md          ← Ark Skill 格式
├── scripts/          ← 可執行程式碼（選配）
└── references/       ← 參考文件（選配）
```

## Step 7：驗證 Code ↔ Spec（ark-code-spec-validator）

📝 輸入：

```
驗證 code 跟 spec 一致嗎
```

產出 Drift Report（4 維度 × 0-100 評分）：
- ✅ ≥ 90：可 Ship
- ⚠️ 70-89：修復後再驗
- ❌ < 70：重新對齊

> 🎉 Phase 2 完成！Skill 有了品質保障。

---

# Phase 3：知識庫（第三堂）

> 目標：Agent 有長期記憶，能 RAG 問答，知識會成長。

## Step 8：匯入知識（Ingest）

💻 把文件放入 `knowledge/shared/raw/`：

```bash
# 範例文件已在 sample-docs/
cp sample-docs/*.md my-agent/knowledge/shared/raw/
```

觸發 ingest：

```bash
curl -X POST http://localhost:8000/api/v1/wiki/ingest
```

或 📱 Telegram 輸入：「匯入知識」

結果：`knowledge/shared/wiki/` 出現結構化頁面（含 frontmatter）。

## Step 9：RAG 問答

📱 Telegram 輸入：

```
什麼是 asyncio？
```

Agent 會：
1. 搜尋 `knowledge/shared/wiki/` 匹配頁面
2. 注入 Gemini 作為 context
3. 回答 + 附來源引用 `📚 參考：[[python-async-guide]]`

## Step 10：Wiki 健康檢查 + 圖譜

💻 Lint 檢查：

```bash
curl http://localhost:8000/api/v1/wiki/lint
```

回報：
- ⚠️ 缺失 frontmatter
- 🔗 斷裂的 `[[wikilink]]`
- 🏝️ 孤立頁面

### 自演化循環

```
Agent 完成任務 → memory.py 寫入 knowledge/shared/raw/
    → 定期 ingest → knowledge/shared/wiki/ 成長
    → RAG 問答品質提升 → Agent 越用越聰明
```

> 🎉 Phase 3 完成！Agent 有了長期記憶。

---

# 完成！你的 Agent 現在具備

| 能力 | 來自 Phase | 對應模組 |
|------|-----------|---------|
| 有人格（SOUL） | 1 | `.kiro/steering/SOUL.md` |
| 有對話（Gemini） | 1 | `src/llm/gemini_chat.py` |
| 有路由（Planner） | 1 | `src/agent/planner.py` |
| 8 Agent 可切換 | 1 | `agents/` + Inline Button |
| 有品質的 Skills | 2 | `agents/*/.kiro/skills/ark-*/SKILL.md` |
| 有記憶（Memory） | 1+3 | `src/agent/memory.py` + `knowledge/` |
| 有知識（Wiki RAG） | 3 | `src/wiki/engine.py` |
| 自演化（ingest） | 3 | `raw/ → wiki/` 循環 |

## 下一步：課程 B

想從一個人變一個團隊？→ `course-ai-team-agent/`

```
課程 B 解決：
- 5 Agent 真正並行（CoreDaemon）
- A2A 通訊（delegate_task）
- 費用控管 + Dashboard
- Docker 部署
```

---

## 技術棧 —— 你維護的 vs 套件提供的

| 能力 | 在哪 | 你要碰嗎 |
|------|------|---------|
| TG Bot（polling + Inline Button） | `ark_bot_agent` | ❌ |
| Web Chat / REST API / `/admin` | `ark_bot_agent` | ❌ |
| 三模式路由（chat / agent / team） | `ark_bot_agent` | 只在 `bot.yaml` 選 |
| Gemini ReAct（chat 模式） | `ark_bot_agent` | 只在 `bot.yaml` 設模型 |
| CLI backend（kiro / claude） | `ark_bot_agent` | 只在 `bot.yaml` 選 |
| 知識庫四層搜尋 + ingest + lint | `ark_bot_agent` + `ark-wiki-engine` | 放素材、下指令 |
| 記憶（daily / recent / consolidate） | `ark_bot_agent` | ❌ |
| 12 個內建 skill | `ark_bot_agent` | ❌ |
| **有誰** | `agents.yaml` | ✅ |
| **怎麼跑** | `bot.yaml` | ✅ |
| **是誰** | `.kiro/steering/SOUL.md` | ✅✅ 本課重點 |
| **知道什麼** | `knowledge/shared/` | ✅ |

> 💡 這張表就是套件化的意義：以前這些全部要自己寫（約 2 萬行），
> 現在只剩右欄四個打勾的要維護。

---

## 快速複製

```bash
# Phase 1：骨架 → 套件 → 人格
#   ① 在 Kiro 說「用 ark-agent-bot-builder 建 my-agent」
#   ② 裝 wheel：
cd my-agent
python3 -m venv .venv && source .venv/bin/activate
pip install './ark_bot_agent-<版本>-py3-none-any.whl[search,skills]'
#   ③ 在 Kiro 說「用 ark-agent-init 產 my-agent 的 steering 人格」

# 設定 + 啟動
cp .env.example .env      # 填你自己的 TELEGRAM_BOT_TOKEN
python start.py
```

---

*一個專案，三堂課，完整的個體 Agent。*
