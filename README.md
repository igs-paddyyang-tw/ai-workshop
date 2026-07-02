# AI Workshop

> 漸進式 AI Agent 開發教學：用 samples 體驗，用 build-guide 理解。

## 兩個獨立課程

| 課程 | 名稱 | 堂數 | 體驗什麼 |
|------|------|------|---------|
| **[A](course-ai-bot/)** | AI Agent 開發入門 | 3 堂（2.5 hr） | 切 Agent + 改 SOUL + 開發 Skill + RAG 問答 |
| **[B](course-ai-team-agent/)** | AI Agent Team 實戰 | 2 堂（1.5 hr） | 派工 + 分工並行 + Dashboard + 費用管理 |

```
課程 A（用 samples/ai-bot）         課程 B（用 samples/ai-team-agent）
┌──────────────────────────┐       ┌──────────────────────────┐
│ 01 說話（切 Agent + SOUL）│       │ 04 合作（派工 + 並行）    │
│ 02 做事（Spec-Driven）    │  →    │ 05 管理（Dashboard）      │
│ 03 記住（RAG + Wiki）     │       │                          │
└──────────────────────────┘       └──────────────────────────┘
```

## 教學方式

```
啟動 samples（5 min）→ 動手操作（35 min）→ 理解原理（10 min）
```

| 文件 | 用途 |
|------|------|
| QUICKSTART | 上課用（50 min 體驗操作） |
| build-guide | 課後用（從零建構 + 完整原理） |

## 快速開始

```bash
# 課程 A：個體 Agent
cd samples/ai-bot
pip install -r requirements.txt && cp .env.example .env
python start.py

# 課程 B：Agent Team
cd samples/ai-team-agent
pip install -r requirements.txt && cp .env.example .env
cp team-ops.yaml team.yaml && python start.py
```

## 目錄結構

```
ai-workshop/
├── README.md
├── course-ai-bot/               ← 課程 A 教材
│   ├── build-guide.md           ← 完整規格（Step 0-10）
│   ├── QUICKSTART-01/02/03.md   ← 體驗操作（50 min × 3）
│   ├── quickstart.html          ← 教材展示頁
│   └── 素材
├── course-ai-team-agent/        ← 課程 B 教材
│   ├── build-guide.md           ← 完整規格（Step 0-8）
│   ├── QUICKSTART-04/05.md      ← 體驗操作（50 min × 2）
│   ├── quickstart.html          ← 教材展示頁
│   └── 素材
├── samples/                     ← 完整可跑範例
│   ├── ai-bot/                  ← 課程 A 用（8 Agent + Inline Button）
│   └── ai-team-agent/           ← 課程 B 用（5 Agent 並行平台）
├── shared/                      ← 共用資源
├── instructor/                  ← 講師指南
└── docs/                        ← 參考文件
```

## Skills 分類

| 課程 | Skills（上課體驗用） |
|------|---------------------|
| A | `ark-grill-me`、`ark-superpowers`、`ark-code-spec-validator`、`ark-wiki-engine` |
| B | （直接操作 samples，不需要額外 Skill） |

| 課程 | Skills（從零建構用） |
|------|---------------------|
| A | `ark-agent-builder`、`ark-kiro-init` + 上面 4 個 |
| B | `ark-agent-team-builder`、`ark-kiro-init` |

## 前置條件

| 工具 | 課程 A | 課程 B |
|------|--------|--------|
| Python 3.12+ | ✅ | ✅ |
| Git | ✅ | ✅ |
| Telegram Bot Token | ✅ | ✅ |
| Gemini API Key | ✅ | — |
| Kiro CLI 2.7+ | 選配 | ✅ |
| Node.js 20+ | — | ✅（Dashboard） |

---

*兩個課程獨立完整，可分開報名授課。*
