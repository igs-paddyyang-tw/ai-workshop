# 故障排除

> 課程 B（`ark_team_agent` 消費端）常見問題。更新：2026-09-14
>
> 🔴 **這份表的一半不是「故障」，是「正常但看起來像壞了」。** 先分清楚再動手。

---

## 「看起來壞了，其實正常」— 先看這一區

| 現象 | 真相 | 怎麼確認 |
|------|------|---------|
| **私訊送了沒回**（最常見） | kiro-cli backend **首次冷啟要 2–4 分鐘**（spawn team MCP + 握手）。訊息在佇列裡，沒有掉 | `cat /proc/<kiro-cli pid>/stat` 看 CPU 時間有沒有在動；log 有 `Queued message` 就是還在等 |
| `/health` 回 404 | team 套件的端點是 **`/api/health`**（bot 套件才是 `/health`） | `curl -s localhost:23050/api/health` |
| `authority-matrix.yml not found` | 決策鎖是**選配**，non-fatal | 啟動繼續就是正常 |
| 看板打不開 | website 在 **`health_port + 5000`**（23050 → 28050） | `/api/health` 回應的 `website.port` 就寫著 |
| Agent 都 ready 但沒在跑 | `persistent: false` 是 **lazy spawn**，有需求才啟動 | `curl -s localhost:23050/api/instances` |
| `instances.total` 比編制少 | 同上，lazy 的還沒被喚醒 | 派一個工給它就會起來 |

---

## 🔴 「設定看起來生效了，其實沒有」

| 現象 | 原因 | 解法 |
|------|------|------|
| 派工不照 `group` 走 | 寫成 **`group_members`**（那是課程 A 的 bot 端寫法） | 改成 `group: leader-agent`；啟動 log 會印「欄位不存在 → 已忽略」 |
| 各 agent 的 skill 每次啟動變回預設 | `kiro_files.skills.policy` 不是 `skip` | 設 `skip`，改完重跑 `scripts/sync_skills.py` |
| 自訂欄位沒作用 | **未知欄位會被靜默丟掉** | 約束寫進 `description` 或該 agent 的 `SOUL.md` |
| 改了 `SOUL.md` 沒反應 | 該 instance 還在跑舊 session | `curl -X POST localhost:23050/api/instances/<name>/restart` |

> 💡 這一類最危險：**它不報錯**。改完設定要去 log 找證據，不要只看「有沒有紅字」。

---

## 環境問題

| 問題 | 解法 |
|------|------|
| `pip install` 被拒絕（PEP 668） | 必須用 venv：`python3 -m venv .venv && source .venv/bin/activate` |
| `ModuleNotFoundError: ark_team_agent` | wheel 沒裝進這個 venv。**驗 import 不看 pip 輸出**：`python -c "import ark_team_agent; print(ark_team_agent.__version__)"` |
| 裝了但版本不對 | 同上，用 import 驗；若 `pyproject.toml` 有 pin 版號，升級要同步改 pin |
| Python 版本不對 | 需要 3.12+（部分專案需 3.13），`python3 --version` |
| `kiro-cli not found` | 確認在 PATH：`kiro-cli --version`；沒有它 instance 起不來 |
| `sync_skills.py` 說來源不存在 | 上游共用庫沒 clone：`git clone .../ark-agent-skills ~/kiro-cli/.kiro/skills` |

## Telegram 問題

| 問題 | 解法 |
|------|------|
| **Bot 有時回有時不回** | 🔴 **同一個 token 有兩個地方在 polling**（另一台電腦、另一個專案）。它會**隨機**吃掉訊息且兩邊都不報錯 —— 每人用自己的 token |
| `Conflict: terminated by other getUpdates` | 同上的顯性版本：`pkill -f start.py` 殺掉全部再啟動一個 |
| `telegram.error.InvalidToken` | `.env` 還是 `your_token`，或貼錯 |
| Bot 沒回應（私聊） | `team.yaml` 的 `access.allowed_users` 沒填你的 user ID |
| 找不到 user_id | 先對 Bot 發訊，再 `curl -s "https://api.telegram.org/bot<TOKEN>/getUpdates"`，看 `from.id` |
| Group Topics 不 work | Bot 要是群組 Admin + `group_id` 正確 |

## 啟動問題

| 問題 | 解法 |
|------|------|
| `Address already in use` | 改 `team.yaml` 的 `health_port`（記得看板會跟著變 +5000），或關掉佔用的進程 |
| start.py 閃退無日誌 | 前台跑 `python start.py`（不加 `&`）看錯誤 |
| instance `process died during startup` | 多半是 `working_directory` 不存在，或 kiro-cli 不在 PATH |
| 想看套件解析到什麼 | `curl -s localhost:23050/api/status` |

## 費用問題

| 問題 | 解法 |
|------|------|
| 費用顯示 $0 | 要 agent 實際執行過才有記錄 |
| 擔心費用爆掉 | `team.yaml` 的 `cost_guard.daily_limit_usd` 設低（如 $5），`warn_at_percentage` 設 60 |
| 費用估算不準 | 以 chars 估 tokens，誤差約 10-20%；當護欄用，不當帳單用 |

## 重啟

```bash
# 前台重啟
pkill -f start.py && python start.py

# 只重啟單一 instance（不中斷整個團隊）
curl -X POST localhost:23050/api/instances/coder-agent/restart

# 常駐（systemd user service）
systemctl --user restart my-team
journalctl --user -u my-team -n 50 --no-pager
```

---

## 還是卡住？

1. `curl -s localhost:23050/api/health` — daemon 活著嗎
2. `curl -s localhost:23050/api/instances` — 誰在跑
3. 看 log 有沒有「欄位不存在 → 已忽略」— 設定是不是沒生效
4. 看 kiro-cli 進程的 CPU 時間 — 是不是還在冷啟

**先分清「沒生效」「還沒好」「真的壞了」，再開始修。**
