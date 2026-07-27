---
title: "LLM 整合指南"
type: concept
tags: [llm, prompt, ai]
sources: [raw/llm-integration.md]
related: [system-architecture, python-fastapi]
created: 2026-07-02
updated: 2026-07-20
status: mature
---
# LLM 整合指南

## 模型選擇

- gemini-2.5-flash：低延遲、日常任務
- opus：深度推理、複雜分析

## System Prompt 設計

八段式結構：身份 / 人格 / 能力 / 邊界 / 流程 / 格式 / 成長 / 禁制

## 評估維度

- 準確度（回答品質）
- 延遲（回應時間）
- 成本（token 費用）

## MCP 工具整合

讓 LLM 能呼叫外部能力，透過 function calling 機制串接。
