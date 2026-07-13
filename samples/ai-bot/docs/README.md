# docs/ — 文件索引

## 結構

```
docs/
├── README.md          ← 本檔（索引）
├── specs/             ← 規格文件（需求定義）
├── designs/           ← 設計文件（架構決策 + ADR）
├── plans/             ← 執行計畫（里程碑 + 任務）
└── one-pagers/        ← 快速提案（一頁式概念驗證）
```

> 歷史文件不再保留 archive/。
> 有知識價值的已移入 `knowledge/shared/wiki/`，草稿移入 `output/drafts/`。

## 四類文件定義

| 類型 | 用途 | 生命週期 | 命名規範 |
|------|------|----------|----------|
| Spec | 需求規格：做什麼、為什麼、驗收標準 | 定案後不改 | `{feature}-spec.md` |
| Design | 技術設計：怎麼做、ADR、模組拆分 | 隨實作演進 | `{feature}-design.md` |
| Plan | 執行計畫：Phase / 任務 / 時間 | 完成後歸檔 | `{feature}-plan.md` |
| One Pager | 輕量提案：一頁搞定背景+方案+決策 | 核准後不改 | `one-pager-{feature}.md` |

## 現行文件

### ReAct Agent 系統

| 文件 | 類型 | 狀態 |
|------|------|------|
| [specs/react-agent-spec.md](specs/react-agent-spec.md) | Spec | approved |
| [designs/react-agent-design.md](designs/react-agent-design.md) | Design | done |
| [plans/react-agent-plan.md](plans/react-agent-plan.md) | Plan | done |
| [one-pagers/one-pager-gemini-react-agent.md](one-pagers/one-pager-gemini-react-agent.md) | One Pager | done |

### 自我成長系統

| 文件 | 類型 | 狀態 |
|------|------|------|
| [specs/self-growth-spec.md](specs/self-growth-spec.md) | Spec | draft |
| [designs/self-growth-design.md](designs/self-growth-design.md) | Design | proposed |
| [plans/self-growth-plan.md](plans/self-growth-plan.md) | Plan | draft |

### 平台規格

| 文件 | 類型 | 狀態 |
|------|------|------|
| [specs/agent-expert-platform-spec.md](specs/agent-expert-platform-spec.md) | Spec | approved |

### One Pagers（已完成功能）

| 文件 | 功能 |
|------|------|
| [one-pager-8-agents-config.md](one-pagers/one-pager-8-agents-config.md) | 8 Agent 配置 |
| [one-pager-a2a-lite.md](one-pagers/one-pager-a2a-lite.md) | A2A 輕量派工 |
| [one-pager-dual-mode-chat.md](one-pagers/one-pager-dual-mode-chat.md) | 雙模式對話 |
| [one-pager-inline-agent-switch.md](one-pagers/one-pager-inline-agent-switch.md) | Inline Agent 切換 |
| [one-pager-knowledge-layers.md](one-pagers/one-pager-knowledge-layers.md) | 知識庫分層 |
| [one-pager-wiki-browser.md](one-pagers/one-pager-wiki-browser.md) | Wiki 瀏覽器 |
| [one-pager-wiki-graph.md](one-pagers/one-pager-wiki-graph.md) | Wiki 圖譜 |

## 文件命名規範

| 類型 | 格式 | 範例 |
|------|------|------|
| Spec | `{feature}-spec.md` | `react-agent-spec.md` |
| Design | `{feature}-design.md` | `react-agent-design.md` |
| Plan | `{feature}-plan.md` | `react-agent-plan.md` |
| One Pager | `one-pager-{feature}.md` | `one-pager-wiki-graph.md` |
| ADR | `designs/adr/{NNN}-{title}.md` | 需要時建立 |

## docs vs wiki vs output 的區別

| 問自己 | 答案 | 去處 |
|--------|------|------|
| 「這是開發流程文件嗎？（spec/design/plan）」 | 是 | docs/ |
| 「這是可反覆引用的知識嗎？」 | 是 | knowledge/wiki/ |
| 「這是一次性交付物嗎？」 | 是 | output/ |
