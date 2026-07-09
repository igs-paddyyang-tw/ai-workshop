---
title: "Knowledge 三層知識架構 — Agent 私有 + 共用 + 專案"
type: onepager
status: approved
created: 2026-07-08
---

# Knowledge 三層知識架構

## 目標

讓每台 ai-bot / ai-team-agent 的知識庫統一為三層結構，Kiro CLI 和 TG/API 都能存取全部知識。

```
查詢優先順序：
  1. Agent 私有 → agents/{name}/knowledge/
  2. 共用知識  → knowledge/shared/
  3. 專案知識  → knowledge/{project}/（如 hoyeah/、ocean-king/）
```

---

## 目錄結構

```
project-root/
├── knowledge/                          ← 全域知識目錄
│   ├── shared/                         ← 所有 Agent 共用（通用知識）
│   │   ├── raw/
│   │   ├── wiki/
│   │   ├── .index/
│   │   ├── schema.md
│   │   ├── index.md
│   │   └── log.md
│   ├── hoyeah/                         ← 專案知識（遊戲相關）
│   │   ├── raw/
│   │   ├── wiki/
│   │   ├── .index/
│   │   ├── schema.md
│   │   ├── index.md
│   │   └── log.md
│   └── {other-project}/               ← 可擴充更多專案
│       └── ...
│
└── agents/
    └── {name}-agent/
        ├── .kiro/
        │   ├── steering/
        │   │   ├── SOUL.md
        │   │   ├── memory.md
        │   │   └── KIRO.md             ← 新增：指示 Kiro CLI 知識來源
        │   └── skills/
        ├── knowledge/                  ← Agent 私有知識（Kiro CLI 的 cwd 可達）
        │   ├── raw/                    ← 私有記憶寫入處
        │   ├── wiki/
        │   ├── shared -> ../../../knowledge/shared  (symlink)
        │   └── hoyeah -> ../../../knowledge/hoyeah  (symlink)
        └── output/
```

---

## 三層查詢優先順序

| 層級 | 路徑 | 用途 | 誰寫入 |
|------|------|------|--------|
| 1. 私有 | `agents/{name}/knowledge/raw/` + `wiki/` | Agent 個人記憶、對話累積 | Kiro CLI 自動寫 |
| 2. 共用 | `knowledge/shared/wiki/` | 所有 Agent 都該知道的（公司規範、流程、FAQ） | 人工 ingest |
| 3. 專案 | `knowledge/{project}/wiki/` | 特定產品/專案的知識（競品分析、設計文件） | 人工 ingest |

---

## Kiro CLI 存取方案：symlink + KIRO.md

### symlink（啟動時建立）

在 `start.py` 啟動時，對每個 Agent 建立 symlink：

```python
# start.py
for agent_dir in Path("agents").iterdir():
    if not agent_dir.is_dir():
        continue
    kb_dir = agent_dir / "knowledge"
    kb_dir.mkdir(exist_ok=True)

    # symlink 全域知識目錄
    for project in Path("knowledge").iterdir():
        if project.is_dir() and not project.name.startswith("."):
            link = kb_dir / project.name
            if not link.exists():
                link.symlink_to(project.resolve())
```

結果：

```
agents/market-agent/knowledge/
├── raw/              ← 私有（真實目錄）
├── wiki/             ← 私有（真實目錄）
├── shared -> /abs/path/knowledge/shared   (symlink)
└── hoyeah -> /abs/path/knowledge/hoyeah   (symlink)
```

### KIRO.md（告訴 Kiro CLI 知識來源）

在每個 Agent 的 `.kiro/steering/KIRO.md` 加入：

```markdown
## 知識庫存取

查詢知識時，依以下優先順序搜尋：

1. **私有知識**：`knowledge/raw/` 和 `knowledge/wiki/`（你自己的記憶）
2. **共用知識**：`knowledge/shared/wiki/`（所有 Agent 共用的通用知識）
3. **專案知識**：`knowledge/hoyeah/wiki/`（HoYeah 遊戲專案知識）

寫入新記憶時，寫到 `knowledge/raw/`（私有）。
引用知識時，標註來源層級：`[私有]`、`[共用]`、`[hoyeah]`。
```

Kiro CLI 讀 KIRO.md 後知道要往 symlink 的目錄查找。

---

## WikiEngine 改動

```python
class WikiEngine:
    def __init__(self, agent_id: str | None = None):
        # 三層 wiki 目錄（查詢優先順序）
        self.layers = []

        # Layer 1: Agent 私有
        if agent_id:
            private = BASE_DIR / "agents" / f"{agent_id}-agent" / "knowledge"
            if private.exists():
                self.layers.append(("private", private))

        # Layer 2: 共用
        shared = BASE_DIR / "knowledge" / "shared"
        if shared.exists():
            self.layers.append(("shared", shared))

        # Layer 3: 專案（掃所有 knowledge/{project}/）
        for project_dir in sorted((BASE_DIR / "knowledge").iterdir()):
            if project_dir.is_dir() and project_dir.name not in ("shared", ".index"):
                self.layers.append((project_dir.name, project_dir))

    async def query(self, q: str, **kwargs) -> dict:
        """三層查詢：私有 → 共用 → 專案。"""
        all_results = []
        for scope, kb_path in self.layers:
            hits = self._search_layer(kb_path, q)
            for h in hits:
                h["scope"] = scope
            all_results.extend(hits)
        # ... 四層搜尋管線（metadata → BM25 → hybrid → rerank）
```

---

## Ingest 改動

```python
# ingest 支援指定目標
engine.ingest(scope="shared")          # 匯入到 knowledge/shared/
engine.ingest(scope="hoyeah")          # 匯入到 knowledge/hoyeah/
engine.ingest(scope="private")         # 匯入到 agents/{name}/knowledge/
```

API：
```
POST /api/v1/wiki/ingest?scope=shared
POST /api/v1/wiki/ingest?scope=hoyeah
POST /api/v1/wiki/ingest              # 預設 shared
```

---

## 實作步驟

| # | 任務 | 時間 |
|---|------|------|
| 1 | 建立 `knowledge/shared/` 結構（schema + index + log） | 10 min |
| 2 | 現有根目錄 `knowledge/raw/` + `wiki/` 搬入 `knowledge/shared/` | 10 min |
| 3 | start.py 加 symlink 建立邏輯 | 15 min |
| 4 | 每個 Agent 的 KIRO.md 加知識庫存取指示 | 15 min |
| 5 | WikiEngine 改為三層查詢 | 30 min |
| 6 | indexer.py 支援多知識庫目錄（每個 scope 各自的 .index/） | 20 min |
| 7 | ingest API 加 scope 參數 | 15 min |
| 8 | .gitignore 更新 `knowledge/**/.index/` | 5 min |
| 9 | 驗收：Kiro CLI 能透過 symlink 查到全域知識 | 15 min |

**總計 ~2.5 小時**

---

## 驗收條件

- [ ] `agents/*/knowledge/shared` symlink 指向 `knowledge/shared/`
- [ ] Kiro CLI 在 agent cwd 下能讀到 `knowledge/shared/wiki/*.md`
- [ ] KIRO.md 指示 Kiro CLI 查詢三層知識
- [ ] WikiEngine query 依序查 私有 → shared → {project}
- [ ] ingest scope=shared / scope=hoyeah 分別寫入對應目錄
- [ ] 每個 scope 有各自的 .index/（metadata + bm25s）
- [ ] 私有記憶仍寫入 `agents/{name}/knowledge/raw/`
- [ ] TG Bot 和 Web API 能查到三層知識

---

## 遷移計畫（現有資料搬移）

```
現有：
  knowledge/raw/*.md        → 搬到 knowledge/shared/raw/
  knowledge/wiki/*.md       → 搬到 knowledge/shared/wiki/
  knowledge/index.md        → 搬到 knowledge/shared/index.md
  knowledge/schema.md       → 搬到 knowledge/shared/schema.md
  knowledge/log.md          → 搬到 knowledge/shared/log.md
  knowledge/.index/         → 搬到 knowledge/shared/.index/

新建：
  knowledge/hoyeah/raw/     ← 未來放遊戲專案知識
  knowledge/hoyeah/wiki/
  knowledge/hoyeah/schema.md
  knowledge/hoyeah/index.md
  knowledge/hoyeah/log.md
```

---

## 教學對應

| 堂 | 教什麼 |
|----|--------|
| 01 | SOUL + KIRO.md（知識來源設定） |
| 03 | ingest 到 shared/（共用知識）+ 查詢三層 |
| 04 | 團隊派工時 Agent 引用 shared 知識互相協作 |
| 06 | 跨機時，每台的 shared/ 內容不同 → 各有專長 |
