from fastapi import FastAPI, Depends, HTTPException
from contextlib import asynccontextmanager
from models.schemas import SearchRequest, SearchResponse, DocumentResponse, LibraryMapResponse, ConnectionsResponse, GapsResponse, DocumentMetadata, SearchResult, DocumentResult
from core.embedding_client import EmbeddingClient
from core.vector_db import VectorDB

# We store the models and clients in a dictionary 
resources = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize Embedding Client
    resources["embedder"] = EmbeddingClient(base_url="http://embeddings:8001")
    
    # Initialize Vector DB client
    print("Connecting to Qdrant...")
    resources["vector_db"] = VectorDB(host="qdrant")
    
    # Ensure collection exists
    print("Ensuring collection 'papers' exists...")
    await resources["vector_db"].ensure_collection(collection_name="papers")
    
    yield
    # Clean up
    resources.clear()

app = FastAPI(lifespan=lifespan)

def get_embedder():
    return resources["embedder"]

def get_vector_db():
    return resources["vector_db"]

def map_payload_to_metadata(payload: dict) -> DocumentMetadata:
    pdf_meta = payload.get("metadata", {})
    
    title = (
        payload.get("title") or 
        pdf_meta.get("Title") or 
        payload.get("filename") or 
        "Unknown"
    )
    
    authors_val = payload.get("authors")
    if not authors_val:
        author = pdf_meta.get("Author")
        authors_val = [author] if author else []
        
    abstract = payload.get("abstract")
    if not abstract and "text" in payload:
        text = payload["text"]
        abstract = text[:300] + "..." if len(text) > 300 else text

    return DocumentMetadata(
        title=title,
        authors=authors_val,
        year=payload.get("year"),
        abstract=abstract,
        tags=payload.get("tags", []),
        raw_metadata=pdf_meta if pdf_meta else None
    )

@app.get("/")
def read_root():
    return {"status": "ok", "message": "Vector Search API is running"}

@app.post("/search", response_model=SearchResponse)
async def search(request: SearchRequest, embedder: EmbeddingClient = Depends(get_embedder), vector_db: VectorDB = Depends(get_vector_db)):
    # 1. Generate embedding for the query
    query_vector = await embedder.get_embedding(request.query)
    
    # 2. Query Qdrant
    results = await vector_db.search(
        collection_name="papers", 
        query_vector=query_vector, 
        limit=request.top_k
    )
    
    # 3. Formulate SearchResponse
    search_results = []
    for res in results:
        metadata = map_payload_to_metadata(res.payload or {})
        search_results.append(SearchResult(id=str(res.id), score=res.score, metadata=metadata))
    
    return SearchResponse(results=search_results)

@app.get("/documents/{document_id}", response_model=DocumentResponse)
async def get_document(document_id: str, vector_db: VectorDB = Depends(get_vector_db)):
    res = await vector_db.get_point(collection_name="papers", point_id=document_id)
    if not res:
        raise HTTPException(status_code=404, detail="Document not found")
    
    metadata = map_payload_to_metadata(res.payload or {})
    return DocumentResponse(result=DocumentResult(id=str(res.id), metadata=metadata))

@app.get("/library/map")
async def get_library_map():
    return LibraryMapResponse(points=[], clusters=[])

@app.get("/connections")
async def get_connections():
    return ConnectionsResponse(connections=[])

@app.get("/gaps")
async def get_gaps():
    return GapsResponse(gaps=[])
