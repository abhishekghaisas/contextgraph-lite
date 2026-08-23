from fastapi import APIRouter, HTTPException, Query
from neo4j.exceptions import AuthError, ServiceUnavailable

from ..db import run_query
from ..models import PathResult

router = APIRouter(prefix="/path", tags=["path"])

DB_UNAVAILABLE = "CognoDB is unreachable right now. Please try again shortly."


@router.get("", response_model=PathResult)
def shortest_path(
    from_id: str = Query(..., alias="from"),
    to_id: str = Query(..., alias="to"),
):
    """
    Shortest chain of context connecting two people, through any relationship
    type. This is the query a relational schema handles badly: it needs a
    recursive CTE with an unknown number of self-joins, re-written per hop
    count, and gets slow fast. Cypher expresses it natively in one line.
    """
    cypher = """
    MATCH p = shortestPath((a:Person {id: $from})-[*..6]-(b:Person {id: $to}))
    RETURN [n IN nodes(p) | coalesce(n.name, n.title, n.id)] AS path,
           [r IN relationships(p) | type(r)] AS hops
    """
    try:
        rows = run_query(cypher, {"from": from_id, "to": to_id})
    except (ServiceUnavailable, AuthError):
        raise HTTPException(status_code=503, detail=DB_UNAVAILABLE)
    if not rows:
        raise HTTPException(
            status_code=404, detail="No connecting path found within 6 hops"
        )
    return rows[0]
