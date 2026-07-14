# admin-agent 持久事實

> 上限 2000 tokens。

## 常駐化完成（2026-07-14）

- 進程模式：persistent（--legacy-ui + stdin pipe）
- 5 agents 全部常駐就緒，Tier 4 滿載
- Health Loop 30 秒巡檢、自動重啟（指數退避 + cooldown）
- MCP hash 偵測：config 變更 → 強制新 session
- 切換方式：`team.yaml` → `defaults.persistent: false` 回到 spawn

## 關鍵技術細節

- Ready pattern: "ctrl-c to start chatting now" / "All tools are now trusted"
- 結束標記: "▸ Time:"
- Graceful stop: /quit → code=0
- Pipe 保護: BrokenPipeError → 標記 _pipe_broken → health loop 重啟

