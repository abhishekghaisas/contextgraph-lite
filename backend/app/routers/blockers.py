from fastapi import APIRouter, HTTPException
from neo4j.exceptions import AuthError, ServiceUnavailable

from ..db import run_query
from ..models import BlockerChain

router = APIRouter(prefix="/blockers", tags=["blockers"])

DB_UNAVAILABLE = "CognoDB is unreachable right now. Please try again shortly."


@router.get("/project/{project_id}", response_model=list[BlockerChain])
def blockers_for_project(project_id: str):
    """
    Root blockers (tasks not themselves blocked by anything) and everything
    downstream of them, up to 4 hops of BLOCKS relationships.
    """
    cypher = """
    MATCH (root:Task)-[:PART_OF]->(:Project {id: $projectId})
    WHERE NOT (:Task)-[:BLOCKS]->(root)
    OPTIONAL MATCH (root)-[:BLOCKS*1..4]->(blocked:Task)
    WITH root, collect(DISTINCT blocked.title) AS blockedTasks
    WHERE size(blockedTasks) > 0
    RETURN root.title AS rootBlocker, blockedTasks
    """
    try:
        return run_query(cypher, {"projectId": project_id})
    except (ServiceUnavailable, AuthError):
        raise HTTPException(status_code=503, detail=DB_UNAVAILABLE)
