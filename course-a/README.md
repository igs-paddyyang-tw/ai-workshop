# 課程 A — AI Agent 開發入門

> 打造你的第一個智能助手：說話 → 做事 → 記住（3 堂，共 2.5 小時）

## 你會學到

```
01 它能「說話」    系統提詞 + 意圖路由 + Bot 啟動
02 它能「做事」    Spec-Driven Skill 開發迴圈
03 它能「記住」    RAG 問答 + 知識庫 + 自演化
```

## 課程總覽

| # | Workshop | 時長 | 核心 Skill | 產出 |
|---|----------|------|-----------|------|
| 01 | [Agent 初始](01-agent-workshop/) | 50 min | `ark-agent-builder` | 有人格的 Telegram Bot |
| 02 | [Skills 開發](02-skills-workshop/) | 50 min | `ark-grill-me` + `ark-superpowers` + `ark-code-spec-validator` | 可驗證的 Skill |
| 03 | [LLM Wiki](03-llm-wiki-workshop/) | 50 min | `ark-wiki-engine` | RAG 知識庫系統 |

## 使用的 Skills（7 個）

| Skill | 用途 | 堂次 |
|-------|------|------|
| `ark-agent-builder` | 一鍵建構 Bot 專案 | 01 |
| `ark-env-doctor` | 環境檢查 | 01 |
| `ark-grill-me` | 拷問設計（釐清需求） | 02 |
| `ark-superpowers` | 產出 Spec 文件 | 02 |
| `ark-skill-creator` | 建立新 Skill | 02 |
| `ark-code-spec-validator` | 驗證 Code ↔ Spec | 02 |
| `ark-wiki-engine` | Wiki 知識庫系統 | 03 |

## 前置條件

- Python 3.12+
- Git
- Telegram 帳號 + Bot Token
- Gemini API Key（免費）

## 快速開始

```bash
# 取得 Skills
git clone https://github.com/igs-paddyyang-tw/ark-agent-skills .kiro/skills/

# 從第一堂開始
cd 01-agent-workshop && cat QUICKSTART.md
```

## 完成後你有什麼

一個完整的個體 Agent：
- ✅ 有人格（SOUL.md 系統提詞）
- ✅ 有能力（Spec-Driven 開發的 Skills）
- ✅ 有記憶（Wiki 知識庫 + RAG 問答）

## 想繼續？

完成課程 A 後，進入 **[課程 B — AI Agent Team 實戰](../course-b/)**，
讓你的 Agent 從「一個人」變成「一個團隊」。

## 科技日報貫穿案例

| 堂次 | 日報怎麼做 |
|------|-----------|
| 01 | Bot 觸發 NewsSkill → 抓 HN 新聞 |
| 02 | Spec-Driven 重構 NewsSkill（多來源+重試） |
| 03 | 日報結果 ingest → Wiki，可問「上週趨勢」 |

---

*課程 A = 個體能力。課程 B = 團隊協作。*
