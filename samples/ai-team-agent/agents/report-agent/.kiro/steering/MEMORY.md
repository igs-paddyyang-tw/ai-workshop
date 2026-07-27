---
inclusion: always
---
# 🧠 report-agent 記憶

> 每完成一個段落必須更新。歸檔規則：> 2 週移到 knowledge/。

## 專案快照

- **專案：** ai-team-agent
- **角色：** Report — Markdown/HTML 報告產出、圖表渲染、定期摘要
- **狀態：** 動態啟動（收到任務時啟動）
- **上游：** leader-agent 派工 / data-agent + market-agent 資料

## 技術備註

- 完成任務後用 reply() 回報，遇阻礙用 log_to_leader()
- 產出存放：output/

## 近期進度

（agent 自行追加）
