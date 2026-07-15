---
inclusion: always
---
# Memory — 專案狀態

> 持久化上下文，避免每次重問。定期由使用者更新。

## 專案狀態（2026-07-15）

- 架構：TG Bot gateway + Gemini Chat（ReAct + Tool Calling）+ Agent CLI 派工
- LLM：Gemini 3.5 Flash（快速）+ Claude Sonnet 4.6（深度 via agy）
- Tool Calling：Gemini Function Calling，schema 需經 clean_schema() 清理
- Skills：auto_discover 掃描 src/skills/internal/

## 技術決策

- Prompt 注入：SOUL + MEMORY + session history，依 backend 不同走不同路徑
- ReAct Loop：agent_loop()，最多 5 iterations，超限強制 summary
- 壓縮：compress_messages() 防止 context 超限

## 踩坑紀錄

- Gemini FC schema 需清理（移除 anyOf / title / default）
- agy 的 --add-dir 不等於主 workspace，GEMINI.md/AGENTS.md 不會被讀取
- _inject_soul() 解法：subprocess 呼叫時直接 prepend SOUL.md 到 prompt
