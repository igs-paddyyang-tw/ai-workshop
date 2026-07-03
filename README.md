# AI Workshop

> 五堂課建立自演化 AI 團隊。用 Kiro IDE vibe coding + Telegram 即時驗證。

## 兩個獨立課程

| 課程 | 名稱 | 堂數 | 你學會 |
|------|------|------|--------|
| **[A](course-ai-bot/)** | AI Agent 開發入門 | 3 堂 | 說話 → 做事 → 記住 |
| **[B](course-ai-team-agent/)** | AI Agent Team 實戰 | 2 堂 | 合作 → 自己跑 |

## 五堂課能力遞進

| 堂 | 主題 | 一句話 | Skill | 帶走的能力 |
|---|------|--------|-------|-----------|
| 01 | 🗣️ Agent 初始 | 改 SOUL → Bot 行為變 | — | 為任何場景設計 AI 人格 |
| 02 | ⚡ Skills 開發 | 拷問 → Spec → 實作 → 驗證 | grill-me + superpowers + skill-creator + validator | Spec-Driven 開發方法 |
| 03 | 🧠 LLM Wiki | 加知識 → 回答有依據 | ark-wiki-engine | 建立知識庫 + 自演化 |
| 04 | 🤝 Agent Team | 一句話派工 → 自動分工 | ark-agent-team-builder + ark-kiro-init | 建立 AI 團隊 |
| 05 | 🏭 營運落地 | 排程 + 費控 = 自動運作 | — | 從 Demo 到正式上線 |

```
01 控制 AI 說什麼（SOUL）
 ↓
02 保證做得好（Spec-Driven）
 ↓
03 越用越聰明（RAG + 自演化）
 ↓
04 一群 AI 協作（Team）
 ↓
05 自動運作（排程 + 費控 + 監控）
```

## 教學方式

**你不需要寫程式。** 打字告訴 Kiro IDE 你要什麼 → 去 Telegram 驗證結果。

| 操作 | 圖示 | 做什麼 |
|------|------|--------|
| Kiro IDE | 📝 | 自然語言指示 AI 修改程式碼 |
| 終端 | 💻 | 啟動服務、curl API |
| Telegram | 📱 | 手動驗證效果（= 使用者視角） |

### 兩個工程思維

| 課程 | 思維 | 核心心法 |
|------|------|---------|
| A（01-03） | 🏗️ 駕馭工程 | 你是方向盤，AI 是引擎。你決定去哪。 |
| B（04-05） | 🔄 迴圈工程 | 設計迴圈不是步驟。讓系統自己跑、自己學。 |

## 快速開始

```bash
# 課程 A：個體 Agent
cd samples/ai-bot
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt && cp .env.example .env
# 填入 TELEGRAM_BOT_TOKEN + GEMINI_API_KEY
python start.py

# 課程 B：Agent Team
cd samples/ai-team-agent
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt && cp .env.example .env
# 填入 TELEGRAM_BOT_TOKEN + GEMINI_API_KEY
python start.py
```

## 貫穿案例：遊戲競品分析

五堂課使用同一個業務情境，逐步升級：

| 堂 | 做什麼 |
|----|--------|
| 01 | 設計「遊戲分析師」的 SOUL |
| 02 | 開發新聞爬蟲 Skill（Spec-Driven） |
| 03 | 匯入 Ocean King / Super Ace 競品分析到 Wiki |
| 04 | market + designer + report 三 Agent 協作產出報告 |
| 05 | 排程每天自動產出科技日報 + 每週競品週報 → 產出自動累積成知識 |

## 目錄結構

```
ai-workshop/
├── README.md
├── course-ai-bot/                  ← 課程 A 教材
│   ├── QUICKSTART-01-agent.md      ← 第一堂（SOUL 設計）
│   ├── QUICKSTART-02-skills.md     ← 第二堂（Spec-Driven）
│   ├── QUICKSTART-03-wiki.md       ← 第三堂（RAG 知識庫）
│   ├── build-guide.md              ← 完整規格（課後參考）
│   └── sample-docs/                ← Wiki 範例素材
├── course-ai-team-agent/           ← 課程 B 教材
│   ├── QUICKSTART-04-team.md       ← 第四堂（團隊派工）
│   ├── QUICKSTART-05-platform.md   ← 第五堂（營運落地）
│   └── build-guide.md              ← 完整規格（課後參考）
├── samples/                        ← 完整可跑範例（帶走用）
│   ├── ai-bot/                     ← 8 Agent + Inline Button + Memory
│   └── ai-team-agent/             ← 5 Agent 團隊平台
├── docs/                           ← 文件
│   ├── ai-workshop-guide.html      ← 分頁總覽（首頁+A+B+進階）
│   └── enterprise-5-layer-architecture.html
├── shared/                         ← 共用資源
└── instructor/                     ← 講師指南
```

## 前置條件

| 工具 | 課程 A | 課程 B |
|------|--------|--------|
| Python 3.12+ | ✅ | ✅ |
| Telegram Bot Token | ✅ | ✅ |
| Gemini API Key | ✅ | ✅ |
| Kiro IDE | ✅ | ✅ |

## 學完能做什麼

| 堂 | 職場應用 |
|----|---------|
| 01 | 幫公司建一個有品牌風格的客服 / 助手 Bot |
| 02 | 用 Spec 管理 AI 功能開發（可交接、可審核、可驗證） |
| 03 | 建立公司知識庫，新人問 Agent 就有依據的答案 |
| 04 | AI 團隊自動處理日常（新聞 / 競品分析 / 報告） |
| 05 | 排程自動跑 + 費用控管 + 任務監控 = 正式上線 |

---

*兩個課程完全獨立，可分開授課。帶走 `samples/` 就能直接用在業務。*
