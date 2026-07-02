# 課程 A — AI Agent 開發入門

> 一個專案，三堂課：說話 → 做事 → 記住（共 2.5 小時）

## 文件結構

| 文件 | 用途 |
|------|------|
| **[build-guide.md](build-guide.md)** | 完整規格（Phase 1-3，Step 0-10） |
| [QUICKSTART-01-agent.md](QUICKSTART-01-agent.md) | 第一堂 50 min（Bot + SOUL） |
| [QUICKSTART-02-skills.md](QUICKSTART-02-skills.md) | 第二堂 50 min（Spec-Driven） |
| [QUICKSTART-03-wiki.md](QUICKSTART-03-wiki.md) | 第三堂 50 min（Wiki RAG） |

## 三堂課一覽

| Phase | 主題 | 核心 Skill | 產出 |
|-------|------|-----------|------|
| 1 | Agent 初始 | `ark-agent-builder` + `ark-kiro-init` | Bot 有靈魂 |
| 2 | Skills 開發 | `ark-grill-me` + `ark-superpowers` + `ark-code-spec-validator` | Skill 有品質 |
| 3 | LLM Wiki | `ark-wiki-engine` | 知識會成長 |

## 快速開始

```bash
# 直接體驗成品
cd ../sample/a-agent && pip install -r requirements.txt && python start.py

# 從零建構
cd ../sample/a-agent  # 參考結構
cat build-guide.md    # 跟著 Step 0-10 做
```

## 素材

| 檔案 | 用途 |
|------|------|
| `soul-example.md` | SOUL 八段式範例（Phase 1） |
| `bot-responses.md` | Bot 回應範本（Phase 1） |
| `news-skill-guide.md` | 科技日報 Skill 實戰（Phase 2） |
| `structured-example.json` | Mock 資料（Phase 2） |
| `sample-docs/` | Wiki 範例文件 3 篇（Phase 3） |

## 完成後你有

```
說話（SOUL + Planner + Gemini）
  + 做事（Spec-Driven Skills）
  + 記住（Wiki RAG + Memory）
  = 完整的個體 Agent
```

## 想繼續？

→ **[課程 B — AI Agent Team 實戰](../course-b/)**

---

*課程 A = 個體能力。課程 B = 團隊協作。*
