# 🚀 第一堂：Agent 初始 — 它能「說話」

## 🎯 課堂目標

完成後你能：
1. 理解 SOUL.md 如何控制 Agent 人格與回應風格
2. 用 Inline Button 切換不同 Agent 對話，體驗多人格系統
3. 動手修改 SOUL 改變 Bot 風格，即時看到效果
4. 理解 Planner 三層意圖路由的邏輯（關鍵字 → Skill → LLM）

## 📋 前置條件

- Python 3.10+、pip、虛擬環境（venv）
- Telegram Bot Token（跟 @BotFather 申請）
- 文字編輯器（VS Code / Cursor / Vim）
- 約 50 分鐘完整時間

---

## Step 1：啟動 Bot（0-5 min）

**做什麼**：啟動 AI Bot 範例專案  
**為什麼**：確認環境正常，才能進行後續實驗

```bash
cd samples/ai-bot
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # 編輯填入 BOT_TOKEN
python start.py
```

**✅ 預期結果**：終端顯示 `✓ Skills loaded: 5` + `Bot polling started`  
**⚠️ 如果不成功**：`No module` → 確認已啟用 venv；Bot 沒回應 → 確認 `.env` 中 Token 正確

---

## Step 2：切換 Agent 體驗（5-15 min）

**做什麼**：用 Telegram 切換不同 Agent，觀察人格差異  
**為什麼**：親身感受「同一系統、不同人格」的效果

**操作**：
1. 在 Telegram 輸入 `/agents`，出現 Inline Button 選單
2. 點 **Admin** → 問「你是誰」
3. 點 **Coder** → 問同一問題「你是誰」
4. 點 **Market** → 問「今天新聞」

**✅ 預期結果**：Admin 簡潔專業、Coder 技術導向、Market 觸發 NewsSkill 回傳新聞列表  
**⚠️ 如果不成功**：按鈕沒出現 → 確認 Bot 有 inline button 權限；回答都一樣 → 確認 agents/ 目錄結構完整

---

## Step 3：修改 SOUL（15-30 min）⭐ 核心體驗

**做什麼**：改寫 SOUL.md 的人格描述，重啟觀察變化  
**為什麼**：證明 SOUL.md 是控制 Agent 行為的唯一入口

**操作**：
1. 打開 `agents/admin-agent/.kiro/steering/SOUL.md`
2. 找到人格描述段落，改成「你是一位幽默搞笑的助手，喜歡用諧音梗回答」
3. 重啟 Bot（Ctrl+C → `python start.py`）
4. 再問「你是誰」

**✅ 預期結果**：回答風格明顯帶幽默感，其他 Agent 不受影響  
**⚠️ 如果不成功**：風格沒變 → 確認存檔並重啟；改錯檔案 → 確認路徑是 admin-agent  
**🔥 延伸挑戰**：改成「海盜船長」或「貓咪助手」觀察更戲劇性的變化

---

## Step 4：理解路由（30-40 min）

**做什麼**：閱讀 Planner 程式碼，理解三層意圖路由  
**為什麼**：知道訊息怎麼被分配到對應 Skill

**操作**：
1. 打開 `src/agent/planner.py`
2. 找到 `KEYWORD_ROUTES` 字典
3. 觀察對應關係

**✅ 預期結果**：看到 `"新聞"` → news skill、`"wiki"` → WikiEngine 等映射  
**⚠️ 如果不成功**：找不到檔案 → 用 `grep -r "KEYWORD_ROUTES" src/` 搜尋  
**💡 理解重點**：三層降級 = 關鍵字精確匹配 → Skill 模糊匹配 → LLM fallback 兜底

---

## Step 5：動手加路由（40-50 min）

**做什麼**：新增一條路由規則，讓 Bot 能處理「翻譯」指令  
**為什麼**：驗證你已理解路由機制，能自己擴充功能

**操作**：
1. 在 `KEYWORD_ROUTES` 字典中加入：`"翻譯": (IntentType.SKILL, "translate")`
2. 重啟 Bot
3. 輸入「翻譯 hello」

**✅ 預期結果**：觸發 translate skill，回傳含 `[en] hello` 的翻譯結果  
**⚠️ 如果不成功**：沒觸發 → 確認關鍵字拼寫一致（翻譯 vs 翻譯）；確認已重啟

---

## 📊 完成度分級

| 等級 | 達成條件 |
|------|----------|
| ⭐ 基礎 | 完成 Step 1-2，Bot 能跑、能切換 Agent |
| ⭐⭐ 標準 | 完成 Step 3，成功改 SOUL 看到風格變化 |
| ⭐⭐⭐ 進階 | 完成 Step 4-5，能解釋路由並自己加新路由 |

## 🏠 回家練習

1. 為 3 個 Agent 各寫一份獨特的 SOUL.md（至少 50 字人格描述）
2. 在 KEYWORD_ROUTES 多加 2 條自訂路由
3. 思考：如果你要做一個「客服 Agent」，SOUL.md 該怎麼寫？
