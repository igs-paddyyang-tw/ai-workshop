"""FastAPI — AI Agent 專家平台 API + Web UI。"""
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from src.skills.registry import SkillRegistry
from src.wiki.engine import WikiEngine
from pydantic import BaseModel

TEMPLATES_DIR = Path(__file__).resolve().parents[2] / "templates"

app = FastAPI(title="AI Agent 專家平台 API")
engine = WikiEngine()

# ── Memory API Router ──
from src.memory.api import router as memory_router
app.include_router(memory_router)

# ── A2A Router（團隊模式才掛載）──
import os as _os
if _os.getenv("_TEAM_MODE") == "1":
    from src.coordinator.a2a.server import router as a2a_router
    app.include_router(a2a_router)


# ─── Web UI ──────────────────────────────────────────

@app.get("/", response_class=HTMLResponse)
def chat_page():
    """聊天室首頁。"""
    html = (TEMPLATES_DIR / "index.html").read_text(encoding="utf-8")
    return HTMLResponse(content=html)


@app.get("/admin", response_class=HTMLResponse)
def admin_page():
    """管理介面。"""
    html = (TEMPLATES_DIR / "admin.html").read_text(encoding="utf-8")
    return HTMLResponse(content=html)


@app.get("/wiki", response_class=HTMLResponse)
def wiki_page():
    """Wiki 瀏覽器。"""
    html = (TEMPLATES_DIR / "wiki.html").read_text(encoding="utf-8")
    return HTMLResponse(content=html)


@app.get("/builder", response_class=HTMLResponse)
def builder_page():
    """Agent Builder。"""
    html = (TEMPLATES_DIR / "builder.html").read_text(encoding="utf-8")
    return HTMLResponse(content=html)


@app.get("/graph", response_class=HTMLResponse)
def graph_page():
    """Wiki 知識圖譜。"""
    html = (TEMPLATES_DIR / "graph.html").read_text(encoding="utf-8")
    return HTMLResponse(content=html)


@app.get("/api-docs", response_class=HTMLResponse)
def api_docs_page():
    """API 文件（自訂風格）。"""
    html = (TEMPLATES_DIR / "api-docs.html").read_text(encoding="utf-8")
    return HTMLResponse(content=html)


# ─── Chat Trace API ──────────────────────────────────────

@app.get("/api/chat/traces")
async def get_chat_traces(limit: int = 50):
    """查詢最近 Chat Trace 記錄。"""
    from src.memory.chat_trace import get_recent_traces, cleanup_old_traces
    # 順便清理過期記錄
    cleanup_old_traces()
    traces = get_recent_traces(limit=limit)
    return {"traces": traces, "count": len(traces)}


@app.get("/api/chat/traces/{trace_id}")
async def get_chat_trace_by_id(trace_id: str):
    """取得單筆 Trace 詳情。"""
    from src.memory.chat_trace import get_recent_traces
    # 簡易實作：從 recent 中找
    all_traces = get_recent_traces(limit=500)
    for t in all_traces:
        if t["trace_id"] == trace_id:
            return t
    return {"error": "not found"}


# ─── API ─────────────────────────────────────────────

@app.get("/health")
def health_root():
    """健康檢查（短路徑）。"""
    return {"status": "ok"}


@app.get("/api/v1/health")
async def health():
    return {"status": "ok", "service": "a-agent"}


@app.get("/api/v1/skills")
async def list_skills():
    registry = SkillRegistry()
    registry.auto_discover("src.skills.internal")
    return {"skills": registry.list_skills()}


class QueryRequest(BaseModel):
    q: str


class ChatRequest(BaseModel):
    message: str
    agent_id: str = "default"


@app.post("/api/v1/chat")
async def api_chat(req: ChatRequest):
    """統一對話 API — 走 Ark Agent ReAct Loop（與 TG handle_message 同路徑）。"""
    text = req.message.strip()

    try:
        from src.llm.context_builder import build_default_system_prompt
        from src.llm.agent_loop import agent_loop
        import src.llm.tools  # noqa: F401 — 確保 tools 已註冊

        system_prompt = await build_default_system_prompt(query=text)
        result = await agent_loop(
            user_message=text,
            system_prompt=system_prompt,
            max_iterations=5,
        )

        reply = result.text or "⚠️ 無法回應"

        return {
            "reply": reply,
            "source": "agent_loop",
            "iterations": result.iterations,
            "tools_used": [t["tool"] for t in result.tool_calls_log],
        }
    except Exception as e:
        return {
            "reply": f"⚠️ 錯誤：{e}",
            "source": "error",
            "iterations": 0,
            "tools_used": [],
        }


@app.get("/api/v1/graph")
async def get_graph():
    """回傳完整圖譜資料（節點+連線）。"""
    from pathlib import Path
    import re

    nodes = []
    links = []

    # Agent 節點
    agents_dir = Path("agents")
    agent_ids = []
    if agents_dir.exists():
        for d in sorted(agents_dir.iterdir()):
            if d.is_dir() and d.name.endswith("-agent"):
                agent_id = d.name.replace("-agent", "")
                agent_ids.append(agent_id)
                # 讀 SOUL 第一行
                soul_path = d / ".kiro" / "steering" / "SOUL.md"
                soul_desc = ""
                if soul_path.exists():
                    lines = soul_path.read_text(encoding="utf-8").splitlines()
                    for line in lines:
                        if line.strip() and not line.startswith("---") and not line.startswith("#"):
                            soul_desc = line.strip()[:80]
                            break
                nodes.append({"id": f"agent:{agent_id}", "type": "agent", "label": f"{agent_id}-agent", "meta": soul_desc})

                # Skill 節點
                skills_dir = d / ".kiro" / "skills"
                if skills_dir.exists():
                    for skill_dir in sorted(skills_dir.iterdir()):
                        if skill_dir.is_dir() and (skill_dir / "SKILL.md").exists():
                            skill_name = skill_dir.name
                            # 讀 description
                            skill_content = (skill_dir / "SKILL.md").read_text(encoding="utf-8")
                            desc_match = re.search(r"^description:\s*\|?\s*\n?\s*(.+)", skill_content, re.MULTILINE)
                            skill_desc = desc_match.group(1).strip()[:80] if desc_match else ""
                            nodes.append({"id": f"skill:{skill_name}", "type": "skill", "label": skill_name, "meta": skill_desc})
                            # Agent -> Skill 連線
                            links.append({"source": f"agent:{agent_id}", "target": f"skill:{skill_name}", "relation": "has_skill"})

    # Wiki 節點
    wiki_dir = Path("knowledge/shared/wiki")
    wiki_tags = {}  # filename -> tags
    if wiki_dir.exists():
        for md in sorted(wiki_dir.rglob("*.md")):
            content = md.read_text(encoding="utf-8")
            title_match = re.search(r'^title:\s*["\']?(.+?)["\']?\s*$', content, re.MULTILINE)
            title = title_match.group(1) if title_match else md.stem
            tags_match = re.search(r'^tags:\s*\[(.+)\]', content, re.MULTILINE)
            tags = [t.strip().strip("'\"") for t in tags_match.group(1).split(",")] if tags_match else []
            wiki_tags[md.name] = tags
            nodes.append({"id": f"wiki:{md.name}", "type": "wiki", "label": title, "meta": ", ".join(tags)})

    # Skill -> Wiki 連線（Skill 觸發詞匹配 wiki title）
    for node in nodes:
        if node["type"] == "skill":
            skill_id = node["id"]
            # 簡單匹配：skill label 含 wiki 主題關鍵字
            skill_label = node["label"].lower()
            for wiki_node in [n for n in nodes if n["type"] == "wiki"]:
                wiki_label = wiki_node["label"].lower()
                # competitor/market skill 連 競品分析 wiki
                if any(kw in skill_label for kw in ["market", "competitor", "research"]):
                    if any(kw in wiki_label for kw in ["ocean", "super", "slot", "fish", "捕魚", "老虎"]):
                        links.append({"source": skill_id, "target": wiki_node["id"], "relation": "reads_wiki"})

    # Wiki <-> Wiki 連線（共享 tag）
    wiki_files = list(wiki_tags.keys())
    for i in range(len(wiki_files)):
        for j in range(i + 1, len(wiki_files)):
            shared = set(wiki_tags[wiki_files[i]]) & set(wiki_tags[wiki_files[j]])
            if shared:
                links.append({"source": f"wiki:{wiki_files[i]}", "target": f"wiki:{wiki_files[j]}", "relation": "shared_tag"})

    return {"nodes": nodes, "links": links}


@app.get("/api/v1/wiki/pages")
async def list_wiki_pages():
    """列出所有 wiki 頁面（shared + agents），含 scope 標記。"""
    import re as _re

    def extract_title(content: str) -> str:
        m = _re.search(r'^title:\s*["\']?(.+?)["\']?\s*$', content, _re.MULTILINE)
        return m.group(1) if m else ""

    def scan_dir(dir_path: Path, prefix: str = "") -> list:
        items = []
        if not dir_path.exists():
            return items
        for entry in sorted(dir_path.iterdir()):
            if entry.name.startswith("."):
                continue
            rel_path = entry.name if not prefix else f"{prefix}/{entry.name}"
            if entry.is_dir():
                children = scan_dir(entry, rel_path)
                if children:
                    items.append({"type": "folder", "name": entry.name, "path": rel_path, "children": children})
            elif entry.suffix == ".md":
                content = entry.read_text(encoding="utf-8")
                title = extract_title(content) or entry.stem
                items.append({"type": "file", "filename": rel_path, "title": title})
        return items

    pages = []

    # Shared wiki
    shared_wiki = Path("knowledge/shared/wiki")
    if shared_wiki.exists():
        shared_items = scan_dir(shared_wiki, "shared")
        if shared_items:
            pages.append({"type": "folder", "name": "📚 共用知識", "path": "shared", "children": shared_items})

    # Agent wiki
    agents_dir = Path("agents")
    if agents_dir.exists():
        for agent_dir in sorted(agents_dir.iterdir()):
            if agent_dir.is_dir() and agent_dir.name.endswith("-agent"):
                wiki_dir = agent_dir / "knowledge" / "wiki"
                if wiki_dir.exists():
                    agent_items = scan_dir(wiki_dir, f"agents/{agent_dir.name}")
                    if agent_items:
                        pages.append({"type": "folder", "name": f"🤖 {agent_dir.name}", "path": f"agents/{agent_dir.name}", "children": agent_items})

    return {"pages": pages}


@app.get("/api/v1/wiki/pages/{filepath:path}")
async def get_wiki_page(filepath: str):
    """取得指定 wiki 頁面內容（支援 shared/ 和 agents/ 前綴）。"""
    # 路由：shared/xxx → knowledge/shared/wiki/xxx
    #       agents/{name}-agent/xxx → agents/{name}-agent/knowledge/wiki/xxx
    if filepath.startswith("shared/"):
        rel = filepath[len("shared/"):]
        path = Path("knowledge/shared/wiki") / rel
    elif filepath.startswith("agents/"):
        parts = filepath.split("/", 2)  # agents/{name}/rest
        if len(parts) >= 3:
            path = Path(f"agents/{parts[1]}/knowledge/wiki/{parts[2]}")
        else:
            return {"error": "invalid path"}
    else:
        # Fallback：嘗試 shared
        path = Path("knowledge/shared/wiki") / filepath
    if not path.exists() or not path.is_file():
        return {"error": "not found"}
    return {"filename": filepath, "content": path.read_text(encoding="utf-8")}


@app.post("/api/v1/wiki/query")
async def wiki_query(req: QueryRequest):
    result = await engine.query(req.q)
    return result


@app.post("/api/v1/wiki/ingest")
async def wiki_ingest():
    ingested = engine.ingest()
    return {"ingested": ingested, "count": len(ingested)}


@app.get("/api/v1/wiki/lint")
async def wiki_lint():
    issues = engine.lint()
    return {"issues": issues, "healthy": len(issues) == 0}


@app.post("/api/v1/wiki/rebuild-index")
async def wiki_rebuild_index():
    """手動觸發搜尋索引重建。"""
    from src.wiki.indexer import rebuild_index
    manifest = rebuild_index()
    return {"status": "ok", "manifest": manifest}


@app.get("/api/v1/wiki/index-status")
async def wiki_index_status():
    """查看搜尋索引狀態。"""
    import json
    manifest_path = Path("knowledge/.index/manifest.json")
    if not manifest_path.exists():
        return {"status": "not_built", "manifest": None}
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    return {"status": "ok", "manifest": manifest}
