---
name: ark-version-sync
description: |
  版本對齊 — 檢查 upstream 最新異動，比對本地差異，自動補上修改並產出 changelog。
  觸發：當使用者提到 版本更新、對齊 upstream、同步最新版本、拉最新的改動。
---

# 版本對齊 Skill

## 上游來源
https://github.com/igs-paddyyang-tw/ai-workshop/tree/main/samples/ai-bot

## 步驟
1. 取得 upstream（GitHub repo）最新 commit 清單
2. 比對本地檔案與 upstream 差異（新增/修改/刪除）
3. 列出差異摘要供使用者確認
4. 使用者確認後，自動拉取變更並套用到本地
5. 產出本次同步的 changelog（寫入 docs/ 或回覆）

## 觸發詞
- 幫我版本更新
- 對齊 upstream
- 同步最新版本
- 拉最新的改動
- version sync
- pull latest

## 輸出格式
```
🔄 版本對齊報告
├── Upstream: igs-paddyyang-tw/ai-workshop@main
├── 最新 commit: <sha> <message>
├── 差異檔案: N 個
│   ├── 新增: file1.py
│   ├── 修改: file2.py
│   └── 刪除: file3.py
└── 狀態: ✅ 已同步 / ⏳ 待確認
```

## 注意事項
- 同步前會列出差異讓使用者確認，不會自動覆蓋
- 本地有未 commit 的修改時會警告
- 產出的 changelog 會標記日期和同步範圍
