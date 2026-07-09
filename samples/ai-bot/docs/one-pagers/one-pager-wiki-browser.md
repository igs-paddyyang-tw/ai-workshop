---
title: "Wiki 瀏覽器優化 — 資料夾樹狀結構"
type: onepager
status: approved
created: 2026-07-07
---

# Wiki 瀏覽器優化 — 資料夾樹狀結構

## 問題

目前 Wiki 瀏覽器只支援平面列表（`knowledge/wiki/*.md`），當知識庫成長後需要分類：

```
knowledge/wiki/
├── competitive/          ← 競品分析類
│   ├── ocean-king-analysis.md
│   ├── super-ace-analysis.md
│   └── fishing-vs-slot-comparison.md
├── market/               ← 市場趨勢類
│   └── slot-market-trends.md
├── game-design/          ← 遊戲設計類
│   └── boss-design-spec.md
└── overview.md           ← 根層頁面
```

## 需要改的

### 1. API 支援遞迴列出（含子資料夾）

```python
@app.get("/api/v1/wiki/pages")
async def list_wiki_pages():
    """列出所有 wiki 頁面（含子資料夾，回傳樹狀結構）。"""
    wiki_dir = Path("knowledge/wiki")
    
    def scan_dir(dir_path: Path, prefix: str = "") -> list:
        items = []
        for entry in sorted(dir_path.iterdir()):
            rel_path = f"{prefix}{entry.name}" if not prefix else f"{prefix}/{entry.name}"
            if entry.is_dir():
                children = scan_dir(entry, rel_path)
                items.append({"type": "folder", "name": entry.name, "path": rel_path, "children": children})
            elif entry.suffix == ".md":
                content = entry.read_text(encoding="utf-8")
                title = extract_title(content)
                items.append({"type": "file", "filename": rel_path, "title": title})
        return items
    
    return {"pages": scan_dir(wiki_dir)}
```

回傳格式：
```json
{
  "pages": [
    {"type": "folder", "name": "competitive", "path": "competitive", "children": [
      {"type": "file", "filename": "competitive/ocean-king-analysis.md", "title": "Ocean King..."},
      {"type": "file", "filename": "competitive/super-ace-analysis.md", "title": "Super Ace..."}
    ]},
    {"type": "file", "filename": "overview.md", "title": "知識庫總覽"}
  ]
}
```

### 2. GET /api/v1/wiki/pages/{path} 支援子路徑

```python
@app.get("/api/v1/wiki/pages/{filepath:path}")
async def get_wiki_page(filepath: str):
    path = Path("knowledge/wiki") / filepath
    if not path.exists():
        return {"error": "not found"}
    return {"filename": filepath, "content": path.read_text(encoding="utf-8")}
```

### 3. Wiki 前端 — 樹狀側欄

```
┌──────────────┬──────────────────────────────────────────┐
│ 🔍 搜尋       │                                          │
│              │  # Ocean King 捕魚機系列競品分析           │
│ 📁 competitive│                                          │
│   📄 ocean-king│  ## 系列概覽                             │
│   📄 super-ace │  Ocean King 是 IGS 開發的...             │
│   📄 fishing-vs│                                          │
│ 📁 market     │  ## 各版本特色比較                        │
│   📄 slot-trends│ ...                                     │
│ 📁 game-design│                                          │
│   📄 boss-spec │                                          │
│ 📄 overview   │  📚 Tags: fishing-game, arcade            │
│              │  📅 Created: 2026-07-02                    │
└──────────────┴──────────────────────────────────────────┘
```

#### 前端功能

| 功能 | 做法 |
|------|------|
| 資料夾可展開/收合 | 點 📁 toggle children |
| 搜尋即時過濾 | 輸入關鍵字 → 只顯示匹配的檔案 |
| 點檔案載入內容 | fetch `/api/v1/wiki/pages/{path}` |
| Markdown 渲染 | 簡易 HTML 轉換（標題/粗體/列表/表格/程式碼） |
| Frontmatter 顯示 | 解析後顯示在內容底部（tags/type/created） |
| 目前選中高亮 | 側欄 active 樣式 |

### 4. WikiEngine 支援子資料夾搜尋

```python
# engine.py _search_dir 已用 rglob("*.md")，自動支援子資料夾 ✅
```

### 5. Ingest 支援子資料夾產出

```python
# raw/ 也可以有子資料夾
# ingest 時保持目錄結構：raw/competitive/xxx.md → wiki/competitive/xxx.md
```

## 實作步驟

| # | 任務 | 檔案 | 時間 |
|---|------|------|------|
| 1 | API list_wiki_pages 改為遞迴樹狀 | `src/server/main.py` | 20 min |
| 2 | API get_wiki_page 支援 `{filepath:path}` | `src/server/main.py` | 10 min |
| 3 | wiki.html 側欄改為樹狀（展開/收合） | `templates/wiki.html` | 40 min |
| 4 | wiki.html Markdown 渲染優化 | `templates/wiki.html` | 20 min |
| 5 | wiki.html frontmatter 解析顯示 | `templates/wiki.html` | 15 min |
| 6 | WikiEngine.ingest 保持子資料夾結構 | `src/wiki/engine.py` | 15 min |

**總時間：~2 小時**

## 驗收條件

- [ ] 知識庫有子資料夾時，API 回傳樹狀結構
- [ ] Wiki 側欄顯示 📁 可展開收合
- [ ] 點檔案能載入並渲染 Markdown
- [ ] 搜尋能過濾（含子資料夾內的檔案）
- [ ] Ingest 保持 raw/ 的子資料夾結構
- [ ] 現有的平面結構（無子資料夾）也正常運作

## 相容性

- 現在 wiki/ 沒子資料夾 → 平面列表照常顯示（沒有 folder 節點）
- 學員加子資料夾後 → 自動出現樹狀結構
- WikiEngine 的 `rglob("*.md")` 已支援遞迴搜尋

## 未來擴充

- 新增資料夾（前端按鈕）
- 拖曳移動檔案到不同資料夾
- 批次操作（全資料夾 ingest / lint）
