from fastapi import APIRouter, HTTPException
from neo4j.exceptions import AuthError, ServiceUnavailable

from ..db import run_query
from ..models import ContextResult

router = APIRouter(prefix="/context", tags=["context"])

DB_UNAVAILABLE = "CognoDB is unreachable right now. Please try again shortly."


@router.get("/task/{task_id}", response_model=list[ContextResult])
def context_for_task(task_id: str, hops: int = 3):
    """
    Everyone connected to a task within N hops, through ANY relationship type
    (assignment, mentions in messages, authored docs, meetings, etc).

    Note: the hop count (*1..N) is a variable-length path bound, which Cypher
    does not allow as a bound parameter — it must be a literal integer in the
    query text. It is safe here because it's clamped server-side to 1-4 and
    never taken from raw user input; the actual lookup key (taskId) IS fully
    parameterized below.
    """
    hops = max(1, min(hops, 4))
    cypher = f"""
    MATCH (t:Task {{id: $taskId}})
    MATCH (t)-[*1..{hops}]-(p:Person)
    RETURN DISTINCT p.name AS person, p.title AS title
    LIMIT 25
    """
    try:
        return run_query(cypher, {"taskId": task_id})
    except (ServiceUnavailable, AuthError):
        raise HTTPException(status_code=503, detail=DB_UNAVAILABLE)
