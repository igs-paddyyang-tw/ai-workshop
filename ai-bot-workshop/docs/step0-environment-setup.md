# Step 0：環境設置紀錄

> 日期：2026-05-29

---

## 1. 詢問時用的提詞

```
我現在想先從Step 0 的環境建設開始，你幫我逐個檢查一遍，
CLI用Kiro的就夠了，幫我確認基礎工具安裝及搞定Telegram Bot的相關設定就好，
我現在有個Bot 的Token為 8991505360:AAEDdnhVseUTI-hMuHCJ0S7ZmE1e_nLVeq8，幫我開始設定
```

---

## 2. 遇到的問題

### 問題 A：無法透過 getUpdates 取得 Chat ID

**現象：** 呼叫 `https://api.telegram.org/bot<TOKEN>/getUpdates` 回傳空陣列 `{"ok": true, "result": []}`，即使使用者已對 Bot 發送訊息。

**原因：** 使用者已有另一個 Bot polling 程序在運行中（該程序會即時回覆 `/start`、`/status` 等指令），所有 updates 都被該程序消費掉，導致 API 查詢永遠拿不到新訊息。

---

## 3. 解決方法

**方案：使用第三方 Bot 取得 Chat ID**

請使用者在 Telegram 搜尋 `@getmyid_bot`，對它發送 `/start`，該 Bot 會回覆使用者的 Chat ID。

取得 Chat ID 後，手動填入 `.env` 檔案的 `TELEGRAM_CHAT_ID` 欄位。

---

## 4. 結果

### 環境檢查結果

| 項目 | 狀態 | 版本 / 值 |
|------|------|-----------|
| Python | ✅ 通過 | 3.12.10 |
| pip | ✅ 通過 | 26.0.1 |
| Git | ✅ 通過 | 2.45.1 |
| Node.js | ✅ 通過 | 22.19.0 |
| npm | ✅ 通過 | 10.9.3 |

### Telegram Bot 設定結果

| 項目 | 狀態 | 值 |
|------|------|---|
| Bot Token 驗證 | ✅ 有效 | `getMe` 回傳正確 |
| Bot 名稱 | ✅ | TAIYIBOT |
| Bot Username | ✅ | @taiyi_ark_bot |
| Chat ID | ✅ 取得 | 8523602047 |
| 推送測試 | ✅ 成功 | `sendMessage` API 回傳 OK |

### 產出檔案

- `ai-bot/.env` — 已填入 Token 和 Chat ID，可直接使用

```
TELEGRAM_BOT_TOKEN=8991505360:AAEDdnhVseUTI-hMuHCJ0S7ZmE1e_nLVeq8
TELEGRAM_CHAT_ID=8523602047
NEWS_SCHEDULE_CRON=0 9 * * *
NEWS_TIMEZONE=Asia/Taipei
LOG_LEVEL=INFO
```

---

*Step 0 完成，環境就緒，可進入 Step 1。*
