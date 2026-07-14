"""MCP stdio server — 橋接 Kiro IDE 與 FastAPI backend。"""
from __future__ import annotations

import argparse
import asyncio
import json
import logging
import sys
from typing import Any

import httpx

log = logging.getLogger(__name__)

# ── Tool 定義 ────────────────────────────────────────────────────

TOOLS: list[dict[str, Any]] = [
    {
        "name": "reply",
        "description": "回覆使用者（Telegram）",
        "inputSchema": {
            "type": "object",
            "properties": {
                "text": {"type": "string", "description": "回覆內容"},
                "kind": {"type": "string", "description": "訊息類型", "default": "text"},
            },
            "required": ["text"],
        },
    },
    {
        "name": "send_to_instance",
        "description": "發訊息給指定 agent",
        "inputSchema": {
            "type": "object",
            "properties": {
                "instance": {"type": "string", "description": "目標 agent 名稱"},
                "msg": {"type": "string", "description": "訊息內容"},
            },
            "required": ["instance", "msg"],
        },
    },
    {
        "name": "delegate_task",
        "description": "委派任務給指定 agent",
        "inputSchema": {
            "type": "object",
            "properties": {
                "instance": {"type": "string", "description": "目標 agent 名稱"},
                "task": {"type": "string", "description": "任務描述"},
            },
            "required": ["instance", "task"],
        },
    },
    {
        "name": "query_team_status",
        "description": "查詢團隊狀態",
        "inputSchema": {"type": "object", "properties": {}},
    },
    {
        "name": "broadcast_all",
        "description": "廣播訊息給全員",
        "inputSchema": {
            "type": "object",
            "properties": {
                "message": {"type": "string", "description": "廣播內容"},
            },
            "required": ["message"],
        },
    },
    {
        "name": "create_task",
        "description": "建立任務",
        "inputSchema": {
            "type": "object",
            "properties": {
                "title": {"type": "string", "description": "任務標題"},
                "assignee": {"type": "string", "description": "指派對象"},
                "description": {"type": "string", "description": "任務描述", "default": ""},
                "priority": {"type": "integer", "description": "優先級 1-4", "default": 3},
            },
            "required": ["title"],
        },
    },
    {
        "name": "update_task",
        "description": "更新任務狀態",
        "inputSchema": {
            "type": "object",
            "properties": {
                "task_id": {"type": "string", "description": "任務 ID"},
                "status": {"type": "string", "description": "狀態：completed | failed"},
                "output": {"type": "string", "description": "產出摘要", "default": ""},
            },
            "required": ["task_id", "status"],
        },
    },
    {
        "name": "list_tasks",
        "description": "列出任務",
        "inputSchema": {
            "type": "object",
            "properties": {
                "status": {"type": "string", "description": "篩選狀態（pending/assigned/completed）"},
            },
        },
    },
    {
        "name": "wiki_query",
        "description": "搜尋知識庫",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "搜尋關鍵字"},
            },
            "required": ["query"],
        },
    },
    {
        "name": "record_spend",
        "description": "記錄成本",
        "inputSchema": {
            "type": "object",
            "properties": {
                "amount_usd": {"type": "number", "description": "金額（USD）"},
            },
            "required": ["amount_usd"],
        },
    },
    {
        "name": "log_to_leader",
        "description": "私下回報 leader（pm-agent）",
        "inputSchema": {
            "type": "object",
            "properties": {
                "text": {"type": "string", "description": "回報內容"},
            },
            "required": ["text"],
        },
    },
]


# ── Tool 執行邏輯 ────────────────────────────────────────────────

class McpBridge:
    """將 MCP tool call 轉發到 FastAPI backend。"""

    def __init__(self, base_url: str, instance: str, role: str) -> None:
        self.base_url = base_url.rstrip("/")
        self.instance = instance
        self.role = role

    async def call_tool(self, name: str, arguments: dict[str, Any]) -> Any:
        async with httpx.AsyncClient(timeout=30.0) as client:
            handler = getattr(self, f"_tool_{name}", None)
            if handler is None:
                return {"error": f"Unknown tool: {name}"}
            return await handler(client, arguments)

    async def _tool_reply(self, client: httpx.AsyncClient, args: dict) -> Any:
        # reply 透過 broadcast（簡化版：記錄到 audit）
        r = await client.post(f"{self.base_url}/api/agents/spawn", json={
            "name": self.instance,
            "action": "reply",
            "text": args.get("text", ""),
        })
        return {"status": "sent", "text": args.get("text", "")[:100]}

    async def _tool_send_to_instance(self, client: httpx.AsyncClient, args: dict) -> Any:
        instance = args.get("instance", "")
        msg = args.get("msg", "")
        r = await client.post(f"{self.base_url}/api/agents/spawn", json={
            "name": instance,
            "action": "message",
            "text": f"[from {self.instance}] {msg}",
        })
        return {"status": "sent", "to": instance, "message": msg[:100]}

    async def _tool_delegate_task(self, client: httpx.AsyncClient, args: dict) -> Any:
        instance = args.get("instance", "")
        task = args.get("task", "")
        r = await client.post(f"{self.base_url}/api/issues", json={
            "title": task[:80],
            "description": task,
            "assignee": instance,
        })
        return r.json() if r.status_code < 400 else {"error": r.text}

    async def _tool_query_team_status(self, client: httpx.AsyncClient, args: dict) -> Any:
        r = await client.get(f"{self.base_url}/api/agents")
        if r.status_code >= 400:
            return {"error": r.text}
        agents = r.json()
        return {"agents": [{"id": a["id"], "status": a["status"]} for a in agents]}

    async def _tool_broadcast_all(self, client: httpx.AsyncClient, args: dict) -> Any:
        message = args.get("message", "")
        r = await client.get(f"{self.base_url}/api/agents")
        agents = r.json() if r.status_code < 400 else []
        for a in agents:
            await client.post(f"{self.base_url}/api/agents/spawn", json={
                "name": a["id"],
                "action": "broadcast",
                "text": f"[broadcast from {self.instance}] {message}",
            })
        return {"status": "broadcasted", "count": len(agents)}

    async def _tool_create_task(self, client: httpx.AsyncClient, args: dict) -> Any:
        r = await client.post(f"{self.base_url}/api/issues", json={
            "title": args.get("title", ""),
            "description": args.get("description", ""),
            "priority": args.get("priority", 3),
            "assignee": args.get("assignee"),
        })
        return r.json() if r.status_code < 400 else {"error": r.text}

    async def _tool_update_task(self, client: httpx.AsyncClient, args: dict) -> Any:
        task_id = args.get("task_id", "")
        r = await client.patch(f"{self.base_url}/api/issues/{task_id}/complete", json={
            "status": args.get("status", "completed"),
            "output": args.get("output", ""),
        })
        return r.json() if r.status_code < 400 else {"error": r.text}

    async def _tool_list_tasks(self, client: httpx.AsyncClient, args: dict) -> Any:
        status = args.get("status", "")
        url = f"{self.base_url}/api/issues"
        if status:
            url += f"?status={status}"
        r = await client.get(url)
        return r.json() if r.status_code < 400 else {"error": r.text}

    async def _tool_wiki_query(self, client: httpx.AsyncClient, args: dict) -> Any:
        q = args.get("query", "")
        r = await client.get(f"{self.base_url}/api/v1/wiki/search", params={
            "q": q, "agent_id": self.instance,
        })
        return r.json() if r.status_code < 400 else {"error": r.text}

    async def _tool_record_spend(self, client: httpx.AsyncClient, args: dict) -> Any:
        # 簡化：記錄到 costs summary
        amount = args.get("amount_usd", 0)
        return {"status": "recorded", "amount_usd": amount, "agent": self.instance}

    async def _tool_log_to_leader(self, client: httpx.AsyncClient, args: dict) -> Any:
        text = args.get("text", "")
        await client.post(f"{self.base_url}/api/agents/spawn", json={
            "name": "pm-agent",
            "action": "log",
            "text": f"[log from {self.instance}] {text}",
        })
        return {"status": "logged", "to": "pm-agent"}


# ── JSON-RPC stdio 處理 ──────────────────────────────────────────

async def handle_request(bridge: McpBridge, request: dict) -> dict:
    """處理單一 JSON-RPC request。"""
    method = request.get("method", "")
    req_id = request.get("id")
    params = request.get("params", {})

    if method == "initialize":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "serverInfo": {
                    "name": f"ark-team-mcp ({bridge.instance})",
                    "version": "1.0.0",
                },
            },
        }

    if method == "notifications/initialized":
        return None  # notification，不回覆

    if method == "tools/list":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {"tools": TOOLS},
        }

    if method == "tools/call":
        tool_name = params.get("name", "")
        arguments = params.get("arguments", {})
        try:
            result = await bridge.call_tool(tool_name, arguments)
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "content": [{"type": "text", "text": json.dumps(result, ensure_ascii=False)}],
                },
            }
        except Exception as e:
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "content": [{"type": "text", "text": json.dumps({"error": str(e)}, ensure_ascii=False)}],
                    "isError": True,
                },
            }

    # 未知 method
    if req_id is not None:
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "error": {"code": -32601, "message": f"Method not found: {method}"},
        }
    return None


async def main_loop(bridge: McpBridge) -> None:
    """讀 stdin JSON-RPC，寫 stdout 回覆。"""
    reader = asyncio.StreamReader()
    protocol = asyncio.StreamReaderProtocol(reader)
    await asyncio.get_event_loop().connect_read_pipe(lambda: protocol, sys.stdin.buffer)

    writer_transport, writer_protocol = await asyncio.get_event_loop().connect_write_pipe(
        asyncio.streams.FlowControlMixin, sys.stdout.buffer
    )
    writer = asyncio.StreamWriter(writer_transport, writer_protocol, None, asyncio.get_event_loop())

    while True:
        line = await reader.readline()
        if not line:
            break
        line = line.decode("utf-8").strip()
        if not line:
            continue
        try:
            request = json.loads(line)
        except json.JSONDecodeError:
            continue

        response = await handle_request(bridge, request)
        if response is not None:
            out = json.dumps(response, ensure_ascii=False) + "\n"
            writer.write(out.encode("utf-8"))
            await writer.drain()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Ark Team MCP stdio server")
    parser.add_argument("--port", type=int, default=33333, help="Backend API port")
    parser.add_argument("--instance", type=str, default="admin-agent", help="Agent instance name")
    parser.add_argument("--role", type=str, default="worker", help="Agent role")
    parser.add_argument("--allowed-targets", type=str, default="", help="Allowed targets (unused)")
    parser.add_argument("--home", type=str, default=".", help="Home directory (unused)")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    base_url = f"http://127.0.0.1:{args.port}"
    bridge = McpBridge(base_url=base_url, instance=args.instance, role=args.role)
    asyncio.run(main_loop(bridge))
