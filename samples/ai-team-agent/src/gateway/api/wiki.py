"""Wiki API endpoints。"""
from __future__ import annotations

from fastapi import APIRouter, Query
from pydantic import BaseModel

router = APIRouter(prefix="/api/v1/wiki", tags=["wiki"])


@router.get("/search")
async def wiki_search(
    q: str = Query(..., description="搜尋關鍵字"),
    agent_id: str = Query(None, description="Agent ID（限定 scope）"),
    use_rag: bool = Query(False, description="是否使用 RAG 合成答案"),
):
    """四層知識庫搜尋。"""
    from coordinator.wiki.engine import WikiEngine

    engine = WikiEngine(agent_id=agent_id)
    result = await engine.query(q, use_rag=use_rag)
    return result


@router.get("/pages")
async def wiki_pages(
    scope: str = Query("all", description="shared | private | all"),
    agent_id: str = Query(None),
):
    """列出知識庫所有頁面。"""
    from coordinator.wiki.indexer import load_metadata

    metadata = load_metadata()
    if scope == "shared":
        metadata = [m for m in metadata if m["scope"] == "shared"]
    elif scope == "private" and agent_id:
        agent_name = agent_id if agent_id.endswith("-agent") else f"{agent_id}-agent"
        metadata = [m for m in metadata if m["agent"] == agent_name]

    return {
        "pages": [
            {"path": m["path"], "title": m["title"], "tags": m["tags"], "scope": m["scope"]}
            for m in metadata
        ],
        "count": len(metadata),
    }


class IngestRequest(BaseModel):
    scope: str = "global"
    agent_id: str | None = None
    filename: str | None = None


@router.post("/ingest")
async def wiki_ingest(req: IngestRequest):
    """匯入 raw → wiki。"""
    from coordinator.wiki.engine import WikiEngine

    engine = WikiEngine(agent_id=req.agent_id)
    ingested = engine.ingest(scope=req.scope, filename=req.filename)
    return {"ingested": ingested, "count": len(ingested)}


@router.get("/graph-data")
async def wiki_graph_data():
    """知識圖譜 — 回傳 nodes + edges JSON。"""
    from coordinator.wiki.indexer import load_metadata

    metadata = load_metadata()
    nodes: list[dict] = []
    edges: list[dict] = []
    seen_agents: set[str] = set()

    for m in metadata:
        # Wiki 頁面 node
        node_id = f"wiki:{m['path']}"
        nodes.append({
            "id": node_id,
            "label": m["title"],
            "type": "wiki",
            "scope": m["scope"],
        })

        # Agent node
        agent = m["agent"]
        if agent not in seen_agents and agent != "_project":
            seen_agents.add(agent)
            nodes.append({
                "id": f"agent:{agent}",
                "label": agent,
                "type": "agent",
            })

        # Edge: agent → wiki
        if agent != "_project":
            edges.append({
                "source": f"agent:{agent}",
                "target": node_id,
                "type": "knows",
            })

        # Tag edges（tag → wiki）
        for tag in m.get("tags", []):
            tag_id = f"tag:{tag}"
            if not any(n["id"] == tag_id for n in nodes):
                nodes.append({"id": tag_id, "label": tag, "type": "tag"})
            edges.append({"source": tag_id, "target": node_id, "type": "tagged"})

    return {"nodes": nodes, "edges": edges}
