from __future__ import annotations
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from coordinator.db.models import init_db
from coordinator.events.bus import EventBus
from coordinator.events.types import EventType
from gateway.api.agents import router as agents_router
from gateway.api.issues import router as issues_router
from gateway.api.admin import router as admin_router
from gateway.api.costs import router as costs_router
from gateway.api.schedules import router as schedules_router
from gateway.api.ws import router as ws_router
from gateway.api.board import router as board_router
from gateway.api.memory import router as memory_router
from gateway.api.wiki import router as wiki_router
from gateway.api.skills import router as skills_router
from gateway.api.chat import router as chat_router

bus = EventBus()

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    # Use externally injected bus if available (injected by bootstrap.py which wires services)
    if hasattr(app.state, "bus") and app.state.bus:
        _bus = app.state.bus
    else:
        # Standalone mode: start bus without service subscriptions
        _bus = bus
        await _bus.start()
        app.state.bus = _bus
    yield
    if not hasattr(app.state, "_external_bus"):
        await _bus.stop()

app = FastAPI(title="Ark Agent Platform", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
app.include_router(agents_router, prefix="/api/agents", tags=["agents"])
app.include_router(issues_router, prefix="/api/issues", tags=["issues"])
app.include_router(admin_router, prefix="/api/admin", tags=["admin"])
app.include_router(costs_router, prefix="/api/costs", tags=["costs"])
app.include_router(schedules_router, prefix="/api/schedules", tags=["schedules"])
app.include_router(ws_router, prefix="/api", tags=["websocket"])
app.include_router(board_router, prefix="/api", tags=["board"])
app.include_router(memory_router)
app.include_router(wiki_router)
app.include_router(skills_router)
app.include_router(chat_router, prefix="/api/chat", tags=["chat"])

@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.get("/board")
async def serve_board():
    from fastapi.responses import FileResponse
    from pathlib import Path
    board_path = Path(__file__).resolve().parents[2] / "apps" / "web" / "board.html"
    return FileResponse(board_path, media_type="text/html")
