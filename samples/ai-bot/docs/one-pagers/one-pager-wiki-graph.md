---
title: "Wiki Graph 全貌圖 — 執行計劃"
type: onepager
status: approved
created: 2026-07-07
---

# Wiki Graph 全貌圖

## 目標

一眼看完整個 Agent 生態系：**誰（Agent）→ 會什麼（Skill）→ 知道什麼（Wiki）**

## 現況問題

- 只有 3 個 wiki 節點互連（太空、無意義）
- 連結邏輯只靠共享 tag（全部都有 competitive-analysis → 全連 = 看不出結構）
- 沒有 Agent 和 Skill 的關係

## 設計

### 三層節點

| 層 | 節點來源 | 顏色 | 大小 |
|----|---------|------|------|
| 🤖 Agent | `agents/*/` 目錄 | 紫色 #a78bfa | 大（24px） |
| ⚡ Skill | `agents/*/skills/*/SKILL.md` | 橘色 #fb923c | 中（16px） |
| 📄 Wiki | `knowledge/wiki/*.md` | 青色 #22d3ee | 小（12px） |

### 連線邏輯

| 連線 | 意義 | 怎麼判斷 |
|------|------|---------|
| Agent → Skill | 這個 Agent 有這個能力 | Skill 在 `agents/{agent}/skills/` 下 |
| Skill → Wiki | Skill 讀這份知識 | SKILL.md 提到 `knowledge/wiki` 或觸發詞匹配 wiki title |
| Wiki ↔ Wiki | 共享 tag | 兩頁有相同 tag |

### 視覺佈局

```
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│         🤖          🤖          🤖         🤖               │
│       admin        pm        market      data    ...        │
│         │           │          │  \        │                │
│         ▼           ▼          ▼   \       ▼                │
│        ⚡           ⚡         ⚡    ⚡     ⚡               │
│    system-       task-    market-  competitor  data-         │
│    monitor      planning research    -brief  analysis       │
│                              │          │                   │
│                              ▼          ▼                   │
│                   📄─────────📄─────────📄                  │
│               ocean-king  super-ace  fishing-vs-slot         │
│                                                             │
│  圖例：🤖 Agent（紫）  ⚡ Skill（橘）  📄 Wiki（青）        │
│  大小：大 → 中 → 小                                         │
└─────────────────────────────────────────────────────────────┘
```

### 互動功能

| 功能 | 做法 |
|------|------|
| 點節點 | 右側顯示詳情（SOUL 摘要 / SKILL 步驟 / Wiki frontmatter） |
| Hover | 高亮該節點的所有連線 |
| 篩選 | 工具列按鈕：全部 / 只看 Agent / 只看 Skill / 只看 Wiki |
| 拖曳 | 滑鼠拖曳節點調整位置 |

### 右側面板

```
📊 統計
  Agent: 8 | Skill: N | Wiki: 4 | 連結: M

📄 選中節點詳情
  （點節點後顯示）

🎨 圖例
  🤖 Agent（紫，大）
  ⚡ Skill（橘，中）
  📄 Wiki（青，小）
  ── Agent→Skill（有這能力）
  ── Skill→Wiki（讀這知識）
  ── Wiki↔Wiki（共享 tag）
```

## 資料來源 API

| 需要什麼 | 從哪取 |
|---------|--------|
| Agent 列表 | 讀 `agents/` 目錄 或 hardcode 8 個 |
| Skill 列表 | 讀 `agents/*/skills/*/SKILL.md` |
| Wiki 列表 | `GET /api/v1/wiki/pages` |
| Wiki 內容（取 tags） | `GET /api/v1/wiki/pages/{filename}` |

### 新 API（如果需要）

```python
@app.get("/api/v1/graph")
async def get_graph():
    """回傳完整圖譜資料（節點+連線）"""
    return {
        "nodes": [...],  # {id, type, label, meta}
        "links": [...],  # {source, target, relation}
    }
```

## 實作步驟

| # | 任務 | 檔案 | 時間 |
|---|------|------|------|
| 1 | 新增 `/api/v1/graph` endpoint | `src/server/main.py` | 30 min |
| 2 | 重寫 `graph.html` 三層節點 + 連線 | `templates/graph.html` | 1 hr |
| 3 | 力導向升級（分層排斥 + 拖曳） | `templates/graph.html` | 30 min |
| 4 | 右側面板（統計 + 點擊詳情） | `templates/graph.html` | 30 min |
| 5 | 篩選工具列 | `templates/graph.html` | 15 min |

**總時間：~3 小時**

## 驗收條件

- [ ] 圖譜顯示 8 Agent + N Skill + 4+ Wiki 節點
- [ ] Agent→Skill 連線正確（對應目錄結構）
- [ ] 點節點右側顯示詳情
- [ ] 三種顏色+大小可辨識
- [ ] 不依賴外部套件（純 Canvas）

## 備註

- 不用 d3（太重），用原生 Canvas + 簡易力導向
- 節點數 < 50，效能不是問題
- 未來加入 memory 節點（私有知識）可擴展
