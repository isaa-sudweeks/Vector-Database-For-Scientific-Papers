from fastapi import FastAPI, Depends
from contextlib import asynccontextmanager
from models.schemas import SearchRequest, SearchResponse, DocumentResponse, LibraryMapResponse, ConnectionsResponse, GapsResponse, DocumentMetadata, SearchResult
from core.embedding_client import EmbeddingClient
from core.vector_db import VectorDB

# We store the models and clients in a dictionary 
resources = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize Embedding Client
    # Note: We don't load the model here, we just instantiate the client.
    # The actual model is in the 'embeddings' service.
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

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.post("/search")
async def search(request: SearchRequest, embedder: EmbeddingClient = Depends(get_embedder)):
    # 1. Generate embedding for the query
    # Since this is an async client now, we await it
    query_vector = await embedder.get_embedding(request.query)
    
    # 2. (Next Step) Query Qdrant with this vector
    # We await the search since it's async now
    results = await resources["vector_db"].search(
        collection_name="papers", 
        query_vector=query_vector, 
        limit=request.top_k
    )
    
    # 3. Formulate SearchResponse
    search_results = []
    for res in results:
        # Assuming payload structure matches DocumentMetadata
        payload = res.payload or {}
        metadata = DocumentMetadata(
            title=payload.get("title", "Unknown"),
            authors=payload.get("authors", []),
            year=payload.get("year"),
            abstract=payload.get("abstract"),
            tags=payload.get("tags", [])
        )
        search_results.append(SearchResult(id=str(res.id), score=res.score, metadata=metadata))
    
    return SearchResponse(results=search_results)

@app.get("/documents/{document_id}")
async def get_document(document_id: str):
    return DocumentResponse(result=[])

@app.get("/library/map")
async def get_library_map():
    return LibraryMapResponse(points=[], clusters=[])

@app.get("/connections")
async def get_connections():
    return ConnectionsResponse(connections=[])

@app.get("/gaps")
async def get_gaps():
    return GapsResponse(gaps=[])

