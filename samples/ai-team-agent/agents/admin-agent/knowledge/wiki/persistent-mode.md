# 常駐模式（Persistent Mode）操作說明

## 概述

常駐模式讓 Agent 以長駐子進程運行，透過 stdin/stdout pipe 持續接收任務，
免去每次 spawn 的 2-5 秒冷啟動延遲。

## 關鍵技術

- **`--legacy-ui`**：必須使用此 flag，否則 stdout 為空
- **`stderr=STDOUT`**：合併到單一 stream 讀取
- **Ready 偵測**：正則匹配 `"All tools are now trusted"` / `"ctrl-c to start chatting now"`
- **結束標記**：`"▸ Time:"` 出現在每次回答末尾
- **Graceful stop**：`/quit` 命令

## 設定（team.yaml）

```yaml
defaults:
  persistent: true        # 全域啟用
  
instances:
  admin-agent:
    persistent: true      # per-instance override
    skip_resume: true     # 每次啟動新 session
```

## 架構

```
PersistentDaemon
├── ManagedProcess (per agent)
│   ├── stdin pipe → 寫入任務
│   ├── stdout pipe → ring buffer (500 行)
│   └── kill / restart
├── Health Loop (30s)
│   ├── 崩潰偵測 → 自動重啟（指數退避）
│   ├── Rate limit → soft-pause 90s
│   └── Error pattern → FailureMemory
├── Queue Worker (per agent)
│   ├── asyncio.Queue(maxsize=50)
│   └── overflow → SQLite 持久化
└── Heartbeat (30s → state/heartbeat)
```

## 常見問題

### Agent 無回應

1. 檢查 `state/heartbeat` 是否過期（> 90s）
2. 查看 `process.capture()` 最近輸出
3. 嘗試 `restart_instance(name)`

### Rate limit

- 連續 3 次 rate_limit → 自動 soft-pause 90 秒
- 不 kill 進程，等待 retry-after 自行恢復

### MCP 工具沒載入

- 系統自動偵測 mcp.json hash 變更 → skip_resume（新 session）
- 手動修正：設定 `skip_resume: true` 後重啟
