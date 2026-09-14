# 課程 B — AI Agent Team 實戰

> 用 `samples/ai-team-agent` 體驗：合作 → 自己跑（2 堂 × 50 min）

## 教學方式

```
啟動 samples/ai-team-agent → Kiro 設定團隊 → Telegram 派工驗證 → 排程自動運作
```

## 文件

| 文件 | 用途 |
|------|------|
| [QUICKSTART-04-team.md](QUICKSTART-04-team.md) | 第四堂：加 Agent + 派工 + 捕魚機競品 |
| [QUICKSTART-05-platform.md](QUICKSTART-05-platform.md) | 第五堂：排程 + 費控 + 知識累積 |
| [build-guide.md](build-guide.md) | 課後：從零建構（Step 0-8） |

## 兩堂課體驗什麼

| 堂 | 主題 | 核心操作 |
|----|------|---------|
| 04 | 合作 | Kiro 加 Agent → `/assign` vs `@leader` 派工 → 捕魚機競品分析 |
| 05 | 自己跑 | 設排程 → 設費控 → 手動觸發 → 產出自動進知識庫 → 迴圈成長 |

## 快速啟動

```bash
cd ../samples/ai-team-agent
python3 -m venv .venv && source .venv/bin/activate
pip install './ark_team_agent-<版本>-py3-none-any.whl'
python3 scripts/sync_skills.py        # 裝各 agent 的專業技能
cp .env.example .env                  # 填你自己的 TELEGRAM_BOT_TOKEN
python start.py
```

⏱️ 首次啟動兩階段：daemon + TG 約 20 秒，kiro-cli backend 冷啟 **2–4 分鐘**。

## 團隊配置

完整 8 人在 `team.yaml`；想精簡就**把不需要的 instance 整段註解掉**：

| 配置 | 成員 | 場景 |
|------|------|------|
| 完整 | admin + leader + ai-dev + coder + qa + market + data + report | 全場景 |
| 營運 5 人 | admin + leader + market + data + report | 市場 + 數據 + 報告 |
| 研發 5 人 | admin + leader + ai-dev + coder + qa | 開發 + 測試 |

## 完成後

```
排程自動派工 → Agent 協作產出 → 產出寫入知識庫 → 下次更準 → ♻️
= 自演化的 AI 團隊平台
```

→ 帶走 `samples/ai-team-agent/`，改 team.yaml + scheduler.yaml 直接用！

---

*QUICKSTART = 上課體驗。build-guide = 課後建構。*
