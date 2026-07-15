---
inclusion: always
---
# Memory — 專案狀態

> 持久化上下文，避免每次重問。定期由使用者更新。

## 專案狀態（2026-07-15）

- 架構：TG Bot gateway + Gemini Chat + Agent CLI 派工
- DB：SQLite（memory.db + sessions.db）
- 數據源：內部 SQLite、memory/ 日誌、wiki/ 知識庫

## 技術決策

- 圖表：matplotlib（中文需設定字型 PingFang TC / Noto Sans CJK）
- 查詢：直接 SQL 或 pandas read_sql
- 輸出：output/reports/ 或 output/exports/

## 踩坑紀錄

- matplotlib 中文需設定字型（PingFang TC / Noto Sans CJK）
- SQLite 在 Windows 下路徑需用正斜線或 raw string
