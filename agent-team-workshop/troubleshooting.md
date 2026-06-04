# 故障排除

> 常見問題與解法。

---

## 環境問題

| 問題 | 解法 |
|------|------|
| `start-team.bat` 執行失敗 | 確認 Python 和 kiro-cli 在 PATH |
| `kiro-cli not found` | 確認 kiro-cli 在 PATH，執行 `kiro-cli --version` |
| Python 版本不對 | 需要 3.11+，`python --version` 確認 |
| `pip install` 失敗 | 確認在專案目錄下，`pip install -r requirements.txt` |

## Telegram 問題

| 問題 | 解法 |
|------|------|
| Bot 沒回應 | 確認 Bot 在群組裡且是 Admin |
| 找不到 group_id | 群組發訊息後 `curl "https://api.telegram.org/bot{TOKEN}/getUpdates"` |
| 找不到 topic_id | 在 Topic 裡發訊息，看 getUpdates 的 `message_thread_id` |
| Bot 只回一個 agent | 確認 team.yaml 的 `topic_id` 對應正確 |
| 純私聊模式沒反應 | 確認 `access.allowed_users` 有你的 user ID |

## 啟動問題

| 問題 | 解法 |
|------|------|
| Instance 啟動超時 | 查看 `logs/team.log`，確認 kiro-cli 可用 |
| Port 被佔用 | 改 `health_port`（預設 **13030**，第二個團隊用 23030） |
| 崩潰重啟循環 | 確認 `working_directory` 路徑存在 |
| MCP 工具失敗 | `curl http://127.0.0.1:13030/api/status` 確認 daemon 在跑 |
| 編碼錯誤 | 已內建 surrogate 防護，重啟即可 |
| admin mcp.json 是空 `{}` | 重新執行 `build_kiro.py`（會自動覆蓋空的 mcp.json） |

## 費用問題

| 問題 | 解法 |
|------|------|
| 費用超限暫停 | 調高 `cost_guard.daily_limit_usd` 或等隔天 |
| 想省錢 | 簡單任務用 `model: claude-haiku-4.5`，核心用 sonnet |
| 忘記關 | 設 daily_limit，或關閉 start-team.bat 視窗 |

## 配置問題

| 問題 | 解法 |
|------|------|
| team.yaml 格式錯 | 檢查 YAML 語法（縮排、冒號後空格） |
| agent 目錄不存在 | `build_team.py` 會自動建立，或手動 `mkdir` |
| .kiro/ 沒產出 | 重新執行 `build_kiro.py team.yaml` |
| Skills 沒載入 | 確認 `.kiro/skills/{name}/SKILL.md` 存在，或執行 `--clone-skills` |
| validate 失敗 | 依錯誤訊息補缺少的檔案，或重新執行對應 script |

---

## 快速診斷指令

```bash
# 確認環境
kiro-cli --version
python --version

# 驗證專案結構
python .kiro/skills/ark-agent-team-builder/scripts/build_team.py --validate .
python .kiro/skills/ark-kiro-init/scripts/build_kiro.py --validate .

# 確認 daemon 運行（port 預設 13030）
curl http://127.0.0.1:13030/api/status

# 查看日誌
# Windows: type logs\team.log
# Mac/Linux: tail -f logs/team.log

# 重啟（watchdog 自動拉起）
echo "" > restart.flag

# 停止
# 關閉 start-team.bat 視窗（Ctrl+C）
```

---

## 重啟方式

| 情境 | 方式 |
|------|------|
| 正常重啟（保留 session） | `echo "" > restart.flag` |
| 強制重啟（清除 session） | 關閉視窗 → 重新雙擊 `start-team.bat` |
| MCP 設定變更後 | 強制重啟（新 session 才載入新工具） |

---

*作者：paddyyang ｜ 更新：2026-05-27*
