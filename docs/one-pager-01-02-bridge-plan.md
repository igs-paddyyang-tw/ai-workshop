---
title: "Workshop 01→02 銜接重構計畫 — 單兵升級為團隊"
type: onepager
status: draft
language: zh-TW
created: 2026-07-01
author: paddyyang
tags: [ai-workshop, bridge, restructure, 01-to-02]
---

# Workshop 01→02 銜接重構計畫 — 單兵升級為團隊

## 問題

01 和 02 之間存在三個斷層：

1. **難度斷崖**：01 花 6 步手把手建一個 Bot，02 一步 `build_team.py` 產出 16 模組平台，學員看不到中間的「為什麼要升級」
2. **產出不複用**：01 的 `my-bot` 在 02 完全被丟棄，學員感覺白做了
3. **概念不連續**：01 教「一個 Agent 怎麼思考」，02 跳到「五個 Agent 怎麼協作」，中間缺少「一個不夠，需要多個」的動機建立

加上先前分析的整體改善建議（03→04 脫鉤、04→05 缺實際串接、日報案例重複但技術路徑不相容），需要一併處理。

## 目標

- 01 的產出（my-bot）成為 02 的「一個 Agent」被整合進團隊
- 學員在 01 結尾自然感受到「單兵瓶頸」→ 產生「需要團隊」的動機
- 「科技日報」作為貫穿 01→05 的持續案例，技術路徑逐步升級
- 03、04、05 各有一個 hands-on 步驟引用前堂產出

## 非目標

- 不重寫 01 或 02 的核心內容（改善是加橋接，不是重建）
- 不改動 build_team.py / build_kiro.py 的 script 邏輯
- 不改動五層架構的教學設計

## 方案

### A. 01 結尾加「瓶頸體驗 + 升級預告」(新增 Step 7)

在 01 完成 Step 6（科技日報）後，加一個 Step 7 讓學員親身體驗單兵限制：

```
Step 7: 🚧 單兵瓶頸體驗（5 分鐘）
─────────────────────────────────
📱 在 TG 同時問 Bot：
  「幫我查今天新聞」+「翻譯這段英文」+「寫一個 Python 腳本」

觀察：Bot 只能一個一個處理（序列阻塞）。
如果爬蟲失敗？整個 Bot 卡住。
如果要加新能力？修改 planner.py + 重啟。

⚠️ 這就是「單兵模式」的天花板。
🔜 下一堂（02）：5 個 Agent 並行 → 10 秒完成你的 3 個需求。
```

### B. 02 開頭加「01 對照表」(新增 Section)

在 02 的 build guide Step 1 之前，加一個對照表：

```markdown
## 你的 my-bot 在團隊裡變成了什麼？

| 01 你手動做的 | 02 在哪裡 | 進化了什麼 |
|--------------|----------|-----------|
| `src/skills/` BaseSkill | `src/runtime/` SkillRegistry | 5 個 Agent 各有獨立 Skills |
| `src/bot/planner.py` 意圖路由 | `src/coordinator/` TaskGraph | 不只路由，還能拆子任務 + 並行 |
| `src/bot/handlers.py` 指令 | `src/gateway/telegram.py` | 多 Agent 路由（@mention / topic） |
| `src/llm/gemini_chat.py` | 每個 agent 的 kiro-cli 後端 | 每個 Agent 有獨立 LLM session |
| `src/workflow/engine.py` 排程 | `scheduler.yaml` + 排程引擎 | 可排程派工到不同 Agent |
| 01 的「科技日報」全流程 | market-agent + report-agent 分工 | 爬蟲/分析/渲染各 Agent 專責 |
```

### C. 統一「科技日報」為貫穿案例

讓日報成為 5 堂課都在做的同一件事，但技術逐步升級：

| Workshop | 日報的技術實現 | 升級了什麼 |
|----------|---------------|-----------|
| 01 | 手動寫爬蟲 + Gemini CLI → HTML | 單兵全做 |
| 02 | market 爬 + report 渲染 → TG 推送 | 分工並行 |
| 03 | 透過 API `/api/v1/workflows/run` 觸發 | 理解 API 化 |
| 04 | 用 Spec-Driven 重構 news_scraper Skill | 品質把關 |
| 05 | 日報結果 ingest → Wiki → 趨勢知識庫 | 知識沉澱 |

### D. 03 加「程式碼閱讀」hands-on

在 03 的 Step 3（A2A 協作機制）加一個子步驟：

```markdown
### 3.5 打開程式碼看 TaskGraph

💻 打開 `src/coordinator/task_graph.py`：
  - 找到 `resolve_dependencies()` 方法
  - 這就是「02 Step 5 你派工時，leader 背後在做的事」

💻 打開 `src/coordinator/discovery.py`：
  - 找到 `match_agent()` 方法
  - 這就是「leader 怎麼決定派給誰」
```

### E. 04 範例改用 my-team 裡的 news Skill

把 04 的「每日科技新聞日報 Skill」拷問場景設定在 `my-team` 專案中：

```markdown
## 前置：使用你的 my-team 專案

cd my-team
# 我們要用 Spec-Driven 方式「重構」market-agent 的新聞爬蟲 Skill

📝 輸入：
「拷問我的設計：重構 market-agent 的 news_scraper Skill，
 改善 01 的簡單爬蟲，加入多來源併發 + 失敗重試 + 結構化輸出」
```

### F. 05 的 ingest 步驟用 04 產出

把 05 Step 4 的 sample-docs 改為「04 驗證通過的 Skill spec + 日報歷史」：

```markdown
### 4.2 匯入你的真實知識

💻 匯入 04 產出的 Spec（如果有的話）：
cp my-team/docs/specs/news-scraper-spec.md knowledge/my-wiki-bot/raw/

💻 匯入歷史日報：
cp my-team/agents/market-agent/output/*.md knowledge/my-wiki-bot/raw/

📝 然後在 Chat 輸入：「匯入 raw 資料夾的文件到 Wiki」
```

> 保留 sample-docs/ 作為 fallback（學員沒做 04 時仍可獨立操作）。

## 執行步驟

| # | 任務 | 影響範圍 | 工時 |
|---|------|---------|------|
| 1 | 01 build-guide 加 Step 7（瓶頸體驗） | `01-agent-workshop/ai-bot-build-guide.md` | 20 min |
| 2 | 01 QUICKSTART 結尾加「下堂預告」 | `01-agent-workshop/QUICKSTART.md` | 10 min |
| 3 | 02 build-guide 加「01 對照表」section | `04-agent-team-workshop/agent-team-build-guide.md` | 20 min |
| 4 | 02 QUICKSTART 開頭加「01→02 升級說明」 | `04-agent-team-workshop/QUICKSTART.md` | 10 min |
| 5 | 03 build-guide Step 3 加程式碼閱讀 | `05-platform-workshop/platform-build-guide.md` | 15 min |
| 6 | 04 build-guide 前置改用 my-team | `02-skills-workshop/skills-build-guide.md` | 20 min |
| 7 | 05 build-guide Step 4 加 04 產出匯入 | `03-llm-wiki-workshop/llm-wiki-build-guide.md` | 15 min |
| 8 | README.md 更新「科技日報」貫穿說明 | `README.md` | 15 min |
| 9 | 新增 `shared/bridge-diagram.md` 視覺化 | `shared/bridge-diagram.md` | 20 min |
| **合計** | | | **~2.5 hr** |

## 實施優先順序

```
Phase 1（最高優先 — 解決核心斷層）
├── 任務 1: 01 加 Step 7
├── 任務 3: 02 加對照表
└── 任務 8: README 科技日報貫穿

Phase 2（中優先 — 前後呼應）
├── 任務 5: 03 加程式碼閱讀
├── 任務 6: 04 改用 my-team
└── 任務 7: 05 加真實匯入

Phase 3（收尾 — 細節潤飾）
├── 任務 2: 01 QUICKSTART 預告
├── 任務 4: 02 QUICKSTART 升級說明
└── 任務 9: bridge-diagram 視覺化
```

## 驗收條件

- [ ] 01 結尾有明確的「瓶頸→升級」過渡，學員知道為什麼需要 02
- [ ] 02 開頭有對照表，學員看得到「01 的東西在 02 哪裡」
- [ ] 「科技日報」在 01-05 是同一條線的逐步升級（README 有說明）
- [ ] 03 有至少一個「打開程式碼」的 hands-on 步驟
- [ ] 04 的拷問範例可在 my-team 中執行（不強制，保留獨立性）
- [ ] 05 有路徑匯入 04 產出（保留 sample-docs fallback）
- [ ] 所有修改不破壞各 Workshop 的獨立可用性（可跳堂）

## 風險

| 風險 | 機率 | 影響 | 緩解 |
|------|------|------|------|
| 加了銜接卻增加 50 min 時間壓力 | 中 | 講不完 | Step 7 和對照表設計為可跳過（標「選讀」） |
| 04/05 依賴前堂產出，跳堂學員卡住 | 中 | 體驗差 | 保留 fallback 路徑（sample-docs 仍可用） |
| README 科技日報線太長，新人看不懂 | 低 | 困惑 | 用簡潔表格 + 視覺流程圖，不寫長文 |
| 改動太多，跟 instructor teaching-guide 脫節 | 中 | 教學矛盾 | Phase 1 完成後更新 teaching-guide |

## 成功指標

| 指標 | 目前 | 目標 |
|------|------|------|
| 01→02 的「為什麼升級」可理解度 | 無過渡 | 學員在 01 結尾自然說出「需要多個 Agent」 |
| 01 產出在 02 的可見度 | 0%（完全丟棄） | 對照表覆蓋 6 個以上對應點 |
| 科技日報技術路徑一致性 | 01/02 用不同路徑 | 明確標注為「同案例的升級版」 |
| 各堂可獨立運行 | ✅ | ✅（不破壞） |

---

*使用 ark-superpowers 框架產出 ｜ 2026-07-01*
