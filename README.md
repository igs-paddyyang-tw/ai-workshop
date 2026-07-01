# AI Workshop

> 漸進式 AI Agent 開發教學：從個體到團隊，從能力到平台。

## 兩個獨立課程

| 課程 | 名稱 | 堂數 | 對象 | 產出 |
|------|------|------|------|------|
| **[A](course-a/)** | AI Agent 開發入門 | 3 堂（2.5 hr） | 個人開發者 | 一個有能力的 Agent |
| **[B](course-b/)** | AI Agent Team 實戰 | 2 堂（1.5 hr） | 團隊 Lead | 可運作的 Agent 團隊平台 |

```
課程 A（個體）                    課程 B（團隊）
┌─────────────────────┐          ┌─────────────────────┐
│ 01 說話（系統提詞）  │          │ 04 合作（多 Agent）  │
│ 02 做事（Skills）    │    →     │ 05 管理（Dashboard） │
│ 03 記住（Wiki）      │          │                     │
└─────────────────────┘          └─────────────────────┘
  7 個 Skills                      2 個 Skills
  一個人的完整能力                    一群人的協作管理
```

## Skills 分類

### 課程 A 使用的 Skills（7 個）

| Skill | 用途 | 堂次 |
|-------|------|------|
| `ark-agent-builder` | 一鍵建構 Bot 專案 | 01 |
| `ark-env-doctor` | 環境檢查 | 01 |
| `ark-grill-me` | 拷問設計 | 02 |
| `ark-superpowers` | 產出 Spec | 02 |
| `ark-skill-creator` | 建立 Skill | 02 |
| `ark-code-spec-validator` | 驗證 Code ↔ Spec | 02 |
| `ark-wiki-engine` | Wiki 知識庫 | 03 |

### 課程 B 使用的 Skills（2 個）

| Skill | 用途 | 堂次 |
|-------|------|------|
| `ark-agent-team-builder` | 一鍵產出完整團隊平台 | 04 |
| `ark-kiro-init` | 批次產出 Agent .kiro/ 配置 | 04 |

> A 用多個小 Skill 逐步建構；B 用少量大 Skill 一次產出整個平台。

## 三條路

### 路徑 A：直接體驗完整平台（5 分鐘）

```bash
cd sample
pip install -r requirements.txt
cp .env.example .env && cp team-ops.yaml team.yaml
python start.py
```

### 路徑 B：從零建構（教學路徑）

```bash
# 課程 A
cd course-a/01-agent-workshop && cat QUICKSTART.md

# 課程 B
cd course-b/04-agent-team-workshop && cat QUICKSTART.md
```

### 路徑 C：一鍵產出（快速路徑）

```bash
git clone https://github.com/igs-paddyyang-tw/ark-agent-skills .kiro/skills/
python3 .kiro/skills/ark-agent-team-builder/scripts/build_team.py my-team
python3 .kiro/skills/ark-kiro-init/scripts/build_kiro.py my-team/team.yaml my-team
```

## 目錄結構

```
ai-workshop/
├── course-a/                    ← 課程 A：個體 Agent（3 堂）
│   ├── README.md               ← 課程 A 入口
│   ├── 01-agent-workshop/      ← 說話
│   ├── 02-skills-workshop/     ← 做事
│   └── 03-llm-wiki-workshop/   ← 記住
│
├── course-b/                    ← 課程 B：團隊平台（2 堂）
│   ├── README.md               ← 課程 B 入口
│   ├── 04-agent-team-workshop/ ← 合作
│   └── 05-platform-workshop/   ← 管理
│
├── sample/                      ← 完整可運作平台（教學完帶走用）
│   ├── team-ops.yaml           ← 營運團隊（market + data + report）
│   ├── team-dev.yaml           ← 研發團隊（ai-dev + coder + qa）
│   └── ...                     ← 完整 ai-team-agent 架構
│
├── shared/                      ← 共用資源
│   └── bridge-diagram.md       ← 銜接全覽
├── docs/                        ← 計畫文件
└── instructor/                  ← 講師指南
```

## 科技日報貫穿案例

同一個需求，五堂課逐步升級：

| # | 堂 | 日報怎麼做 | 課程 |
|---|---|-----------|------|
| 01 | Agent | Bot 觸發 NewsSkill | A |
| 02 | Skills | Spec-Driven 重構 | A |
| 03 | Wiki | 結果 ingest → 可查詢 | A |
| 04 | Team | 分工並行（market + report） | B |
| 05 | 管理 | Dashboard 看成功率 + 費用 | B |

## 前置條件

| 工具 | 課程 A | 課程 B |
|------|--------|--------|
| Python 3.12+ | ✅ | ✅ |
| Git | ✅ | ✅ |
| Telegram Bot Token | ✅ | ✅ |
| Gemini API Key | ✅（01, 03） | — |
| Kiro CLI 2.7+ | — | ✅ |
| Node.js 20+ | — | ✅（Dashboard） |

## 誰適合什麼

| 你是... | 建議 |
|---------|------|
| AI 完全新手 | 課程 A → 課程 B |
| 有 Bot 經驗，想學 Skill 開發 | 課程 A 的 02-03 |
| 團隊 Lead，想建 AI 團隊 | 直接課程 B |
| 急用，不想上課 | 路徑 C 一鍵產出 |
| 想先體驗再決定 | 路徑 A 跑 sample |

---

*兩個課程獨立完整，可分開報名、分開授課。*
