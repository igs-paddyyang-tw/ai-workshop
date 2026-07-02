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
cd ai-workshop/sample/ai-bot
pip install -r requirements.txt && cp .env.example .env
python start.py
```

| Phase | sample 中對應 |
|-------|-------------|
| 1 Agent | `src/agent/` + `.kiro/steering/SOUL.md` + `src/bot/` |
| 2 Skills | `src/skills/` + `agents/*/skills/ark-*/SKILL.md` |
| 3 Wiki | `src/wiki/` + `knowledge/` |

---

## 建置步驟總覽

```
── Phase 1：Agent 初始（第一堂）─────────────────
Step 0: 環境準備 + Skills 取得
Step 1: ark-agent-builder → 完整專案骨架
Step 2: ark-kiro-init --standalone → .kiro/ 配置
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
| 1 | `ark-agent-builder` + `ark-kiro-init` | Bot 有靈魂 |
| 2 | `ark-grill-me` + `ark-superpowers` + `ark-code-spec-validator` | Skill 有品質 |
| 3 | `ark-wiki-engine` | 知識會成長 |

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

## Step 1：一鍵建構專案（ark-agent-builder）

💻 執行：

```bash
python3 .kiro/skills/ark-agent-builder/scripts/build_agent.py my-agent
```

產出完整專案：
```
my-agent/
├── src/agent/       ← cli + session + memory + planner
├── src/bot/         ← Inline Button + handlers
├── src/skills/      ← 5 內建 Skills
├── src/wiki/        ← WikiEngine
├── src/llm/         ← Gemini Chat
├── src/server/      ← FastAPI
├── agents/          ← 8 Agent 預設配置
├── config/          ← news_sources + llm_prompts
├── knowledge/       ← Wiki 知識庫結構
└── start.py
```

## Step 2：初始化 Agent 配置（ark-kiro-init）

💻 執行：

```bash
python3 .kiro/skills/ark-kiro-init/scripts/build_kiro.py --standalone my-agent --name "我的助手"
```

產出 `.kiro/`：
```
my-agent/.kiro/
├── steering/SOUL.md     ← 下一步要修改
├── steering/KIRO.md
├── steering/MEMORY.md
├── steering/USER.md
├── settings/mcp.json
├── agents/我的助手.json
└── prompts/route-message.md
```

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
agents/market-agent/skills/ark-news-scraper/
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

💻 把文件放入 `knowledge/raw/`：

```bash
# 範例文件已在 sample-docs/
cp sample-docs/*.md my-agent/knowledge/raw/
```

觸發 ingest：

```bash
curl -X POST http://localhost:8000/api/v1/wiki/ingest
```

或 📱 Telegram 輸入：「匯入知識」

結果：`knowledge/wiki/` 出現結構化頁面（含 frontmatter）。

## Step 9：RAG 問答

📱 Telegram 輸入：

```
什麼是 asyncio？
```

Agent 會：
1. 搜尋 `knowledge/wiki/` 匹配頁面
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
Agent 完成任務 → memory.py 寫入 knowledge/raw/
    → 定期 ingest → knowledge/wiki/ 成長
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
| 有品質的 Skills | 2 | `agents/*/skills/ark-*/SKILL.md` |
| 有記憶（Memory） | 1+3 | `src/agent/memory.py` + `knowledge/` |
| 有知識（Wiki RAG） | 3 | `src/wiki/engine.py` |
| 自演化（ingest） | 3 | `raw/ → wiki/` 循環 |

## 下一步：課程 B

想從一個人變一個團隊？→ `course-b/`

```
課程 B 解決：
- 5 Agent 真正並行（CoreDaemon）
- A2A 通訊（delegate_task）
- 費用控管 + Dashboard
- Docker 部署
```

---

## 技術棧

| 層 | 技術 |
|----|------|
| Bot | python-telegram-bot 21+（Inline Button） |
| LLM | Gemini API（httpx + system_prompt） |
| Agent CLI | kiro-cli subprocess（.kiro/ 全生效） |
| Skills | BaseSkill + SkillRegistry + SKILL.md |
| Wiki | WikiEngine（query + ingest + lint） |
| Session | SessionManager（per user_id + 10 輪歷史） |
| Memory | save_memory → knowledge/raw/ |
| Server | FastAPI |
| 意圖路由 | Planner（三層降級） |

---

## 快速複製

```bash
# 一鍵完成 Phase 1
python3 .kiro/skills/ark-agent-builder/scripts/build_agent.py my-agent
python3 .kiro/skills/ark-kiro-init/scripts/build_kiro.py --standalone my-agent

# 設定 + 啟動
cd my-agent && cp .env.example .env
pip install -r requirements.txt
python start.py
```

---

*一個專案，三堂課，完整的個體 Agent。*
