---
title: "新聞爬蟲經驗筆記"
type: concept
tags: [scraping, news, httpx]
created: 2026-07-02
---

# 新聞爬蟲經驗

## Hacker News
- 用官方 Firebase API 最穩定（不需要 selector）
- topstories.json → 取前 N 個 ID → 逐個查詳情

## 注意事項
- 帶 User-Agent header 避免被擋
- 併發用 Semaphore(3) 限流
- 單來源 timeout 10s，失敗不影響其他
