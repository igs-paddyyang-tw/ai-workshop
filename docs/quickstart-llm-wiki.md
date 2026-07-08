# LLM Wiki 知識庫 — 簡易安裝與使用教學

> 3 分鐘在 Kiro IDE 裡建好一個 AI 知識庫，讓你的 Agent 有記憶、能引用。

---

## 前置條件

- Kiro IDE 已安裝並登入
- 有一個空資料夾（或現有 ai-bot 專案）

---

## 開始：打開 Kiro IDE 對話

啟動 Kiro IDE，開啟你的專案資料夾，進入 Chat 對話框。

### 用 Skill 建立專案目錄

在對話框輸入：

```
幫我用 ark-wiki-engine 建立 Wiki 知識庫系統
```

> 💡 **Skill 來源**：https://github.com/igs-paddyyang-tw/ark-agent-skills/blob/main/ark-wiki-engine/SKILL.md
>
> Kiro IDE 會根據這份 Skill 規格，自動產出完整的目錄結構和程式碼。

完成後你的專案會多出：

```
knowledge/
├── raw/          ← 放原始資料（教學檔案放這裡）
├── wiki/         ← AI 整理後的知識頁面
├── schema.md     ← 知識庫規則
├── index.md      ← 索引目錄
└── log.md        ← 操作日誌
```

### 下載教學檔案

在對話框輸入：

```
幫我下載以下教學範例放到 knowledge/raw/：
1. Ocean King 捕魚機競品分析
2. Super Ace 老虎機競品分析
3. 捕魚機 vs 老虎機比較
```

或手動放入任何 `.md` 檔案到 `knowledge/raw/` 資料夾。

---

## 步驟 1：將教學檔案放到 raw

在 Kiro IDE 左側檔案樹確認 `knowledge/raw/` 裡有檔案：

```
knowledge/raw/
├── ocean-king-analysis.md
├── super-ace-analysis.md
└── fishing-vs-slot-comparison.md
```

如果要自己加資料，直接把任何 `.md` 拖進 `knowledge/raw/` 即可。

> ⚠️ `raw/` 是唯讀區 — AI 只讀不改。這是你的「原始素材庫」。

---

## 步驟 2：匯入到 Wiki

在 Kiro IDE 對話框輸入：

```
匯入知識
```

或更具體：

```
把 raw 資料夾的檔案匯入 wiki
```

Kiro IDE 會：
1. 讀取 `knowledge/raw/` 裡的所有 `.md`
2. 自動補上 frontmatter（title、type、tags、日期）
3. 產出結構化頁面到 `knowledge/wiki/`
4. 更新 `knowledge/index.md` 索引
5. 追加記錄到 `knowledge/log.md`

完成後會回覆類似：

```
✅ 匯入完成：3 篇
• ocean-king-analysis.md
• super-ace-analysis.md
• fishing-vs-slot-comparison.md
```

---

## 步驟 3：查詢 Wiki

在 Kiro IDE 對話框直接問問題：

```
Ocean King 的核心玩法是什麼？
```

```
老虎機和捕魚機的目標玩家有什麼差異？
```

```
Super Ace 的 RTP 是多少？
```

Kiro IDE 會：
1. 搜尋 `knowledge/wiki/` 裡的相關頁面
2. 擷取包含答案的段落
3. 組合回答，並附上參考來源

回覆格式：

```
[回答內容...]

---
📚 參考：ocean-king-analysis, fishing-vs-slot-comparison
```

---

## 其他操作（進階）

| 在對話框說 | 做什麼 |
|-----------|--------|
| `檢查 Wiki` 或 `lint` | 健康檢查 — 找出缺少欄位、孤立頁面 |
| `Wiki 有沒有 XXX` | 搜尋知識庫 |
| `記錄：[任何內容]` | 新增一頁知識到 wiki |
| `更新 [頁面名稱]` | 修改現有知識頁面 |

---

## 總結

```
┌─────────────────────────────────────────────┐
│                                             │
│   raw/（你放素材）                           │
│       │                                     │
│       ↓  「匯入知識」                        │
│                                             │
│   wiki/（AI 整理的知識頁面）                  │
│       │                                     │
│       ↓  直接問問題                          │
│                                             │
│   💬 AI 回答（附參考來源）                    │
│                                             │
└─────────────────────────────────────────────┘
```

**全程在 Kiro IDE 對話框操作，不需要打指令、不需要寫程式。**
