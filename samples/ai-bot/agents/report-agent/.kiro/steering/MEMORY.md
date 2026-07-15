---
inclusion: always
---
# Memory — 專案狀態

> 持久化上下文，避免每次重問。定期由使用者更新。

## 專案狀態（2026-07-15）

- 架構：TG Bot gateway + Gemini Chat + Agent CLI 派工
- 輸出路徑：output/reports/（報告）、output/exports/（CSV/JSON）
- 格式：Markdown 為主，需要時產出 HTML

## 技術決策

- 模板：Jinja2（規劃中，目前純 Markdown）
- 圖表：matplotlib / Chart.js（視需求選擇）
- 命名：{date}_{topic}.md

## 踩坑紀錄

- matplotlib 中文需設定字型（PingFang TC / Noto Sans CJK）
- 報告超過 4000 字需分段發送（TG 訊息長度限制）
