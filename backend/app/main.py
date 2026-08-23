from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .db import db
from .models import HealthResponse
from .routers import blockers, context, experts, graph, path, people, projects, tasks

app = FastAPI(
    title="ContextGraph Lite API",
    description="A small enterprise context graph, backed by CognoDB.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(people.router)
app.include_router(tasks.router)
app.include_router(projects.router)
app.include_router(context.router)
app.include_router(path.router)
app.include_router(blockers.router)
app.include_router(experts.router)
app.include_router(graph.router)


@app.get("/health", response_model=HealthResponse, tags=["health"])
def health():
    """Used by the frontend to show a banner instead of a blank screen if CognoDB is down."""
    ok, error = db.verify_connectivity()
    return HealthResponse(status="ok" if ok else "unreachable", error=error)


@app.on_event("shutdown")
def shutdown():
    db.close()