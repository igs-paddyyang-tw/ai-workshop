---
title: "ADR-006: 舊 samples 直接重建，不保留 legacy 目錄"
category: adr
status: accepted
created: 2026-09-14
tags: [samples, git, maintenance]
---

# ADR-006: 舊 samples 直接重建，不保留 legacy 目錄

## 背景

兩個 sample 共 19,963 行手搭實作（ai-bot 9,995 / ai-team-agent 9,968），
其能力已全部被 `ark_bot_agent` / `ark_team_agent` 取代。

## 決策

`git rm` 掉 `src/` · `apps/web/` · `templates/` · `Dockerfile*` 等，重建為套件消費端骨架。
**不保留 `samples/legacy/`。**

舊實作靠 git 歷史封存：
```bash
git show 987d00d:samples/ai-bot/src/llm/agent_loop.py
```

## 理由

- 學員看到兩份 sample 會問「我該看哪個」——而正確答案永遠是新的那個
- 守門（`check_docs.py` 的 `sample-not-package`）必須為 legacy 開豁免，
  而**豁免清單最常見的失敗模式就是順便蓋掉別的問題**
- repo 從 9 MB 降到約 1 MB（版控部分）

## 後果

- ✅ 「這個資料夾裡沒有 runtime」成為可驗證的規則，不是口號
- ❌ 想看舊實作要下 git 指令（已寫進本 ADR）
