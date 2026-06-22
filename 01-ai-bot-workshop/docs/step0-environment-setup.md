# Step 0：環境準備與 Skills 取得

> 使用 Skill：`ark-env-doctor`
> 觸發語句：「檢查我的開發環境」

---

## 1. 詢問時用的提詞

```
檢查我的開發環境
```

---

## 2. 常見問題

### 問題 A：無法透過 getUpdates 取得 Chat ID

**現象：** 呼叫 `https://api.telegram.org/bot<TOKEN>/getUpdates` 回傳空陣列 `{"ok": true, "result": []}`。

**原因：** 已有另一個 Bot polling 程序在消費 updates，所有 updates 都被該程序吃掉。

**解法：** 在 Telegram 搜尋 `@getmyid_bot`，對它發送 `/start`，回覆的就是你的 Chat ID。

### 問題 B：Gemini CLI 安裝後無法登入

**解法：**
```bash
npm install -g @google/gemini-cli
gemini    # 選 Login with Google → Gmail 登入
```

### 問題 C：Kiro CLI 安裝

```bash
npm install -g kiro-cli
kiro-cli login    # 瀏覽器授權
```

---

## 3. 檢查項目

| 項目 | 最低需求 | 確認方式 |
|------|---------|---------|
| Python | 3.12+ | `python --version` |
| pip / uv | 已安裝 | `pip --version` |
| Git | 已安裝 | `git --version` |
| Node.js | 20+ | `node --version` |
| Gemini CLI | 已安裝 + 登入 | `gemini --version` |
| Kiro CLI | 已安裝 + 登入 | `kiro-cli --version` |
| Telegram Bot Token | 已取得 | 從 @BotFather 取得 |
| Gemini API Key | 已取得 | https://aistudio.google.com/apikeys |

---

## 4. Skills 取得

```bash
# Kiro 使用者
git clone https://github.com/igs-paddyyang-tw/ark-agent-skills .kiro/skills/

# Antigravity 使用者
git clone https://github.com/igs-paddyyang-tw/ark-agent-skills .agents/skills/
```

**repo 內容：** 47 個 Ark Skills，涵蓋本教學所有步驟。

---

## 5. 產出

- 環境診斷報告（pass/fail 清單）
- 缺失項目的安裝建議指令
- `.env.example` 所需環境變數提示

**範例輸出：**
```
── Environment Check ──────────
✅ Python: 3.12.4
✅ uv: 0.7.x
✅ Git: 2.45.x
✅ Node.js: 22.19.0
⚠️ TELEGRAM_BOT_TOKEN: 未設定（Step 2 需要）
⚠️ GEMINI_API_KEY: 未設定（Step 4 需要）
────────────────────────────────
環境就緒，可進入 Step 1。
```

---

## 6. 完成標準

- [x] Python / Git / Node.js 版本正確
- [x] Gemini CLI 已安裝 + Gmail 登入
- [x] Kiro CLI 已安裝 + 授權
- [x] 已取得 Telegram Bot Token
- [x] Skills repo 已 clone 到正確位置

---

*Step 0 完成，環境就緒，可進入 Step 1。*
