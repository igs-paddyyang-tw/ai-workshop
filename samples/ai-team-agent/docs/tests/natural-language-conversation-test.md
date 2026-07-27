---
title: "自然語言對話測試清單"
type: test
status: active
created: 2026-07-27
version: "1.0"
scope: ai-team-agent (post leader-agent rename)
---

# 自然語言對話測試清單

> 適用版本：leader-agent 更名後（commit `a8c5b99`）  
> 服務啟動：`python start.py`，確認 `✅ Ark Agent Platform 全部服務已啟動`

---

## 前置條件

| 條件 | 確認方式 |
|------|---------|
| 服務啟動 | `logs/platform.log` 最後一行含「全部服務已啟動」|
| 8 agents 就緒 | log 顯示 `✅ leader-agent`、`✅ admin-agent` |
| TG Bot 連線 | `Telegram Bot 已啟動` |
| allowed_users 設定 | log 顯示 `allowed_users: [你的ID]` |

---

## 一、基礎路由（預設 → leader-agent）

不帶 `@`，應由 `leader-agent` 接收。

| # | 輸入訊息 | 預期行為 | 驗收標準 |
|---|---------|---------|---------|
| T01 | `你好，介紹一下團隊成員有誰、各自負責什麼` | leader-agent 回覆 | 回覆含 8 個 agent 名稱與職責 |
| T02 | `直` | leader-agent 查詢任務板 | 回覆任務清單或「目前無進行中任務」|
| T03 | `幫我整理今天完成了什麼` | leader-agent 摘要今日工作 | 有實質內容，非空白回覆 |

---

## 二、@mention 指定 agent

帶 `@agent-name`，直接送指定 agent。

| # | 輸入訊息 | 目標 Agent | 特別觀察 |
|---|---------|-----------|---------|
| T04 | `@leader-agent 請確認你的角色和職責` | leader-agent | 驗證更名後 @leader-agent 有效（非舊的 @pm-agent）|
| T05 | `@admin-agent 平台現在運行狀態如何？` | admin-agent | admin 直接回覆，不經 leader-agent |
| T06 | `@coder-agent 幫我寫一個 Python function，接受 list 回傳去重後排序的結果` | coder-agent | **首次呼叫**：出現「⏳ 正在啟動 coder-agent」通知 |
| T07 | `@qa-agent 針對去重排序 function，設計 3 個 pytest 測試案例` | qa-agent | lazy spawn 通知 + 測試案例回覆 |
| T08 | `@ai-dev-agent RAG 架構中 chunk size 如何選擇？` | ai-dev-agent | 技術說明，長度合理（> 50 字）|
| T09 | `@market-agent 搜尋最近一週 Claude AI 的重要更新` | market-agent | 回覆近期 Claude 相關資訊 |
| T10 | ` | data-agent | 有分析內容，含具體觀察 |
| T11 | `@report-agent 幫我產出一份今日工作摘要，使用 Markdown 格式` | report-agent | 回覆含 Markdown 標題與列表 |

---

## 三、A2A 派工流程（leader → worker）

leader-agent 接收後自動分析並派給合適 worker。

| # | 輸入訊息 | 預期派工路徑 | 驗收標準 |
|---|---------|------------|---------|
| T12 | `幫我開發一個 REST API：GET /api/health 回傳 {"status": "ok"}` | leader → coder-agent | 最終回覆含 FastAPI / Flask 程式碼 |
| T13 | `我想做一份競品分析：比較 Claude、GPT-4、Gemini 的最新功能差異` | leader → market-agent | 回覆含三者功能對比 |

---

## 四、關鍵行為驗收

### T14 — Lazy Spawn 通知

```
@coder-agent 你好
（在 coder-agent 已被 evict 或首次啟動時執行）
```

| 步驟 | 預期 |
|------|------|
| 送出訊息 | TG 出現「⏳ 正在啟動 coder-agent，請稍候...」|
| 10-15 秒後 | coder-agent 回覆 |
| reaction | 👀 → 👍 |

---

### T15 — 超時機制（可選，需等 5 分鐘）

```
@leader-agent 請仔細分析整個系統架構，給出所有層次的完整優化建議，不限長度
```

| 步驟 | 預期 |
|------|------|
| 300 秒內無回覆 | TG 出現「⚠️ leader-agent 處理超時（未回覆）」|
| reaction | 👀 → 👎 |

---

### T16 — 白名單保護（需用非白名單帳號測試）

```
/start
（用另一個 TG 帳號，或暫時清空 .env ALLOWED_USERS）
```

| 預期 |
|------|
| 顯示「🔒 需要白名單權限」|
| 顯示「你的 Chat ID：`{uid}`」|
| 顯示「請在 team.yaml → access.allowed_users 加入此 ID」|

---

## 五、TG 指令搭配驗證

| # | 指令 | 預期 | 驗收標準 |
|---|------|------|---------|
| T17 | `/mode` | Tier 顯示 | Tier 0-3 全 ✅，Current Tier: 3，**無 Tier 2 LLM** |
| T18 | `/status` | 團隊狀態卡片 | 顯示 leader-agent（非 pm-agent），8 agent 狀態 |
| T19 | `/agents` | Agent 列表 | 顯示 leader-agent，可點擊查詳情 |
| T20 | `/board` | 任務看板 | pending/assigned/completed 分組顯示 |
| T21 | `/costs` | 費用報告 | total_usd + by_agent 分組（無 crash）|
| T22 | `/assign 建立 SQLite 備份腳本` | 建立 Issue + 選 Agent | Issue 建立成功，Agent 選單含 leader-agent |
| T23 | `/recall 部署` | 查詢 leader-agent 記憶 | 有結果或「沒有相關記憶」（無 crash）|
| T24 | `/recall 任務` | 同上 | 同上 |
| T25 | `/help` | 指令說明 | 顯示「直接打字 → leader-agent 接收」（非 pm-agent）|

---

## 六、觀察指標彙整

| 指標 | 觀察方式 | 通過標準 |
|------|---------|---------|
| 更名路由正確 | 自然語言訊息 → 確認 log `📨 user=xxx → leader-agent` | `leader-agent` 非 `pm-agent` |
| Lazy spawn 通知 | 第一次傳訊給 worker | TG 出現 `⏳ 正在啟動...` |
| TG 通知格式 | 任務完成時 | `#真實8碼ID — 標題`，非 `#?` |
| reaction 流程 | 每次訊息 | 收訊 → 👀，完成 → 👍，失敗 → 👎 |
| typing 指示 | 送出訊息後 | TG 顯示「正在輸入...」|
| /mode Tier | `/mode` 指令 | 顯示 4 層（0-3），無 LLM Tier |
| agent 名稱 | `/status` / `/agents` | 顯示 `leader-agent`，無 `pm-agent` |

---

## 已知限制

| 項目 | 說明 |
|------|------|
| A2A reply_to | 目前用 `[A2A]` header 格式，worker 完成後是否自動回報 leader 需人工觀察 |
| last_heartbeat | `GET /api/agents/{id}/health` 的 `last_heartbeat` 欄位回 None（待整合）|
| idle evict | worker agent 閒置 10 分鐘後自動停止（`IDLE_TIMEOUT_MINUTES=10`），再次呼叫會重新 lazy spawn |

---

## 執行記錄欄位

| # | 執行日期 | 執行人 | T01 | T02 | T03 | T04 | T05 | T06 | T07 | T08 | T09 | T10 | T11 | T12 | T13 | T17-T25 | 備註 |
|---|---------|--------|-----|-----|-----|-----|-----|-----|-----|-----|-----|-----|-----|-----|-----|---------|------|
| 1 | 2026-07-27 | CTO | | | | | | | | | | | | | | | 首次執行 |
