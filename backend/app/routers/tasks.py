from typing import Optional

from fastapi import APIRouter, HTTPException
from neo4j.exceptions import AuthError, ServiceUnavailable

from ..db import run_query
from ..models import TaskOut

router = APIRouter(prefix="/tasks", tags=["tasks"])

DB_UNAVAILABLE = "CognoDB is unreachable right now. Please try again shortly."


@router.get("", response_model=list[TaskOut])
def list_tasks(q: Optional[str] = None):
    """Powers the task picker in the UI — no one should have to know a raw node id."""
    cypher = """
    MATCH (t:Task)-[:PART_OF]->(proj:Project)
    WHERE $q IS NULL OR toLower(t.title) CONTAINS toLower($q)
    RETURN t.id AS id, t.title AS title, proj.name AS project
    ORDER BY t.title
    LIMIT 25
    """
    try:
        return run_query(cypher, {"q": q})
    except (ServiceUnavailable, AuthError):
        raise HTTPException(status_code=503, detail=DB_UNAVAILABLE)