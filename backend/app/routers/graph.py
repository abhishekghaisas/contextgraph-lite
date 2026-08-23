from fastapi import APIRouter, HTTPException
from neo4j.exceptions import AuthError, ServiceUnavailable

from ..db import run_query
from ..models import GraphEdge, GraphNode, GraphResponse

router = APIRouter(prefix="/graph", tags=["graph"])

DB_UNAVAILABLE = "CognoDB is unreachable right now. Please try again shortly."


@router.get("/project/{project_id}", response_model=GraphResponse)
def project_graph(project_id: str):
    """Nodes/edges for a project's tasks and people, shaped for a force-graph view."""
    cypher = """
    MATCH (proj:Project {id: $projectId})
    OPTIONAL MATCH (proj)<-[:PART_OF]-(t:Task)
    OPTIONAL MATCH (proj)<-[:WORKS_ON]-(member:Person)
    RETURN proj {.id, .name} AS proj,
           collect(DISTINCT t {.id, .title}) AS tasks,
           collect(DISTINCT member {.id, .name}) AS members
    """
    try:
        rows = run_query(cypher, {"projectId": project_id})
    except (ServiceUnavailable, AuthError):
        raise HTTPException(status_code=503, detail=DB_UNAVAILABLE)
    if not rows:
        raise HTTPException(status_code=404, detail="Project not found")

    row = rows[0]
    proj = row["proj"]
    nodes: dict[str, GraphNode] = {
        proj["id"]: GraphNode(id=proj["id"], label=proj["name"], type="Project")
    }
    edges: list[GraphEdge] = []

    for t in row["tasks"]:
        if not t:
            continue
        nodes[t["id"]] = GraphNode(id=t["id"], label=t["title"], type="Task")
        edges.append(GraphEdge(source=t["id"], target=proj["id"], type="PART_OF"))

    for m in row["members"]:
        if not m:
            continue
        nodes[m["id"]] = GraphNode(id=m["id"], label=m["name"], type="Person")
        edges.append(GraphEdge(source=m["id"], target=proj["id"], type="WORKS_ON"))

    return GraphResponse(nodes=list(nodes.values()), edges=edges)
