# AI Workshop

> 漸進式 AI Agent 開發教學：從個體到團隊，從能力到平台。

## 兩個獨立課程

| 課程 | 名稱 | 堂數 | 產出 |
|------|------|------|------|
| **[A](course-a/)** | AI Agent 開發入門 | 3 堂（2.5 hr） | 有靈魂的個體 Agent |
| **[B](course-b/)** | AI Agent Team 實戰 | 2 堂（1.5 hr） | 可運作的團隊平台 |

```
課程 A（個體）                    課程 B（團隊）
┌─────────────────────┐          ┌─────────────────────┐
│ Phase 1 說話（SOUL） │          │ Phase 1 合作（Team）│
│ Phase 2 做事（Skill）│    →     │ Phase 2 管理（平台）│
│ Phase 3 記住（Wiki） │          │                     │
└─────────────────────┘          └─────────────────────┘
  7 個 Skills                      2 個 Skills
```

## 三條路

### A. 直接體驗（5 分鐘）

```bash
cd sample/a-agent && pip install -r requirements.txt && python start.py
cd sample/b-agent-team && pip install -r requirements.txt && python start.py
```

### B. 從零建構（教學路徑）

```bash
cat course-a/build-guide.md   # Step 0-10
cat course-b/build-guide.md   # Step 0-8
```

### C. 一鍵產出

```bash
git clone https://github.com/igs-paddyyang-tw/ark-agent-skills .kiro/skills/
python3 .kiro/skills/ark-agent-builder/scripts/build_agent.py my-agent
python3 .kiro/skills/ark-agent-team-builder/scripts/build_team.py my-team
```

## 目錄結構

```
ai-workshop/
├── README.md                    ← 本文件
├── course-a/                    ← 課程 A（3 堂）
│   ├── build-guide.md          ← 統一規格（Phase 1-3, Step 0-10）
│   ├── QUICKSTART-01/02/03     ← 分堂 50 min 節奏
│   └── 素材（soul-example, sample-docs 等）
├── course-b/                    ← 課程 B（2 堂）
│   ├── build-guide.md          ← 統一規格（Phase 1-2, Step 0-8）
│   ├── QUICKSTART-04/05        ← 分堂 50 min 節奏
│   └── 素材（team.example.yaml 等）
├── sample/                      ← 完整可跑範例
│   ├── a-agent/                ← 課程 A 成品（8 Agent + Inline Button）
│   └── b-agent-team/           ← 課程 B 成品（5 Agent 並行平台）
├── shared/                      ← 共用資源
│   ├── bridge-diagram.md       ← 銜接全覽
│   ├── env-check.md            ← 環境檢查
│   └── telegram-setup.md       ← TG 設定步驟
├── instructor/                  ← 講師指南
│   └── teaching-guide.md       ← 5 堂課教學手冊
└── docs/                        ← 設計文件
```

## Skills 分類

| 課程 | Skills |
|------|--------|
| A | `ark-agent-builder`, `ark-kiro-init`, `ark-grill-me`, `ark-superpowers`, `ark-code-spec-validator`, `ark-skill-creator`, `ark-wiki-engine` |
| B | `ark-agent-team-builder`, `ark-kiro-init` |

## 科技日報貫穿案例

| Phase | 做法 |
|-------|------|
| A-1 | Bot 觸發 NewsSkill → 抓 HN |
| A-2 | Spec-Driven 重構爬蟲 |
| A-3 | 日報 ingest → Wiki |
| B-1 | market + report 分工並行 |
| B-2 | Dashboard 看成功率 + 費用 |

## 前置條件

| 工具 | 課程 A | 課程 B |
|------|--------|--------|
| Python 3.12+ | ✅ | ✅ |
| Git | ✅ | ✅ |
| Telegram Bot Token | ✅ | ✅ |
| Gemini API Key | ✅ | — |
| Kiro CLI 2.7+ | — | ✅ |
| Node.js 20+ | — | ✅ |

---

*兩個課程獨立完整，可分開報名授課。*
