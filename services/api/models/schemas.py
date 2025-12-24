from typing import List, Optional
from pydantic import BaseModel, Field

# --- Common/Shared ---

class DocumentMetadata(BaseModel):
    title: str
    authors: List[str]
    year: Optional[int] = None
    abstract: Optional[str] = None
    tags: List[str] = Field(default_factory=list)

# --- Search API ---

class SearchFilters(BaseModel):
    authors: Optional[List[str]] = None
    year_min: Optional[int] = None
    year_max: Optional[int] = None
    tags: Optional[List[str]] = None

class SearchRequest(BaseModel):
    query: str
    top_k: int = 10
    filters: Optional[SearchFilters] = None

class SearchResult(BaseModel):
    id: str
    score: float
    metadata: DocumentMetadata

class SearchResponse(BaseModel):
    results: List[SearchResult]

# --- Document API ---

class DocumentResult(BaseModel):
    id: str
    metadata: DocumentMetadata

class DocumentResponse(BaseModel):
    result: DocumentResult

# --- Library Map API ---

class MapPoint(BaseModel):
    id: str
    x: float
    y: float
    cluster_id: int
    title: str

class Cluster(BaseModel):
    id: int
    label: str
    color: str

class LibraryMapResponse(BaseModel):
    points: List[MapPoint]
    clusters: List[Cluster]

# --- Connections API ---

class PaperSummary(BaseModel):
    id: str
    title: str

class Connection(BaseModel):
    source_cluster: str
    target_cluster: str
    papers: List[PaperSummary]
    score: float

class ConnectionsResponse(BaseModel):
    connections: List[Connection]

# --- Gaps API ---

class ResearchGap(BaseModel):
    id: str
    description: str
    score: float
    surrounding_clusters: List[str]

class GapsResponse(BaseModel):
    gaps: List[ResearchGap]
