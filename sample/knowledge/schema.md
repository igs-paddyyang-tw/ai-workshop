# Wiki Schema 規則 v3.0

## 目錄結構

```
knowledge/
├── raw/          → 唯讀原始資料（不可修改）
├── wiki/         → 結構化知識頁面（ingest 產出）
├── schema.md     → 本檔案（規則定義）
├── index.md      → 索引目錄
└── log.md        → 操作日誌（append-only）
```

## Frontmatter 必要欄位

每個 wiki/ 頁面必須有以下 YAML frontmatter：

| 欄位 | 必要 | 說明 |
|------|------|------|
| title | ✅ | 頁面標題 |
| type | ✅ | concept / entity / source |
| tags | ✅ | 分類標籤（陣列） |
| created | ✅ | 建立日期 YYYY-MM-DD |
| updated | ✅ | 更新日期 YYYY-MM-DD |

## 規則

- `raw/` 唯讀，不可修改
- 修改 wiki 後必須同步 `index.md`
- `log.md` 為 append-only，不可刪除舊記錄
