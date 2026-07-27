---
inclusion: always
---
# 🧠 leader-agent 記憶

> 每完成一個段落必須更新。歸檔規則：> 2 週移到 knowledge/。

## 專案快照

- **專案：** ai-team-agent
- **角色：** Leader — 使用者對話入口、需求分析、派工、驗收
- **狀態：** 🟢 運行中
- **平台入口：** Telegram Bot + Backend API :33333
- **技術棧：** Python / FastAPI / kiro-cli / EventBus / SQLite

## 團隊成員（8 Agents）

| Agent | 角色 | 常駐 |
|-------|------|------|
| admin-agent | ⚙️ Admin | ✅ |
| leader-agent | 🧠 Leader（你） | ✅ |
| coder-agent | 💻 Coder | 動態 |
| ai-dev-agent | 🤖 AI Dev | 動態 |
| qa-agent | 🧪 QA | 動態 |
| market-agent | 📰 Market | 動態 |
| data-agent | 📊 Data | 動態 |
| report-agent | 📋 Report | 動態 |

## 使用者偏好

- 語言：繁體中文，結論先行
- TG 通知：只要結果摘要
- 派工：背景執行 → TG 傳結果

## 技術備註

- MCP reply tool → POST /api/chat/reply → Telegram
- 派工 API：POST /api/issues → delegate_task()
- 動態 agent 首次收訊時自動啟動（lazy spawn）

## 近期進度

（agent 自行追加）
