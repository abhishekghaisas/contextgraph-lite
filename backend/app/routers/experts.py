from fastapi import APIRouter, HTTPException
from neo4j.exceptions import AuthError, ServiceUnavailable

from ..db import run_query
from ..models import ExpertResult

router = APIRouter(prefix="/experts", tags=["experts"])

DB_UNAVAILABLE = "CognoDB is unreachable right now. Please try again shortly."


@router.get("/{person_id}", response_model=list[ExpertResult])
def experts_for_person(person_id: str):
    """
    People who share project context with you (via authored documents) but
    aren't on your team — the "who should I ask, that I wouldn't have
    thought of" query.
    """
    cypher = """
    MATCH (me:Person {id: $personId})-[:AUTHORED]->(:Document)-[:RELATES_TO]->(proj:Project)
    MATCH (proj)<-[:RELATES_TO]-(:Document)<-[:AUTHORED]-(expert:Person)
    WHERE expert <> me
      AND NOT (me)-[:MEMBER_OF]->(:Team)<-[:MEMBER_OF]-(expert)
    RETURN DISTINCT expert.name AS name, expert.title AS title
    LIMIT 25
    """
    try:
        return run_query(cypher, {"personId": person_id})
    except (ServiceUnavailable, AuthError):
        raise HTTPException(status_code=503, detail=DB_UNAVAILABLE)
