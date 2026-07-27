---
title: "LLM 整合指南"
type: concept
tags: [llm, prompt, ai, integration]
sources: [agents/ai-dev-agent/knowledge/raw/llm-integration.md]
related: [react-agent-architecture, system-architecture]
created: 2026-07-02
updated: 2026-07-14
status: developing
---
# LLM 整合指南

## 模型選擇策略

- **gemini-2.5-flash**：低延遲、高吞吐，適合即時對話與批次處理
- **opus**：深度推理，適合複雜分析與架構決策

## System Prompt 八段式結構

1. 身份（Identity）
2. 人格（Personality）
3. 能力（Capabilities）
4. 邊界（Boundaries）
5. 流程（Workflow）
6. 格式（Output Format）
7. 成長（Learning）
8. 禁制（Restrictions）

## 評估維度

| 維度 | 指標 |
|------|------|
| 準確度 | 任務完成率、正確率 |
| 延遲 | 首 token 延遲、總回應時間 |
| 成本 | Token 用量 × 單價 |

## MCP 工具整合

LLM 透過 MCP（Model Context Protocol）呼叫外部能力，實現 Agent 工具鏈。
