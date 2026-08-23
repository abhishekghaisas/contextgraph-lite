from typing import Optional

from fastapi import APIRouter, HTTPException
from neo4j.exceptions import AuthError, ServiceUnavailable

from ..db import run_query
from ..models import ProjectOut

router = APIRouter(prefix="/projects", tags=["projects"])

DB_UNAVAILABLE = "CognoDB is unreachable right now. Please try again shortly."


@router.get("", response_model=list[ProjectOut])
def list_projects(q: Optional[str] = None):
    """Powers the project picker in the UI."""
    cypher = """
    MATCH (p:Project)
    WHERE $q IS NULL OR toLower(p.name) CONTAINS toLower($q)
    RETURN p.id AS id, p.name AS name, p.status AS status
    ORDER BY p.name
    LIMIT 25
    """
    try:
        return run_query(cypher, {"q": q})
    except (ServiceUnavailable, AuthError):
        raise HTTPException(status_code=503, detail=DB_UNAVAILABLE)