---
title: "Workshop Sample 預建專案計畫 — git clone 即用"
type: onepager
status: draft
language: zh-TW
created: 2026-06-26
author: admin-agent
tags: [ai-workshop, sample, teaching, quick-start]
---

# Workshop Sample 預建專案計畫 — git clone 即用

## 問題

目前 Workshop 50 分鐘中，20-30 分鐘花在「建構 + 安裝 + 設定」。
學員真正操作核心功能的時間只剩 20 分鐘。

## 目標

- 學員 `git clone` + 填 `.env` + `pip install` → 5 分鐘內啟動
- 50 分鐘全花在「使用」教學，不花在「建構」
- 5 個 Workshop 各一個可獨立運行的 sample 專案

## 非目標

- 不取代「從零建構」的教學路徑（那是 build-guide 的用途）
- 不改動現有 Skill 或 builder 程式碼

## 方案

### Repo 結構

```
github.com/igs-paddyyang-tw/ai-workshop-samples/
├── 01-agent/              ← Workshop 01 完整可跑的 Bot
├── 04-agent-team/          ← Workshop 02 完整可跑的 Team
├── 05-platform/            ← Workshop 03 完整可跑的 Platform（= 02 + Web）
├── 02-skills/         ← Workshop 04 Skills 開發範例
├── 03-llm-wiki/            ← Workshop 05 Wiki + RAG 完整可跑
└── README.md               ← 總導覽
```

### 每個 Sample 的標準結構

```
{sample}/
├── .env.example            ← 學員只需 cp → .env 填 Token
├── requirements.txt        ← pip install -r 就能跑
├── start.py                ← python start.py 一鍵啟動
├── README.md               ← 5 分鐘 Quick Start + 功能測試清單
├── src/                    ← 完整程式碼（已產出、可跑）
├── .kiro/                  ← Agent 配置（SOUL + Skills 已裝好）
├── knowledge/              ← 預置知識庫（含 sample docs）
└── docs/                   ← 使用教學（非建構教學）
```

### 學員操作流程（5 分鐘啟動）

```bash
git clone https://github.com/igs-paddyyang-tw/ai-workshop-samples.git
cd ai-workshop-samples/04-agent-team
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env        # 填入 TELEGRAM_BOT_TOKEN
python start.py             # 啟動！
```

### 50 分鐘時間分配（使用導向）

| 時間 | 動作 | 現有 | 新方案 |
|------|------|------|--------|
| 0-5 min | 環境啟動 | 20-30 min | **5 min**（clone + env + start） |
| 5-15 min | 核心功能體驗 | — | Telegram 實測 |
| 15-30 min | 進階功能探索 | — | 根據 Workshop 主題深入 |
| 30-45 min | 動手修改/擴充 | — | 學員自己改配置/加功能 |
| 45-50 min | 回顧 + Q&A | — | 架構理解 + 問答 |

## 5 個 Sample 的產出規格

### 01-agent

| 項目 | 內容 |
|------|------|
| 產出來源 | `build_agent.py` 產出 |
| 預置功能 | Telegram Bot + Gemini Chat + News Skill + Planner |
| 學員體驗 | `/start` → 問問題 → AI 回答 → 觸發新聞 |
| 需要的 Key | `TELEGRAM_BOT_TOKEN` + `GEMINI_API_KEY`（可選） |

### 04-agent-team

| 項目 | 內容 |
|------|------|
| 產出來源 | `build_team.py --level full` + `build_kiro.py --clone-skills` |
| 預置功能 | 5 Agent + Task Lifecycle + /board /assign + Autopilot |
| 學員體驗 | `/agents` → `/assign 寫 API` → 看派工 → `/board` |
| 需要的 Key | `TELEGRAM_BOT_TOKEN` |

### 05-platform

| 項目 | 內容 |
|------|------|
| 產出來源 | = 02 + apps/web/ + board.html |
| 預置功能 | API 21 端點 + Web Dashboard + Kanban Board |
| 學員體驗 | curl API → 開 /board 頁面 → Telegram 指令 |
| 需要的 Key | `TELEGRAM_BOT_TOKEN` |

### 02-skills

| 項目 | 內容 |
|------|------|
| 產出來源 | 最小 Web 專案 + 3 個範例 Skill 已產出 |
| 預置功能 | ark-grill-me + ark-superpowers + ark-code-spec-validator 可觸發 |
| 學員體驗 | 拷問設計 → 產出 Spec → 建 Skill → 驗證 Drift |
| 需要的 Key | 無（純本地 Kiro CLI） |

### 03-llm-wiki

| 項目 | 內容 |
|------|------|
| 產出來源 | Web 專案 + ark-wiki-engine 產出 + sample-docs 已 ingest |
| 預置功能 | Wiki API + Chat + RAG + 已有 3 篇知識頁面 |
| 學員體驗 | 問問題 → AI 引用 Wiki 回答 → lint → graph |
| 需要的 Key | `GEMINI_API_KEY` |

## 產出方式

### 方案 A：用現有 Skill 自動產出（推薦）

```bash
# 每個 sample 用對應的 builder 一鍵產出
python3 .kiro/skills/ark-agent-builder/scripts/build_agent.py samples/01-agent
python3 .kiro/skills/ark-agent-team-builder/scripts/build_team.py samples/04-agent-team
# 03 = 複製 02
cp -r samples/04-agent-team samples/05-platform
# 04 = 最小版 + 範例 Skills
# 05 = Web + Wiki + pre-ingest sample-docs
```

### 方案 B：從 ai-team-agent 直接剝離

直接複製 ai-team-agent 的精簡版到各 sample（最穩定，但手動）。

## 驗收條件

- [ ] 5 個 sample 都能 `clone → env → pip → start.py` 在 5 分鐘內跑起來
- [ ] 每個 sample 有獨立 README（使用教學，非建構教學）
- [ ] `.env.example` 只列必要的 Key（最少化）
- [ ] 不需要 Kiro CLI 就能跑（sample 是已產出的成品）
- [ ] 每個 sample 互相獨立（不依賴其他 sample）

## 預估工時

| 任務 | 時間 |
|------|------|
| 01-agent sample 產出 + README | 30 min |
| 04-agent-team sample 產出 + README | 30 min |
| 05-platform（= 02 延伸） | 15 min |
| 02-skills 手動組裝 | 30 min |
| 03-llm-wiki sample + pre-ingest | 30 min |
| 總導覽 README | 15 min |
| **合計** | **~2.5 小時** |

## 風險

| 風險 | 緩解 |
|------|------|
| 依賴版本不一致 | requirements.txt pin 版本 |
| sample 跟 builder 版本脫節 | 用 CI 定期重新產出 or 版本標記 |
| 學員電腦環境差異 | README 加 troubleshooting |

---

*使用 ark-superpowers 框架產出。*
