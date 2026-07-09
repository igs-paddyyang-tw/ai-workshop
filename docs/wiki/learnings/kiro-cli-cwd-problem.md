---
title: "踩坑：Kiro CLI 看不到全域知識庫"
type: article
tags: [kiro-cli, knowledge, cwd, pitfall]
created: 2026-07-09
updated: 2026-07-09
---

# 踩坑：Kiro CLI 看不到全域知識庫

## 問題

Kiro CLI 的 cwd 是 `agents/{name}-agent/`，它只能看到相對於 cwd 的檔案。根目錄的 `knowledge/shared/wiki/` 對 Agent 來說是「不存在」的。

## 症狀

- Agent 被問知識庫問題時回答「找不到相關資料」
- TG Bot 和 Web API 能正常查到（因為程式碼硬寫根目錄路徑）
- 只有 Kiro CLI 直接對話時出問題

## 嘗試過的方案

| 方案 | 問題 |
|------|------|
| symlink | Windows 權限問題 + 容器裡失效 + 維護混淆 |
| 改 cwd 到根目錄 | 破壞 .kiro/steering/ 的讀取機制 |

## 最終解法

在 KIRO.md 裡用相對路徑 `../../knowledge/shared/wiki/` 告訴 Kiro CLI 去哪找：

```markdown
## 知識庫三層架構
1. 私有：knowledge/raw/
2. 共用：../../knowledge/shared/wiki/
3. 專案：../../knowledge/{project}/wiki/
```

Kiro CLI 讀到 KIRO.md 後，知道要用 `../../` 往上跳兩層去查。

## 教訓

- Kiro CLI 的 file read tool 支援相對路徑，但 LLM 不會自己猜要往上跳
- 必須在 steering 明確寫路徑，不能靠「約定俗成」
