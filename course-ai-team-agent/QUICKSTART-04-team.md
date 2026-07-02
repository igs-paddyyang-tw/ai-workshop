# 🚀 第四堂：Agent Team — 它們能「合作」

> 50 分鐘體驗：5 Agent 並行派工、觀察 TaskGraph 拆任務、科技日報分工。

## 前置
- Python 3.12+ / Telegram Bot Token / Kiro CLI 2.7+

## 啟動（5 min）
```bash
cd samples/ai-team-agent
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # 填入 TELEGRAM_BOT_TOKEN
cp team-ops.yaml team.yaml
python start.py
```

## 50 min 節奏
| 時間 | 動作 | 你做什麼 |
|------|------|------|
| 0-5 | 啟動 | pip install + start.py |
| 5-15 | 基本派工 | /agents → /assign → /board |
| 15-30 | ⭐ 科技日報 | 派工 market + report → 觀察並行 |
| 30-40 | 程式碼閱讀 | 打開 task_graph + discovery 看背後邏輯 |
| 40-50 | 加 Agent + Q&A | 改 team.yaml 加新角色 → 重啟 |

## 操作細節

### 基本派工（5-15 min）
📱 Telegram：
- /agents → 看 5 個 Agent
- /assign 寫 REST API backend → 觀察自動派給 coder
- /board → 看任務狀態

### 科技日報分工（15-30 min）
📱 輸入：
```
@leader 規劃科技日報：market 抓新聞、report 產出 HTML
```
觀察：leader 拆任務 → market 爬蟲 → report 渲染 → TG 推送

### 程式碼閱讀（30-40 min）
```bash
head -60 src/coordinator/a2a/graph.py      # TaskGraph
head -60 src/coordinator/a2a/discovery.py   # Agent 匹配
```

## 完成度
🏆 科技日報分工完成 + 理解 TaskGraph + 加新 Agent
✅ /assign 派工 + /board 看到狀態
🎯 start.py 啟動 + /agents 有回應

## 回家練習
- 切換 team-dev.yaml（研發團隊）再試
- 改 scheduler.yaml 加每日排程
- 試 Docker 部署
