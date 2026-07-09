---
title: "ADR-002: 為什麼改用相對路徑不用 Symlink"
category: adr
status: accepted
created: 2026-07-09
tags: [symlink, relative-path, cross-platform, KIRO.md]
---

# ADR-002: 為什麼改用相對路徑不用 Symlink

## 決策背景

專案中多個模組需要共用 `shared/` 目錄下的資源（Skills、Wiki、Config）。
最初使用 symlink 讓各模組「看到」共用資源，後來改為相對路徑引用。

## Symlink 的問題

### 1. Windows 不友善
- Windows 建立 symlink 需要管理員權限或開發者模式
- 部分 Git 客戶端不正確處理 symlink（clone 後變成純文字檔）
- 學員環境不可控，無法假設所有人都能建 symlink

### 2. 權限混淆
- 容器環境中 symlink 指向宿主機路徑會斷裂
- CI/CD runner 的工作目錄不同，symlink 指向錯誤位置
- 多人開發時，絕對路徑的 symlink 只在建立者的機器上有效

### 3. 認知負擔
- `ls -la` 看到 symlink 指向不明路徑，新人困惑
- 刪除 symlink 和刪除目標的語義不同，容易誤刪
- IDE 有時會跟隨 symlink 顯示重複檔案

## 解法：`../../shared/` 相對路徑

```
ai-workshop/
├── shared/              ← 共用資源放這裡
│   ├── skills/
│   └── wiki/
├── samples/
│   ├── ai-bot/          ← 用 ../../shared/skills 引用
│   └── ai-team-agent/   ← 用 ../../shared/skills 引用
```

規則很簡單：**從使用者的位置，用 `../` 往上走到共同祖先，再往下走到目標**。

## KIRO.md 的角色

每個模組根目錄的 `KIRO.md` 負責宣告「我的共用資源在哪」：

```markdown
## Shared Resources
- Skills: ../../shared/skills
- Wiki: ../../shared/wiki
- Config: ../../shared/config
```

Agent 讀取 `KIRO.md` 就知道去哪裡找資源，不需要 symlink 幫忙。

## 後果

### 接受的代價
- 路徑比較長（`../../shared/skills/ark-grill-me`）
- 搬移目錄層級時要更新相對路徑

### 獲得的好處
- 跨平台零問題（Windows、Linux、macOS、Docker）
- Git clone 後直接可用，不需要額外設定步驟
- 學員不需要理解 symlink 概念
- CI/CD 和容器環境自然支援
