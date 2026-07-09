# docs/ — 文件索引

## 結構

```
docs/
├── README.md                ← 本檔（索引）
├── specs/                   ← 規格文件（需求定義）
├── designs/                 ← 設計文件（架構決策）
├── plans/                   ← 執行計畫（里程碑 + 任務）
├── one-pagers/              ← 快速提案（合併版）
└── archive/                 ← 歷史文件（僅供參考）
```

## 現行文件

### 自我成長系統（進行中）

| 文件 | 類型 | 狀態 | 說明 |
|------|------|------|------|
| [specs/self-growth-spec.md](specs/self-growth-spec.md) | Spec | draft | 需求規格：記憶 + Skill 推薦 + Steering 重構 |
| [designs/self-growth-design.md](designs/self-growth-design.md) | Design | proposed | 技術設計：架構 + ADR + API + 模組 |
| [plans/self-growth-plan.md](plans/self-growth-plan.md) | Plan | draft | 執行計畫：3 Phase × 具體任務 |

### One Pagers（已完成功能的快速提案）

| 文件 | 功能 |
|------|------|
| [one-pagers/one-pager-8-agents-config.md](one-pagers/one-pager-8-agents-config.md) | 8 Agent 配置 |
| [one-pagers/one-pager-a2a-lite.md](one-pagers/one-pager-a2a-lite.md) | A2A 輕量派工 |
| [one-pagers/one-pager-inline-agent-switch.md](one-pagers/one-pager-inline-agent-switch.md) | Inline Agent 切換 |
| [one-pagers/one-pager-knowledge-layers.md](one-pagers/one-pager-knowledge-layers.md) | 知識庫分層 |
| [one-pagers/one-pager-wiki-browser.md](one-pagers/one-pager-wiki-browser.md) | Wiki 瀏覽器 |
| [one-pagers/one-pager-wiki-graph.md](one-pagers/one-pager-wiki-graph.md) | Wiki 圖譜 |

### Archive（歷史參考）

| 文件 | 說明 |
|------|------|
| archive/self-growth-architecture-v0.2.md | 原始架構設計草稿（已由 spec + design 取代） |
| archive/agent-expert-platform-spec.md | 早期平台規格 |
| archive/system-architecture.md | 早期系統架構 |
| archive/architecture-wiki-paths.md | Wiki 路徑設計稿 |

## 文件命名規範

- Spec：`{feature}-spec.md`
- Design：`{feature}-design.md`
- Plan：`{feature}-plan.md`
- One Pager：`one-pager-{feature}.md`
- ADR：`designs/adr/{NNN}-{title}.md`（未來需要時建立）
