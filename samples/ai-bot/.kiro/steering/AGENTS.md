# AGENTS.md — 全域行為準則（多 CLI 共用 SSOT）

> 這份是**跨 CLI 的單一真相來源**：Kiro CLI 讀 `.kiro/steering/`、
> Claude Code 讀 `CLAUDE.md`、Codex / Cursor 讀 `AGENTS.md`。
> 要讓它們共用同一份規範，就讓其他入口**連結**到這裡，不要各自維護三份。

## 這個專案是什麼

`ark_bot_agent` 套件的**消費端**。框架（runtime / Web UI / 記憶 / 四層搜尋 /
TG polling）都在套件裡，本目錄只有**設定與人格**。

## 三個設定檔的分工（不合併）

| 檔 | 職責 |
|----|------|
| `agents.yaml` | 有誰（agent 定義）← 專案根哨兵 |
| `bot.yaml` | 怎麼跑（server / modes / llm / backend / report / features） |
| `.env` | 只放機密（TG token / API key） |

## 紅線

- 🚫 不要在這個專案手搭 runtime —— 套件已經有了，兩套並存必漂移
- 🚫 不要在 `agents.yaml` 自創欄位 —— **未知欄位會被靜默丟掉**，
  約束要寫進 `desc` 或該 agent 的 `SOUL.md`
- 🚫 不要把 token 寫進 `memory/` 或知識庫
- 🚫 知識庫頁面由 ingest 產出，不手寫進 `knowledge/shared/wiki/`

## 產出落點

| 類型 | 路徑 |
|------|------|
| 規格 / 設計 / 計畫 | `docs/specs` · `docs/designs` · `docs/plans` |
| 報告 | `artifacts/reports/` |
| 知識素材 | `knowledge/shared/raw/` → ingest → `knowledge/shared/wiki/` |
| 記憶 | `memory/`（daily / recent.md / memory.md） |
