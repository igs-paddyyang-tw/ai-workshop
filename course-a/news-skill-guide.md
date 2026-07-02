# 科技日報 Skill 開發實戰（從 01 移過來的補充教材）

> 本檔是 01 的爬蟲+日報內容移到 02 作為 Spec-Driven 開發的實戰範例。

---

## 🎯 NewsSkill 開發目標

將 01 的簡易新聞技能升級為生產級 Skill，具備：

| 能力 | 說明 |
|------|------|
| 多來源並發 | 同時爬取 3+ 新聞來源，asyncio 並發執行 |
| 失敗重試 | 單一來源失敗不影響整體，自動 retry 3 次 |
| 結構化 JSON | 統一輸出格式，前端可直接渲染卡片 |

---

## 📄 Mock 資料參考

使用 `structured-example.json` 作為開發時的 mock 資料：

```bash
cat 02-skills-workshop/structured-example.json
```

此 JSON 包含完整的新聞卡片結構（topic、title、what、why、tags），
開發時可先用此 mock 確認格式正確，再接入真實爬蟲。

---

## 🔄 Spec-Driven 開發流程

要用 Spec-Driven 方式開發：**先拷問 → 寫 Spec → 實作 → 驗證**

```
1. 拷問設計：這個 Skill 要解決什麼？邊界在哪？錯誤怎麼處理？
2. 寫 Spec：定義 input/output schema + 錯誤碼 + 效能需求
3. 實作：依照 Spec 逐項實作，不多不少
4. 驗證：用 mock 資料 + 真實 API 雙重驗證 Spec 一致性
```

> 💡 這就是 02 的核心方法論 — 從「寫得動」升級到「寫得對」。
