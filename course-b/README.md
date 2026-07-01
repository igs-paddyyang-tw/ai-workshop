# 課程 B — AI Agent Team 實戰

> 從個人到團隊的平台管理：合作 → 管理（2 堂，共 1.5 小時）

## 你會學到

```
04 它們能「合作」  多 Agent 派工 + 並行執行 + 故障隔離
05 你能「管理」    API + Dashboard + 費用 + 監控
```

## 課程總覽

| # | Workshop | 時長 | 核心 Skill | 產出 |
|---|----------|------|-----------|------|
| 04 | [Agent Team](04-agent-team-workshop/) | 50 min | `ark-agent-team-builder` + `ark-kiro-init` | 5 Agent 協作平台 |
| 05 | [平台管理](05-platform-workshop/) | 50 min | （續用 04 產出） | Dashboard + 運維能力 |

## 使用的 Skills（2 個核心 + 輔助）

| Skill | 用途 | 堂次 |
|-------|------|------|
| `ark-agent-team-builder` | 一鍵產出完整團隊平台（110+ 檔案） | 04 |
| `ark-kiro-init` | 批次產出所有 Agent 的 .kiro/ 配置 | 04 |

> 課程 B 的 Skill 數量少，但每個 Skill 產出量大（整個平台骨架）。

## 前置條件

- Python 3.12+
- Git
- Kiro CLI 2.7+（`kiro-cli login` 完成）
- Telegram 帳號 + Bot Token
- Node.js 20+（Web Dashboard）
- **建議**：已完成課程 A（或至少理解「一個 Agent 是什麼」）

## 快速開始

```bash
# 取得 Skills
git clone https://github.com/igs-paddyyang-tw/ark-agent-skills .kiro/skills/

# 從第四堂開始
cd 04-agent-team-workshop && cat QUICKSTART.md
```

## 完成後你有什麼

一個可實戰運作的 Agent Team 平台：
- ✅ 5 Agent 真正並行（CoreDaemon + kiro-cli）
- ✅ 任務狀態完整流轉（backlog → done）
- ✅ A2A 通訊（Agent 之間可對話派工）
- ✅ 費用控管 + 排程自動化 + 故障偵測
- ✅ Web Dashboard（Next.js）
- ✅ Docker 部署

## 團隊配置選擇

教學完帶走 `sample/`，可選擇：

| 配置 | 成員 | 場景 |
|------|------|------|
| **營運團隊** | admin + pm + market + data + report | 市場監控、數據分析、報告產出 |
| **研發團隊** | admin + pm + ai-dev + coder + qa | AI 開發、全端實作、品質保證 |

```bash
# 啟動營運團隊
cd ../sample && cp team-ops.yaml team.yaml && python start.py

# 或研發團隊
cd ../sample && cp team-dev.yaml team.yaml && python start.py
```

## 科技日報貫穿案例

| 堂次 | 日報怎麼做 |
|------|-----------|
| 04 | market 爬 + report 渲染 → TG 推送（分工並行） |
| 05 | Dashboard 看成功率 + 費用 + 排程管理 |

## 沒做課程 A？

可以直接從課程 B 開始，但建議：
1. 先跑一次 `sample/` 體驗完整平台（5 分鐘）
2. 看 04 開頭的「01-03 對照表」了解個體 Agent 概念

---

*課程 A = 個體能力。課程 B = 團隊協作。*
