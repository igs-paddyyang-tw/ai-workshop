# LLM Wiki 知識庫 — 簡易安裝與使用教學

> 3 分鐘在 Kiro IDE 裡建好一個 AI 知識庫，讓你的 Agent 有記憶、能引用。

---

## 前置條件

- Kiro IDE 已安裝並登入
- 有一個空資料夾（或現有 ai-bot 專案）

---

## 開始：打開 Kiro IDE 對話

啟動 Kiro IDE，開啟你的專案資料夾，進入 Chat 對話框。

### 初始化（一次貼完，AI 全部跑完）

複製以下整段文字，貼到對話框送出：

```
1. 幫我下載 https://github.com/igs-paddyyang-tw/ark-agent-skills/blob/main/ark-wiki-engine/SKILL.md 放到 .kiro/skills/ark-wiki-engine/SKILL.md
2. 幫我建立 .kiro/steering/SOUL.md，角色是「遊戲產業知識管理專家」，擅長整理競品分析、市場趨勢、玩法設計等知識，回答時引用知識庫來源。
3. 幫我用 ark-wiki-engine 建立 Wiki 知識庫系統
4. 幫我下載 https://github.com/igs-paddyyang-tw/ai-workshop/blob/main/docs/quickstart-llm-wiki.md 放到 knowledge/raw/quickstart-llm-wiki.md
```

> 💡 一段話 4 件事，AI 會依序完成：下載 Skill → 建立角色 → 產出知識庫目錄 → 下載範例素材。

完成後你的專案結構：

```
your-project/
├── .kiro/
│   ├── steering/
│   │   └── SOUL.md                 ← Agent 人格（遊戲產業知識管理專家）
│   └── skills/
│       └── ark-wiki-engine/
│           └── SKILL.md            ← Wiki 知識庫 Skill 規格
├── knowledge/
│   ├── raw/
│   │   └── quickstart-llm-wiki.md  ← 範例素材（就是這份教學）
│   ├── wiki/                        ← AI 整理後的知識頁面
│   ├── schema.md                    ← 知識庫規則
│   ├── index.md                     ← 索引目錄
│   └── log.md                       ← 操作日誌
└── src/
    └── ...                          ← Wiki 引擎程式碼
```

| 產出 | 用途 |
|------|------|
| `SOUL.md` | 決定 Agent「用什麼語氣、什麼角度」回答問題 |
| `SKILL.md` | Kiro IDE 對話時自動參考的 Wiki 建構規格 |
| `knowledge/raw/` | 你放原始素材的地方（AI 只讀不改） |
| `knowledge/wiki/` | AI 整理後的結構化知識頁面 |

---

## 步驟 1：將教學檔案放到 raw

在 Kiro IDE 左側檔案樹確認 `knowledge/raw/` 裡有檔案：

```
knowledge/raw/
└── quickstart-llm-wiki.md    ← 剛才下載的這份教學
```

想加更多？在對話框說：

```
📂 knowledge/raw/ 幫我建立一份「Ocean King 捕魚機競品分析」的範例文件
```

> ⚠️ `raw/` 是唯讀區 — AI 只讀不改。這是你的「原始素材庫」。

---

## 步驟 2：匯入到 Wiki

在 Kiro IDE 對話框輸入：

```
📂 knowledge/ 把 raw 資料夾的檔案匯入 wiki
```

或簡單說：

```
匯入知識
```

Kiro IDE 會：
1. 讀取 `knowledge/raw/` 裡的所有 `.md`
2. 自動補上 frontmatter（title、type、tags、日期）
3. 產出結構化頁面到 `knowledge/wiki/`
4. 更新 `knowledge/index.md` 索引
5. 追加記錄到 `knowledge/log.md`

完成後會回覆類似：

```
✅ 匯入完成：1 篇
• quickstart-llm-wiki.md
```

你可以在檔案樹看到新增的 wiki 頁面：

```
knowledge/wiki/
└── quickstart-llm-wiki.md    ← AI 整理後的版本（有 frontmatter）
```

---

## 步驟 3：查詢 Wiki

在 Kiro IDE 對話框直接問問題：

```
📂 knowledge/ Wiki 知識庫怎麼使用？
```

```
📂 knowledge/ raw 和 wiki 的差別是什麼？
```

```
📂 knowledge/ 怎麼匯入新的知識？
```

Kiro IDE 會：
1. 搜尋 `knowledge/wiki/` 裡的相關頁面
2. 擷取包含答案的段落
3. 組合回答，並附上參考來源

回覆格式：

```
[回答內容...]

---
📚 參考：quickstart-llm-wiki
```

---

## 其他操作（進階）

| 在對話框說 | 做什麼 |
|-----------|--------|
| `📂 knowledge/` + `檢查 Wiki` | 健康檢查 — 找出缺少欄位、孤立頁面 |
| `Wiki 有沒有 XXX` | 搜尋知識庫 |
| `📂 knowledge/wiki/` + `記錄：[內容]` | 新增一頁知識 |
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

---

## 本文件作為範例素材

這份 `quickstart-llm-wiki.md` 本身就是一份知識文件。把它放進 `knowledge/raw/` 後匯入 Wiki，未來你問「怎麼用 Wiki」時，AI 就能直接引用這份教學來回答。

> 🔗 來源：https://github.com/igs-paddyyang-tw/ai-workshop/blob/main/docs/quickstart-llm-wiki.md
