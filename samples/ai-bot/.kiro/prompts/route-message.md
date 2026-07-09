# 意圖路由

判斷使用者意圖，選擇最佳執行路徑：

| 意圖 | 觸發條件 | 路由目標 |
|------|---------|----------|
| Skill 執行 | 符合已註冊 Skill 的 description 關鍵詞 | 對應 Skill |
| 知識查詢 | wiki/知識庫/查知識/recall | WikiEngine 或 Memory Recall |
| 文件產出 | spec/design/plan/ADR/規格/設計 | ark-superpowers Skill |
| 設計拷問 | grill/拷問/質疑設計/review plan | ark-grill-me Skill |
| 程式碼實作 | 寫/改/修/加/刪 + 程式碼相關描述 | 直接實作 |
| 一般對話 | 其他 | Gemini Chat |
