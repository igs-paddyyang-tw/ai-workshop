# b-agent-team — 課程 B 產出（Agent 團隊平台）

> 完整的 Agent Team 平台 = sample/ 根目錄本身。

## 說明

課程 B（04-05）的產出就是 `sample/` 根目錄的完整平台。本目錄只是一個指引。

## 快速啟動

```bash
# 回到 sample 根目錄
cd ../..

# 選團隊配置
cp team-ops.yaml team.yaml    # 營運：admin + pm + market + data + report
# cp team-dev.yaml team.yaml  # 研發：admin + pm + ai-dev + coder + qa

# 啟動
python start.py
```

## 跟 a-agent 的差異

| 維度 | a-agent（課程 A） | b-agent-team（課程 B） |
|------|------------------|----------------------|
| Agent 數量 | 1 個 | 5 個並行 |
| 執行方式 | 單進程 | CoreDaemon 多進程 |
| 協調 | Planner 路由 | TaskGraph + A2A |
| 知識庫 | 單一 knowledge/ | 每 Agent 獨立 + 共用 |
| 派工 | 無 | /assign + 自動分配 |
| 監控 | health API | Dashboard + 費用 + 審計 |
| 排程 | 無 | scheduler.yaml cron |
| 部署 | python start.py | Docker Compose |

## 完整文件

回到 `sample/` 根目錄查看 `README.md`，包含：
- 架構圖
- 專案結構
- API 端點清單
- Bot 指令
- Docker 部署
- 加入新 Agent 方法

---

*課程 B 的產出 = sample/ 根目錄。*
