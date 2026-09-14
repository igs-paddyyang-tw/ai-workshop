---
title: "ADR-007: 課程 B 的 Dashboard 改用套件內建 website"
category: adr
status: accepted
created: 2026-09-14
tags: [curriculum, dashboard, dependencies]
---

# ADR-007: 課程 B 的 Dashboard 改用套件內建 website

## 背景

舊版 `samples/ai-team-agent/apps/web/` 是一套 Next.js Dashboard，
課堂要 `npm install` + `npm run dev`（Node 20+）。

而 `ark_team_agent` **自己就會起一個看板**，port = `health_port + 5000`
（1.6.2 起 offset 為 5000），`/api/health` 的回應裡就寫著它在哪。

## 決策

移除 `apps/web/`，課程 B 改教內建 website（`23050` → 看板 `28050`）。

## 理由

- `npm install` 是課堂最大的卡點來源（版本、網路、平台差異）
- 兩套看板功能重疊，而學員上線後用的是內建那個
- 少一個技術棧 = 少一類故障

## 後果

- ✅ 學員看到的看板與正式環境一致
- ✅ 前置條件不再需要 Node.js
- ❌ 失去「自己改前端」的練習 —— 需要的人用 `ark-frontend-design` 另做
