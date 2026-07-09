---
title: "踩坑：bat 中文亂碼 + spawn 24 個 python"
type: article
tags: [windows, bat, encoding, process]
created: 2026-07-09
updated: 2026-07-09
---

# 踩坑：bat 中文亂碼 + spawn 24 個 python

## 問題 1：中文亂碼

bat 檔案用 UTF-8 存檔含中文，CMD 預設 cp950（Big5），所有中文都變亂碼。

## 問題 2：start /B spawn 多個 python

`start /B python start.py` 本意是背景執行，但 CMD 對每個 `start` 都 spawn 一個新進程。加上 uvicorn reload + bot subprocess，最終產生 24 個 python.exe。

## 解法

```batch
@echo off
chcp 65001 >nul 2>&1
title HOYEAH_BOT
:: 純 ASCII，前景模式，不用 start /B
python start.py
```

停止用 wmic 精準殺：
```batch
taskkill /FI "WINDOWTITLE eq HOYEAH_BOT" /F
for /f ... wmic process where "CommandLine like '%%start.py%%'" ...
```

## 教訓

- bat 檔案只用 ASCII，不寫中文
- 不用 `start /B`，用前景模式 + window title 辨識
- 停止時用 CommandLine 匹配，不靠 PID 檔案
