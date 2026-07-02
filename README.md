# AI Workshop

> 漸進式 AI Agent 開發教學：用 samples 體驗，用 build-guide 理解。

## 兩個獨立課程

| 課程 | 名稱 | 堂數 | 體驗什麼 |
|------|------|------|---------|
| **[A](course-ai-bot/)** | AI Agent 開發入門 | 3 堂（2.5 hr） | 切 Agent + 改 SOUL + 開發 Skill + RAG 問答 |
| **[B](course-ai-team-agent/)** | AI Agent Team 實戰 | 2 堂（1.5 hr） | 派工 + 分工並行 + Dashboard + 費用管理 |

## 五堂課學什麼

| 堂 | 主題 | 核心概念 | 帶走的能力 |
|---|------|---------|-----------|
| 01 | 說話 | SOUL = Agent 的靈魂 | 設計 AI 人格、控制回覆風格 |
| 02 | 做事 | Spec-Driven = 品質保障 | 拷問→Spec→實作→驗證 的開發迴圈 |
| 03 | 記住 | RAG = 有依據的回答 | 知識庫管理 + 自演化循環 |
| 04 | 合作 | TaskGraph = 自動分工 | 多 Agent 派工 + 並行執行 |
| 05 | 管理 | Dashboard = 全盤掌控 | API + 費用 + 排程 + 監控 |

### 能力遞增

```
01 你能控制一個 AI 的「說什麼」
    ↓
02 你能保證它「做得好」
    ↓
03 你能讓它「越來越聰明」
    ↓
04 你能讓「一群 AI 協作」
    ↓
05 你能「掌控全局」
```

### 學完能做什麼

| 堂 | 職場應用 |
|----|---------|
| 01 | 幫公司建一個有品牌風格的客服 Bot |
| 02 | 用 Spec 管理 AI 功能開發（可交接、可審核） |
| 03 | 建立公司內部知識庫，新人問問題有依據 |
| 04 | 讓 AI 團隊自動處理日常營運（新聞/數據/報告） |
| 05 | 管理多個 AI Agent 的成本和品質 |

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
│   └── 素材
├── course-ai-team-agent/        ← 課程 B 教材
│   ├── build-guide.md           ← 完整規格（Step 0-8）
│   ├── QUICKSTART-04/05.md      ← 體驗操作（50 min × 2）
│   └── 素材
├── samples/                     ← 完整可跑範例
│   ├── ai-bot/                  ← 課程 A 用（8 Agent + Inline Button）
│   └── ai-team-agent/           ← 課程 B 用（5 Agent 並行平台）
├── shared/                      ← 共用資源
├── instructor/                  ← 講師指南
└── docs/                        ← 參考文件
```

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
