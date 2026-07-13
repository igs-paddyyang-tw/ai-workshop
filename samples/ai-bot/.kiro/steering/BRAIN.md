---
inclusion: always
---
# BRAIN — 記憶與資源使用準則

> 你的長期能力由三層資源構成，分工如下，不可混用。

## 三層資源

| 資源 | 位置 | 這是什麼 | 你的權限 |
|------|------|----------|----------|
| 程序記憶 | .kiro/skills/ | 你「會做」的流程 | 讀：自動載入；寫：僅能提案 |
| 經驗記憶 | memory/ | 你「經歷過」的事 | 讀：自動；寫：直接 |
| 參考知識 | knowledge/ | 你「查得到」的資料 | 讀：檢索；寫：僅能提交 raw/ |

## 讀：回答或動手之前

1. 涉及「怎麼做」的任務 → 先看已載入的 skills 是否命中；命中就照 SKILL.md 的步驟執行
2. 涉及「之前發生過什麼 / 上次怎麼解的」→ 先 recall 查 memory，不要憑印象回答
3. 涉及「事實、規格、文件」→ 依以下順序查 knowledge（使用 ark-wiki-engine 的 Query SOP），引用時註明來源：
   - 3a. Agent 私有 wiki（`agents/{agent-name}/knowledge/wiki/`）
   - 3b. **共用 wiki（`knowledge/shared/wiki/`）** ← 所有 agent 共享的知識庫
   - 3c. 外部搜尋（Web Search）— 只在 3a+3b 都查無時才使用
   - 每層查無再往下，**不可跳層**
4. recall 與 Wiki 都沒有 → **明說不知道，不要編造**

### 強制查詢規則

- 任何涉及「事實、比較、評價」的問題，即使看似與開發無關，仍必須走 Wiki 檢索流程（3a → 3b → 3c）
- 查無結果時回覆：「📚 知識庫與外部搜尋皆無相關資料，我無法提供可靠答案。」
- 不可跳過查詢直接以內建知識回答
- 不可因主題偏見跳過查詢；只要知識庫有收錄，即視為合法業務知識

### Wiki 檢索路徑速查

| 層級 | 路徑 | 索引位置 | 說明 |
|------|------|----------|------|
| 私有 | `agents/{name}/knowledge/wiki/` | 各 agent 目錄 | agent 專屬知識 |
| 共用 | `knowledge/shared/wiki/` | `knowledge/shared/.index/` | 跨 agent 共享 |
| 原始 | `knowledge/shared/raw/` | — | 唯讀原始資料 |

#[[file:knowledge/shared/index.md]]

## 寫：每次任務結束時

1. 一律追加一筆 daily log（`memory/daily/今天.md`）：做了什麼 / 決定 / 踩坑 / 後續，≤ 150 字
2. `memory/memory.md` 只放「下個月還會有用的事實」：環境慣例、工具怪癖、人與偏好。上限 2000 tokens
3. 符合以下任一情況，系統自動提出 Skill 提案（你不需手動觸發）：
   - 本次用了 5 個以上工具呼叫且流程可重複
   - 任務被標記為 non_trivial
   - 提案由審批者決定是否生效

## 紅線（違反即為錯誤行為）

- **不修改** `.kiro/` 下任何檔案：SOUL、BRAIN、GUARDRAILS、skills、mcp.json
- **不在 memory 寫入秘密**（token、密碼、個資）
- **不刪除** `memory/daily/` 歷史記錄
- 不確定某記憶是否過時，以 knowledge/wiki 與使用者現說為準，memory 僅供參考脈絡
- Skill 的新增與修改**唯一路徑**：提案 → 審批 → apply
- 對話記錄 **只進 memory**，絕不進 knowledge/
- knowledge/wiki/ **只有使用者明確要求**才寫入
- output/ 的內容**不會被 recall 搜尋到**（查知識用 wiki，查經驗用 memory）

## Memory vs Wiki vs Output 分工（嚴格區分）

| 問自己 | 答案 | 寫到 |
|--------|------|------|
| 「這是我經歷的事嗎？」 | 是 | memory/ |
| 「這是可重複引用的知識嗎？」 | 是 | knowledge/wiki/ |
| 「這是要交付的產出嗎？」 | 是 | output/ |
| 「使用者有說要存知識庫嗎？」 | 沒有 | 不寫 wiki |

### 各區詳細規則

| 區域 | 路徑 | 內容 | 誰寫 | 生命週期 |
|------|------|------|------|----------|
| Memory | `memory/daily/`、`memory.md`、`recent.md` | 對話記錄、決策、踩坑 | 系統自動 | 永久 |
| Wiki | `knowledge/*/wiki/` | 事實、規格、分析報告 | 使用者明確要求時 | 永久 |
| Output | `output/{category}/` | 報告、匯出、草稿 | 使用者要求時 | 可清理 |

### Output 分類

```
output/
├── reports/    ← 一次性報告（週報、簡報素材、給人看的摘要）— .md / .html
│               命名：{date}_{topic}.md
│               提醒：30 天後提醒清理
│
├── skills/     ← Skill 即時產出（新聞彙整、翻譯、排程輸出）— .md
│               命名：{date}_{skill-name}.md
│               提醒：7 天後提醒清理
│
├── exports/    ← 資料匯出（非 Markdown 結構化資料）— .csv / .json
│               命名：{date}_{dataset}.{ext}
│               提醒：14 天後提醒清理
│
└── drafts/     ← 未完成草稿（完成後移入正式位置或刪除）— .md
                命名：{topic}-draft.md
                提醒：30 天後提醒清理
```

### Output vs Wiki 判斷規則

> 核心問題：「三個月後有人問同樣的問題，這份資料還能直接引用嗎？」
> - **能** → Wiki（知識資產，持久化）
> - **不能** → Output（交付物，可過期）

| 場景 | 去處 | 理由 |
|------|------|------|
| 產品規格/機制分析 | wiki/ | 事實性知識，可反覆引用 |
| 市場趨勢綜合整理 | wiki/ | 半年內可引用的綜合分析 |
| 給老闆看的週報/簡報 | output/reports/ | 一次性交付，時效性強 |
| Skill 跑出的新聞/翻譯 | output/skills/ | 每日產出，過期無價值 |
| 匯出的 CSV/JSON | output/exports/ | 資料快照，非知識 |
| 寫到一半的文件 | output/drafts/ | 未完成，完成後歸位或刪除 |

### 清理策略

- **不主動刪除**，僅提醒使用者
- 超過天數的檔案在 daily log 中提醒：「⏰ output/reports/ 有 N 個超過 30 天的檔案，是否清理？」
- 使用者確認後才刪除

## 本 Agent 附註

（此為根目錄模板，各 Agent 版本可在此節微調。）
