# 課程 B — AI Agent Team 實戰

> 用 `samples/ai-team-agent` 體驗：合作 → 管理（2 堂 × 50 min）

## 教學方式

```
啟動 samples/ai-team-agent → 派工操作 → 理解架構
```

## 文件

| 文件 | 用途 |
|------|------|
| [QUICKSTART-04-team.md](QUICKSTART-04-team.md) | 第四堂：派工 + 科技日報分工 |
| [QUICKSTART-05-platform.md](QUICKSTART-05-platform.md) | 第五堂：API + Dashboard + 排程 |
| [build-guide.md](build-guide.md) | 課後：從零建構（Step 0-8） |
| [quickstart.html](quickstart.html) | 教材展示頁 |

## 兩堂課體驗什麼

| 堂 | 主題 | 核心操作 |
|----|------|---------|
| 04 | 合作 | `/assign` 派工 → 觀察 5 Agent 並行 → 科技日報分工 |
| 05 | 管理 | curl API → Dashboard → 費用追蹤 → 改排程 |

## 快速啟動

```bash
cd ../samples/ai-team-agent
pip install -r requirements.txt && cp .env.example .env
cp team-ops.yaml team.yaml
python start.py
```

## 團隊配置

| 配置 | 成員 | 場景 |
|------|------|------|
| 營運 | admin + pm + market + data + report | 市場 + 數據 + 報告 |
| 研發 | admin + pm + ai-dev + coder + qa | 開發 + 測試 |

## 素材

| 檔案 | 用途 |
|------|------|
| `team.example.yaml` | team.yaml 格式範例 |
| `troubleshooting.md` | 常見問題排除 |

## 完成後

```
5 Agent 並行 + A2A 通訊 + Dashboard + 費用控管 + Docker 部署 = 可實戰平台
```

→ 帶走 `samples/ai-team-agent/`，選團隊配置直接用！

---

*QUICKSTART = 上課體驗。build-guide = 課後建構。*
