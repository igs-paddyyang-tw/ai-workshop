# 課程 A — AI Agent 開發入門

> 用 `samples/ai-bot` 體驗：說話 → 做事 → 記住（3 堂 × 50 min）

## 教學方式

```
啟動 samples/ai-bot → 動手操作 → 理解原理
```

## 文件

| 文件 | 用途 |
|------|------|
| [QUICKSTART-01-agent.md](QUICKSTART-01-agent.md) | 第一堂：切 Agent + 改 SOUL |
| [QUICKSTART-02-skills.md](QUICKSTART-02-skills.md) | 第二堂：拷問 + Spec + 驗證 |
| [QUICKSTART-03-wiki.md](QUICKSTART-03-wiki.md) | 第三堂：ingest + RAG |
| [build-guide.md](build-guide.md) | 課後：從零建構（Step 0-10） |
| [quickstart.html](quickstart.html) | 教材展示頁 |

## 三堂課體驗什麼

| 堂 | 主題 | 核心操作 |
|----|------|---------|
| 01 | 說話 | `/agents` 切 Agent → 改 SOUL.md → 觀察風格變化 |
| 02 | 做事 | 拷問設計 → Spec → 實作 Skill → Score ≥ 90 |
| 03 | 記住 | ingest → RAG 問答（有引用）→ 自演化循環 |

## 快速啟動

```bash
cd ../samples/ai-bot
pip install -r requirements.txt && cp .env.example .env
python start.py
```

## 素材

| 檔案 | 用途 |
|------|------|
| `soul-example.md` | SOUL 八段式範例 |
| `bot-responses.md` | Bot 回應範本 |
| `news-skill-guide.md` | 科技日報 Skill 實戰 |
| `sample-docs/` | Wiki 範例文件 3 篇 |

## 完成後

```
有人格（SOUL）+ 有技能（Spec-Driven）+ 有記憶（Wiki RAG）= 完整個體 Agent
```

→ 想升級為團隊？**[課程 B](../course-ai-team-agent/)**

---

*QUICKSTART = 上課體驗。build-guide = 課後建構。*
