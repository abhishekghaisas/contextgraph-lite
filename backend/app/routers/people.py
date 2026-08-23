from typing import Optional

from fastapi import APIRouter, HTTPException
from neo4j.exceptions import AuthError, ServiceUnavailable

from ..db import run_query
from ..models import PersonOut

router = APIRouter(prefix="/people", tags=["people"])

DB_UNAVAILABLE = "CognoDB is unreachable right now. Please try again shortly."


@router.get("", response_model=list[PersonOut])
def list_people(q: Optional[str] = None):
    cypher = """
    MATCH (p:Person)
    WHERE $q IS NULL OR toLower(p.name) CONTAINS toLower($q)
    OPTIONAL MATCH (p)-[:MEMBER_OF]->(t:Team)
    RETURN p.id AS id, p.name AS name, p.title AS title, t.name AS team
    ORDER BY p.name
    LIMIT 50
    """
    try:
        return run_query(cypher, {"q": q})
    except (ServiceUnavailable, AuthError):
        raise HTTPException(status_code=503, detail=DB_UNAVAILABLE)


@router.get("/{person_id}", response_model=PersonOut)
def get_person(person_id: str):
    cypher = """
    MATCH (p:Person {id: $id})
    OPTIONAL MATCH (p)-[:MEMBER_OF]->(t:Team)
    RETURN p.id AS id, p.name AS name, p.title AS title, t.name AS team
    """
    try:
        rows = run_query(cypher, {"id": person_id})
    except (ServiceUnavailable, AuthError):
        raise HTTPException(status_code=503, detail=DB_UNAVAILABLE)
    if not rows:
        raise HTTPException(status_code=404, detail="Person not found")
    return rows[0]
