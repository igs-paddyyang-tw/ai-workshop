# Step 0：環境準備（5 min）

> 進階班前置作業：確認工具已安裝、取得 API Key 與 Bot Token。

---

## 1. 詢問時用的提詞

```
檢查我的開發環境
```

---

## 2. 常見問題

### 問題 A：無法透過 getUpdates 取得 Chat ID

**現象：** 呼叫 `https://api.telegram.org/bot<TOKEN>/getUpdates` 回傳空陣列。

**原因：** 已有另一個 Bot polling 程序在消費 updates。

**解法：** 在 Telegram 搜尋 `@getmyid_bot`，對它發送 `/start` 取得 Chat ID。

### 問題 B：Gemini API Key 無效或額度耗盡

**解法：**
1. 前往 https://aistudio.google.com/apikeys
2. 點擊「Create API Key」→ 複製
3. 免費額度：60 req/min、1,000 req/day

---

## 3. 前提條件

| 項目 | 要求 | 確認方式 |
|------|------|---------|
| Python | 3.12+ | `python --version` |
| Git | 任意版本 | `git --version` |
| Node.js | 20+ | `node --version` |
| Telegram Bot Token | 從 @BotFather 取得 | 填入 `.env` |
| Gemini API Key | 從 AI Studio 取得 | 填入 `.env` |
| AI IDE | Kiro 或 Antigravity | 已安裝並登入 |

---

## 4. Skills 取得

```bash
# Kiro 使用者
git clone https://github.com/igs-paddyyang-tw/ark-kiro-skills .kiro/skills/

# Antigravity 使用者
git clone https://github.com/igs-paddyyang-tw/ark-kiro-skills .agents/skills/
```

---

## 5. 完成標準

- [x] Python / Git / Node.js 版本正確
- [x] 已取得 Telegram Bot Token
- [x] 已取得 Gemini API Key
- [x] Skills repo 已 clone 到正確位置
- [x] AI IDE 環境檢查全部通過

---

*Step 0 完成，環境就緒，可進入 Step 1。*
