---
title: "Skill 開發建置教學 — 6 步驟 Spec-Driven 完整迴圈"
type: guide
created: 2026-06-23
updated: 2026-06-23
author: paddyyang
language: zh-TW
---

# Skill 開發建置教學 — 6 步驟 Spec-Driven 完整迴圈

使用 Ark Skills 進行 Spec-Driven Skill 開發：拷問設計 → 產出規格 → 實作 → 驗證。

**五層架構定位**：L4 執行層 → L5 知識層（技能宣告化 + Spec 驗證）

**操作位置圖示：**
- 📝 = 在 **AI IDE 聊天框**（Kiro CLI）輸入
- 💻 = 在**終端機**執行指令

---

## 專案定位

**Spec-Driven Skill 開發 — 讓 AI 寫 Skill，但品質由 Spec 把關**

核心流程：
```
拷問設計 → 產出 Spec → 依 Spec 實作 → 驗證一致性 → Ship
```

這對應五層架構中 L5 自演化的前半段：有規格才能驗證、有驗證才能信任、有信任才能全域發布。

---

## 前置條件

- Kiro CLI 2.7+
- Python 3.12+
- `.kiro/skills/` 已 clone（含 ark-grill-me、ark-superpowers、ark-skill-creator、ark-code-spec-validator）

### 建議：用你的 01 Bot 專案來練習

> 如果你做過 Workshop 01，在 `my-bot` 專案中開發新 Skill，這樣 01 的 Bot 立刻獲得新能力。
>
> 沒做過 01？沒關係，本堂可完全獨立運行，用任何目錄都行。

**用 my-bot 的好處：**

```
my-bot/
├── src/skills/internal/        ← 你的拷問對象：重構或新增 Skill
├── docs/specs/                 ← Spec 產出位置
└── .kiro/skills/my-daily-news/ ← 新 Skill 產出位置
```

**本堂的貫穿範例：** 重構 01 的 `news_scraper` Skill
- 01 你手寫了一個簡單爬蟲
- **02（本堂）用 Spec-Driven 方式重構它**：加入多來源併發、失敗重試、結構化輸出
- 03 重構後的 Spec + Skill 會被 ingest 到 Wiki，成為組織知識

---

## 建置步驟總覽

| # | Skill | 產出內容 | 角色 |
|---|-------|---------|------|
| 0 | — | 理解 Skill 三層架構 | 概念 |
| 1 | ark-grill-me | 決策摘要 | 釐清需求 |
| 2 | ark-superpowers | docs/specs/*.md | 標準化文件 |
| 3 | ark-skill-creator | .kiro/skills/my-skill/ | 實作 |
| 4 | — | 觸發測試 + evals.json | 品質確認 |
| 5 | ark-code-spec-validator | Drift Report | 驗證一致性 |

---

## Step 0：Skill 三層架構概念

### 什麼是 Skill？

Skill 是 AI 的「記憶模組」——使用者提到特定關鍵字時，AI 自動載入對應指令集。

### 三層載入

```
my-skill/
├── SKILL.md          ← 第 2 層：完整指令（觸發時載入）
│   ├── frontmatter   ← 第 1 層：name + description（永遠在 context）
│   └── markdown body ← 指令內容
├── references/       ← 第 3 層：按需載入（大型參考文件）
├── scripts/          ← 可執行程式碼
└── evals/            ← 評估測試集
```

| 層級 | 載入時機 | 大小建議 |
|------|---------|---------|
| 第 1 層 `description` | 永遠在 context | ~100 字 |
| 第 2 層 `SKILL.md` body | 觸發時 | < 500 行 |
| 第 3 層 `references/` | 明確指示時 | 無限制 |

### 觸發機制

```yaml
---
name: my-daily-news
description: |
  每日科技新聞日報：抓取 RSS Feed，產出 HTML 日報頁面。
  使用此 Skill 當使用者提及新聞日報、RSS、tech news、每日摘要、
  news digest、或任何需要自動抓取新聞並產出報告的場景。
---
```

**原則**：description 要「稍微積極」——寧可多觸發，也不要漏觸發。

---

## Step 1：拷問設計（ark-grill-me）

### 為什麼要拷問？

Plan Mode 的問題：一次給完整計畫 → 人容易說 OK → 控制權被 AI 拿走。
Grill Me 的解法：AI 提問、人回答 → 人保有設計控制權。

### 操作

📝 在 Kiro 聊天框輸入：

```
拷問我的設計：每日科技新聞日報 Skill，抓取 RSS 產出 HTML 日報頁面
```

> 💡 **如果在 my-team 中操作**，更推薦這個版本：
> ```
> 拷問我的設計：重構 market-agent 的 news_scraper Skill，
> 改善 01 的簡單爬蟲，加入多來源併發 + 失敗重試 + 結構化 JSON 輸出
> ```
> 這會讓 AI 針對「從既有實作升級」提出更精準的設計問題。

### AI 行為

- 一次問一個問題，附 2-4 選項 + 推薦答案
- 走完決策樹所有分支（資料來源、輸出格式、觸發方式、邊界條件）
- 通常 8-15 題

### 你的角色

- **主動參與**：質疑推薦答案、補充想法
- **控制範疇**：太細的問題說「之後再決定」
- **不要被動 OK**：每個決策都想過再答

### 產出

拷問結束後 AI 產出「決策摘要」：

```markdown
## 決策摘要：每日科技新聞日報

| # | 決策點 | 決定 | 理由 |
|---|--------|------|------|
| 1 | 資料來源 | HN + TechCrunch | 涵蓋中英文 |
| 2 | 輸出格式 | HTML（暗色主題） | 瀏覽器直開 |
| 3 | 觸發方式 | cron 08:00 + 手動 | 自動+手動 |
| 4 | 失敗策略 | fallback 快取 | 不能空白 |
```

---

## Step 2：產出 Spec（ark-superpowers）

### 操作

📝 拿到決策摘要後輸入：

```
根據以上決策摘要，幫我寫 spec
```

### 產出

`docs/specs/daily-news-spec.md`，包含：

| 章節 | 內容 |
|------|------|
| 目標與非目標 | 做什麼 / 不做什麼 |
| 功能需求 | 基於拷問決策的具體需求 |
| 非功能性需求 | 效能、可靠性、可維護性 |
| 成功指標 | 可量化的完成標準 |
| 驗收條件 | 測試通過的定義 |
| 開放問題 | 待決定事項 |

### 支援的文件類型

| 類型 | 觸發詞 | 產出路徑 |
|------|--------|---------|
| One Pager | 「簡短」、「one pager」 | docs/one-pagers/ |
| 完整 Spec | 「寫 spec」 | docs/specs/ |
| Design Doc | 「設計文件」 | docs/designs/ |
| ADR | 「架構決策」 | docs/designs/adr/ |

### 驗證

💻 確認檔案存在且結構完整：

```bash
cat docs/specs/daily-news-spec.md
```

---

## Step 3：產出 Skill（ark-skill-creator）

### 操作

📝 輸入：

```
建立新 Skill：每日科技新聞日報，根據 docs/specs/daily-news-spec.md 的規格實作
```

### 產出

```
.kiro/skills/my-daily-news/
├── SKILL.md              # 完整 Skill 指令
├── scripts/
│   └── fetch_rss.py      # RSS 抓取腳本
├── references/
│   └── rss-sources.md    # RSS 來源清單
└── evals/
    └── evals.json        # 評估測試集
```

### 驗證

💻 確認產出結構：

```bash
cat .kiro/skills/my-daily-news/SKILL.md | head -20
```

檢查：
- [ ] frontmatter 有 `name` 和 `description`
- [ ] description 涵蓋中文/英文/口語觸發詞
- [ ] body 步驟與 Spec 一致
- [ ] 有範例輸入/輸出

---

## Step 4：觸發測試 + 優化

### 測試觸發

📝 開新對話，測試：

```
幫我產出今天的科技新聞日報
```

觀察：Skill 是否被觸發？執行結果是否符合預期？

### 優化 description

📝 如果觸發率不理想：

```
幫我優化 my-daily-news Skill 的 description，增加觸發關鍵字
```

### 建立評估集

`evals/evals.json`：

```json
{
  "skill_name": "my-daily-news",
  "evals": [
    {"id": 1, "prompt": "幫我產出今天的科技新聞日報", "should_trigger": true},
    {"id": 2, "prompt": "今天天氣如何", "should_trigger": false},
    {"id": 3, "prompt": "RSS news summary", "should_trigger": true}
  ]
}
```

---

## Step 5：驗證 Code ↔ Spec（ark-code-spec-validator）

### 操作

📝 輸入：

```
驗證 code 跟 spec 一致嗎
```

### 產出

Drift Report（4 維度 × 0-100 評分）：

```
📊 Spec Drift Report — Score: 75/100

| 維度 | 分數 |
|------|------|
| ✅ API 端點 | 100/100 |
| ⚠️ Schema | 80/100 |
| ⚠️ 測試覆蓋 | 60/100 |
| ❌ 依賴 | 60/100 |

主要問題：
1. Spec 要求「失敗重試 3 次」但 code 只重試 1 次
2. 缺少 2 個驗收條件的測試

💡 建議：修復重試邏輯 + 補寫測試
```

### 4 維度說明

| 維度 | 比對內容 | 評分邏輯 |
|------|---------|---------|
| API 端點 | code route vs docs API 表格 | 100 - (drift × 5) |
| Schema | Pydantic model vs spec 定義 | 掃描 model 數量 |
| 依賴 | import graph vs design 規則 | 100 - (violations × 20) |
| 測試覆蓋 | spec 驗收條件 vs tests/ | covered / total × 100 |

### 解讀

- ✅ ≥ 90：無顯著 drift，可 Ship
- ⚠️ 70-89：有小問題，需修復
- ❌ < 70：嚴重漂移，需重新對齊

---

## Step 6：修復 + 迭代

### 修復

📝 根據 Drift Report：

```
修復 Drift Report 指出的問題
```

### 重新驗證

📝 再跑一次：

```
再跑一次 spec 驗證
```

目標：Score ≥ 90 → ✅ Ship。

### 完整迴圈圖

```
            ┌──── 設計有問題回來拷問 ────┐
            │                            │
拷問(grill) → Spec(superpowers) → Skill(creator) → 驗證(validator)
   L5 品質門檻    L5 知識沉澱       L4 執行          L4↔L5 驗證
```

---

## 使用的 4 個 Skill 對照表

| Skill | 觸發詞 | 角色 | 產出 |
|-------|--------|------|------|
| `ark-grill-me` | 「拷問我的設計」 | ① 釐清需求 | 決策摘要 |
| `ark-superpowers` | 「幫我寫 spec」 | ② 標準化 | spec.md |
| `ark-skill-creator` | 「建立新 Skill」 | ③ 實作 | SKILL.md |
| `ark-code-spec-validator` | 「驗證 code 跟 spec」 | ④ 驗證 | Drift Report |

---

## 反模式（常見錯誤）

| ❌ 反模式 | ✅ 正確做法 |
|-----------|------------|
| 跳過拷問直接寫 Skill | 先被拷問，釐清每個決策 |
| 拷問時全部回答 OK | 主動質疑、補充想法 |
| 沒有 Spec 就開始實作 | 先產出 Spec，再根據 Spec 寫 |
| 從不驗證 | 每次改動後跑 code-spec-validator |
| Drift Score < 70 就 Ship | 修復到 ≥ 90 再合併 |

---

## 進階主題

### Description 優化迴圈

```
產生 20 個評估查詢（10 應觸發 + 10 不應觸發）
→ 執行觸發測試
→ 分析 false positive / false negative
→ 重寫 description
→ 重測直到 100% 準確
```

### 評估迴圈（ark-skill-creator 內建）

```
產出 Skill → 建立 evals → 執行測試（有 Skill vs 無 Skill）
→ 評分 → 分析差異 → 改善 Skill → 重測
```

### Skill 分享

```bash
# .kiro/skills/ 隨 Git 版控
git add .kiro/skills/my-daily-news/
git commit -m "feat: add daily-news skill"
git push  # 團隊 pull 即可使用
```

---

## 常見問題

| 問題 | 解法 |
|------|------|
| Skill 沒被觸發 | description 加入更多觸發關鍵字（中/英/口語） |
| Skill 被錯誤觸發 | 加入「不適用於...」排除條件 |
| SKILL.md 太長（>500 行） | 移詳細內容到 references/ |
| 拷問太多題（30+） | 先拆解再逐一拷問 |
| Drift Score 很低 | 先修 code 或更新 Spec（保持同步） |
| Spec 產出太簡略 | 指定「完整版」而非 One Pager |

---

## 下一步

- **Workshop 03**：把驗證通過的 Skill 沉澱到 Wiki 知識庫（自演化循環）
- 對不同設計主題拷問（API、架構、重構）
- 用 ADR 記錄每次重要的架構決策
- 建立團隊 Skill Library + Spec 資產庫

---

*作者：paddyyang ｜ 更新：2026-06-23*
