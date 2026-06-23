# AI Workshop

> 漸進式 AI Agent 開發教學：Bot → Team → Platform → Skills → Wiki

## Workshop 列表

| # | Workshop | 時長 | 一鍵指令 | 學什麼 |
|---|----------|------|---------|--------|
| 01 | [AI Bot](01-ai-bot-workshop/) | 50 min | `build_bot.py` | 單一 Bot 對話 + 意圖路由 |
| 02 | [Agent Team](02-agent-team-workshop/) | 50 min | `build_team.py` | 多 Agent 協作 + TG 派工 |
| 03 | [Platform](03-platform-workshop/) | 50 min | 續用 02 | API + Web + A2A + 四層架構 |
| 04 | [Skills](04-skills-workshop/) | 50 min | AI 自動產出 | Skill 架構 + AI 協作開發 |
| 05 | [LLM Wiki](05-llm-wiki-workshop/) | 50 min | `ark-wiki-engine` | RAG 問答 + 知識圖譜 + 自動萃取 |

## 前置條件

- Python 3.12+
- Git
- Kiro CLI 2.7+（Workshop 02+）
- Telegram 帳號 + Bot Token
- Gemini API Key（Workshop 01, 05）
- Node.js 20+（僅 Workshop 03）

## 快速開始

```bash
# 取得 Skills
git clone https://github.com/igs-paddyyang-tw/ark-agent-skills .kiro/skills/

# 選一個 Workshop 開始
cd 01-ai-bot-workshop && cat QUICKSTART.md
```
