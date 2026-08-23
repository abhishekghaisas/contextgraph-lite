from typing import Optional

from pydantic import BaseModel


class PersonOut(BaseModel):
    id: str
    name: str
    title: Optional[str] = None
    team: Optional[str] = None


class ContextResult(BaseModel):
    person: str
    title: Optional[str] = None


class PathResult(BaseModel):
    path: list[str]
    hops: list[str]


class BlockerChain(BaseModel):
    rootBlocker: str
    blockedTasks: list[str]


class ExpertResult(BaseModel):
    name: str
    title: Optional[str] = None


class GraphNode(BaseModel):
    id: str
    label: str
    type: str


class GraphEdge(BaseModel):
    source: str
    target: str
    type: str


class GraphResponse(BaseModel):
    nodes: list[GraphNode]
    edges: list[GraphEdge]


class HealthResponse(BaseModel):
    status: str
    error: Optional[str] = None
