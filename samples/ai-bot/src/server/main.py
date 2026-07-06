"""FastAPI — 課程 A 簡易 API + Web UI。"""
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from src.skills.registry import SkillRegistry
from src.wiki.engine import WikiEngine
from pydantic import BaseModel

TEMPLATES_DIR = Path(__file__).resolve().parents[2] / "templates"

app = FastAPI(title="AI Bot — 個體 Agent API")
engine = WikiEngine()


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


@app.get("/api-docs", response_class=HTMLResponse)
def api_docs_page():
    """API 文件（自訂風格）。"""
    html = (TEMPLATES_DIR / "api-docs.html").read_text(encoding="utf-8")
    return HTMLResponse(content=html)


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
    agent_id: str = "admin"


@app.post("/api/v1/chat")
async def api_chat(req: ChatRequest):
    """統一對話 API — 走跟 TG handle_message 一樣的路由。"""
    import os
    import re
    from src.agent.cli import AVAILABLE_AGENTS, is_cli_available, agent_cli_chat

    text = req.message.strip()
    agent_id = req.agent_id if req.agent_id in AVAILABLE_AGENTS else "admin"
    reply: str | None = None
    source: str = ""

    # L3: Planner keyword 路由
    from src.agent.planner import route, IntentType
    plan = route(text)

    if plan.intent == IntentType.SKILL and plan.skill_id:
        # 觸發 Skill
        if plan.skill_id == "news":
            try:
                from src.skills.internal.news import NewsSkill
                skill = NewsSkill()
                result = await skill.execute({"max_items": 5})
                if result.success:
                    lines = [f"📰 *{result.data['source']}* — {result.data['count']} 則"]
                    for i, art in enumerate(result.data["articles"], 1):
                        lines.append(f"{i}. [{art['title']}]({art['url']})")
                    reply = "\n".join(lines)
                    source = "skill:news"
            except Exception:
                pass

    # L4a: Agent CLI
    if not reply and is_cli_available():
        try:
            reply = await agent_cli_chat(text, agent_id=agent_id)
            if reply:
                source = "cli"
        except Exception:
            reply = None

    # L4b: Wiki RAG
    if not reply:
        wiki_engine = WikiEngine(agent_id=agent_id)
        wiki_result = await wiki_engine.query(text, use_rag=True)
        if wiki_result.get("answer"):
            reply = wiki_result["answer"]
            source = "wiki"

    # L4c: Memory Search
    memory_context = None
    if not reply:
        try:
            from pathlib import Path as P
            memory_dir = P(f"agents/{agent_id}-agent/knowledge/raw")
            if memory_dir.exists():
                keywords = text.lower().split()
                for md in sorted(memory_dir.glob("*.md"), reverse=True)[:10]:
                    content = md.read_text(encoding="utf-8")
                    if any(kw in content.lower() for kw in keywords):
                        memory_context = content[:500]
                        break
        except Exception:
            pass

    # L4d: Gemini API
    if not reply:
        gemini_key = os.getenv("GEMINI_API_KEY", "")
        if gemini_key:
            try:
                from src.llm.gemini_chat import gemini_chat
                # 載入 SOUL
                soul_path = Path(f"agents/{agent_id}-agent/.kiro/steering/SOUL.md")
                soul = soul_path.read_text(encoding="utf-8") if soul_path.exists() else ""
                system = soul
                if memory_context:
                    system += f"\n\n## 相關記憶\n{memory_context}"
                reply = await gemini_chat(text, system=system)
                if reply:
                    source = "gemini"
            except Exception as e:
                reply = f"⚠️ 錯誤: {e}"
                source = "error"

    # 清理 output
    if reply:
        # 清 ANSI
        reply = re.sub(r"\x1b\[[0-9;]*[a-zA-Z]", "", reply)
        reply = re.sub(r"\[(?:\d+;)*\d*m", "", reply)
        reply = re.sub(r"^>\s?", "", reply, flags=re.MULTILINE)
        reply = re.sub(r"\n{3,}", "\n\n", reply).strip()

    if not reply:
        reply = "目前無法回應，請確認 GEMINI_API_KEY 已設定。"
        source = "fallback"

    agent_info = AVAILABLE_AGENTS[agent_id]
    return {
        "reply": reply,
        "agent_id": agent_id,
        "agent_name": agent_info["name"],
        "agent_emoji": agent_info["emoji"],
        "source": source,
        "sources": wiki_result.get("sources", []) if source == "wiki" else [],
    }


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
