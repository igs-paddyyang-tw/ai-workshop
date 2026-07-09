---
title: 跨機協作 Transport 抽象設計
slug: a2a-transport-design
category: architecture
tags: [a2a, transport, distributed, team, design-decision]
created: 2026-07-09
---

# 跨機協作 Transport 抽象設計

## 問題：AgentProcess 只能本地

原始的 `AgentProcess` 實作是直接 spawn 子進程：

```python
proc = subprocess.Popen(["python", "agent.py"], ...)
proc.stdin.write(task_json)
result = proc.stdout.read()
```

這在單機開發很方便，但無法：
- 把 Agent 部署到不同機器（GPU 機跑 rerank、CPU 機跑搜尋）
- 讓遠端團隊成員的 Agent 參與協作
- 水平擴展特定 Agent 的執行實例

## 解法：Transport 抽象層（local | http）

引入 `Transport` 介面，讓上層程式碼不關心 Agent 在哪裡執行：

```python
class Transport(Protocol):
    async def send(self, agent_id: str, task: Task) -> None: ...
    async def receive(self, agent_id: str) -> Result: ...
    async def health_check(self, agent_id: str) -> bool: ...
```

兩種實作：

| Transport | 適用場景 | 通訊方式 |
|-----------|---------|---------|
| `LocalTransport` | 開發 / 單機 | subprocess + stdin/stdout |
| `HttpTransport` | 生產 / 跨機 | HTTP POST + SSE callback |

## team.yaml 漸進升級

```yaml
# 階段 1：全部本地（預設）
agents:
  researcher:
    transport: local
    script: agents/researcher.py

# 階段 2：混合部署
agents:
  researcher:
    transport: http
    endpoint: http://gpu-server:8080/agent/researcher
  writer:
    transport: local
    script: agents/writer.py
```

**零改動升級**：只需改 `transport` 欄位，Agent 程式碼完全不動。
Orchestrator 透過 Transport 介面派工，不感知底層差異。

## Callback / Heartbeat 機制

跨機執行最怕「任務送出去就沒回音」。設計兩層保護：

### Heartbeat（活性偵測）
```
Orchestrator → GET /health → Agent
每 10s 一次，連續 3 次失敗標記 agent 為 unavailable
```

### Callback（結果回報）
```
Agent 完成 → POST /callback/{task_id} → Orchestrator
包含：result、duration、token_usage
```

### Timeout 降級
```
task_timeout: 60s（預設）
超時 → 標記 failed → Orchestrator 決定重試或跳過
```

## 安全設計

| 威脅 | 對策 |
|------|------|
| 未授權呼叫 | Bearer Token 驗證（team.yaml 中配置） |
| 中間人攻擊 | 強制 HTTPS（生產環境） |
| 任務注入 | task schema 驗證 + agent_id 白名單 |
| 資料外洩 | 敏感欄位不進 callback body，只存本地 |
| DDoS | Rate limit per agent_id（10 req/s） |

```yaml
# team.yaml 安全配置
security:
  require_https: true
  token: ${TEAM_SECRET}
  allowed_agents: [researcher, writer, reviewer]
  rate_limit: 10
```

## 設計原則總結

1. **本地優先**：預設 local，不增加開發複雜度
2. **漸進升級**：改一行 YAML 就能跨機
3. **故障容忍**：heartbeat + timeout + retry
4. **安全內建**：不是事後加，而是 transport 層的責任
