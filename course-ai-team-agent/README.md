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
| 04 | 合作 | Kiro 加 Agent → `/assign` vs `@pm` 派工 → 捕魚機競品分析 |
| 05 | 自己跑 | 設排程 → 設費控 → 手動觸發 → 產出自動進知識庫 → 迴圈成長 |

## 快速啟動

```bash
cd ../samples/ai-team-agent
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt && cp .env.example .env
python start.py
```

## 團隊配置

| 配置 | 成員 | 場景 |
|------|------|------|
| 營運 | admin + pm + market + data + report | 市場 + 數據 + 報告 |
| 研發 | admin + pm + ai-dev + coder + qa | 開發 + 測試 |

## 完成後

```
排程自動派工 → Agent 協作產出 → 產出寫入知識庫 → 下次更準 → ♻️
= 自演化的 AI 團隊平台
```

→ 帶走 `samples/ai-team-agent/`，改 team.yaml + scheduler.yaml 直接用！

---

*QUICKSTART = 上課體驗。build-guide = 課後建構。*
