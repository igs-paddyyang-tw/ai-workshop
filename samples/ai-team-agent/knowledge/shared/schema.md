# 知識庫 Schema（v3.0）

## Frontmatter 欄位

| 欄位 | 必要 | 型別 | 說明 |
|------|------|------|------|
| title | ✅ | string | 頁面標題（繁體中文） |
| type | ✅ | enum | 頁面類型（見下方合法值） |
| tags | ✅ | list | 分類標籤（全小寫、kebab-case） |
| created | ✅ | date | 建立日期（YYYY-MM-DD） |
| updated | ✅ | date | 最後更新日期（YYYY-MM-DD） |
| status | 建議 | enum | 頁面成熟度 |
| sources | 建議 | list | 來源（raw/ 檔案或 URL） |
| related | 建議 | list | 相關頁面（檔名不含 .md，用於圖譜） |
| aliases | 建議 | list | 別名（中英對照詞，用於精確查找） |

## 合法 type

| 值 | 用途 | 範例 |
|----|------|------|
| concept | 抽象概念解釋 | ReAct 模式、RAG 架構 |
| entity | 具體事物/產品 | Ocean King、Super Ace |
| source | 原始來源摘錄 | 論文摘要、文件節錄 |
| synthesis | 綜合整理/趨勢 | 市場動態報告 |
| comparison | 比較分析 | A vs B |
| overview | 概覽索引頁 | 知識庫總覽 |
| system | 系統規則/規範 | coding standards、protocol |

## 合法 status

| 值 | 說明 |
|----|------|
| seedling | 剛建立，內容粗略 |
| developing | 有內容但待補充 |
| mature | 完整可引用 |

## 頁面命名規則

- 檔名使用 kebab-case：`ocean-king-analysis.md`
- 不含路徑前綴：wiki 內直接平鋪
- 雙向連結格式：`[[檔名不含.md]]`

## 目錄結構規則

```
knowledge/shared/
├── raw/          → 唯讀原始資料（人類丟入，AI 不改）
├── wiki/         → 結構化知識頁面（AI ingest 產出）
├── .index/       → 持久化搜尋索引（自動生成）
├── schema.md     → 本檔案（規則定義）
├── index.md      → 索引目錄（所有 wiki 頁面列表）
└── log.md        → 操作日誌（append-only，不可刪改）
```

## 操作規則

- raw/ 只讀（人類丟入，AI 不改）
- wiki/ 由 AI ingest 產出或使用者明確要求時寫入
- log.md 只追加不刪改
- 每次 ingest/更新/lint-fix 都要追加 log 記錄
- index.md 必須包含 wiki/ 下所有頁面
