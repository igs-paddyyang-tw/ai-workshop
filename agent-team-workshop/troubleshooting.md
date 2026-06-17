# 故障排除

> 常見問題與解法（更新：2026-06-17）

---

## 環境問題

| 問題 | 解法 |
|------|------|
| `pip install` 被拒絕（PEP 668） | 必須用 venv：`python3 -m venv .venv && source .venv/bin/activate` |
| `No module named 'fastapi'` | 沒在 venv 中，重新 `source .venv/bin/activate` |
| Python 版本不對 | 需要 3.12+，`python3 --version` 確認 |
| `kiro-cli not found` | 確認在 PATH，執行 `kiro-cli --version` |
| Node.js 版本太低（Web Dashboard） | Next.js 需要 Node 20+（Backend 不需要 Node） |

## Telegram 問題

| 問題 | 解法 |
|------|------|
| `Conflict: terminated by other getUpdates` | 有多個 Bot instance 在跑。`pkill -f start.py` 殺掉全部再啟動一個 |
| Bot 沒回應（純私聊） | 確認 `team.yaml` 的 `allowed_users` 有你的 user ID |
| Bot 回覆「⚠️ 執行超時」 | 預設 300 秒超時，確認 kiro-cli 網路正常 |
| Bot 回覆「⚠️ 執行失敗」 | 看 logs：`tail -20 /tmp/team.log` |
| 指令沒反應但 Bot 在線 | 可能是命名衝突：確認沒有 `src/telegram/` 目錄（應為 `src/tg_ui/`） |
| 找不到 user_id | 先對 Bot 發訊，再 `curl .../getUpdates`，看 `from.id` |
| Group Topics 模式不 work | 確認 Bot 是群組 Admin + `group_id` 和 `topic_id` 正確 |

## 啟動問題

| 問題 | 解法 |
|------|------|
| `Address already in use :33333` | `fuser -k 33333/tcp` 或 `lsof -i :33333` 找到並殺掉 |
| `ModuleNotFoundError: telegram.ext` | `src/telegram/` 目錄搶佔命名空間，改名為 `src/tg_ui/` |
| start.py 閃退無日誌 | 前台跑：`python start.py`（不加 &）看錯誤 |
| Agent 都 ready 但不執行 | kiro-cli 用 spawn 模式，每次 send 才啟動，正常 |
| EventBus started 出現兩次 | 正常（lifespan + manual start） |

## Builder 問題

| 問題 | 解法 |
|------|------|
| `build_team.py --help` 產出目錄 | 正常（沒有 argparse），任何參數都當作目錄名 |
| 產出後 import 失敗 | 確認 `generators/` 目錄在 scripts/ 旁邊 |
| `telegram_adapter.py` 殘留 | 新版已移除，手動刪除即可 |

## 費用問題

| 問題 | 解法 |
|------|------|
| 費用顯示 $0 | 需要 agent 實際執行過才有記錄 |
| 擔心費用爆掉 | `team.yaml` 的 `cost_guard.daily_limit_usd` 設低（如 $5） |
| 費用估算不準 | 目前用 chars/4 估算 tokens，誤差約 10-20% |

## 重啟方式

```bash
# 方法 1：直接重啟
pkill -f start.py && sleep 2 && python start.py

# 方法 2：restart.flag（Watchdog 模式）
echo "" > restart.flag
# start-team.sh 會自動偵測並重啟

# 方法 3：看日誌後重啟
tail -20 /tmp/team.log    # 看錯誤原因
fuser -k 33333/tcp        # 釋放 port
python start.py           # 重新啟動
```
