# Memory

## 專案狀態（2026-07-14）

- 四層架構完成：gateway / coordinator / runtime / business
- Builder（ark-agent-team-builder）產出 110 項，與本專案 src/ 零差異
- Workshop 教材 4 份（01-04），全部 50 min，已對齊四層架構
- Repo 改名：ark-kiro-skills → ark-agent-skills
- MCP stdio bridge 完成：`src/gateway/mcp_stdio.py`（轉發 tool call → FastAPI port 33333）
- Agent 結構對齊 ai-bot：8 agent 全有 BRAIN + GUARDRAILS + memory + raw + output
- knowledge/shared/ 已建立（raw 5 篇）
- docs/ 結構已建立（specs/designs/plans/one-pagers）

## 技術決策

- LLM：kiro-cli spawn（複雜）+ Gemini Chat（簡單秒回）
- DB：SQLite dev / PostgreSQL prod
- TG 命名空間：src/gateway/telegram/（避免與 python-telegram-bot 衝突）
- A2A：檔案系統 SharedMemory（agent 可直接讀 knowledge/shared/）
- Process：spawn 模式（每次 send 新建 kiro-cli 進程）
- Timeout：300 秒
- MCP：stdio JSON-RPC bridge（需先啟動 bootstrap.py 才能用）

## 踩坑紀錄

- WSL2 用 localhost 連（不是 WSL IP）
- venv 必要（PEP 668）
- 多 Bot instance 衝突 → pkill 只留一個
- build_team.py 無 --help flag（任何參數都當目錄名）
- generators 用 repr() 不用 json.dumps()（避免 surrogate 問題）
- 舊路徑 `src/ark_team_core/team_mcp.py` 重構後不存在 → mcp.json 全部更新為 `src/gateway/mcp_stdio.py`
