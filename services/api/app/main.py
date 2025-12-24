from fastapi import FastAPI
from pydantic import BaseModel
from models.schemas import SearchRequest, SearchResponse, DocumentResponse, LibraryMapResponse, ConnectionsResponse, GapsResponse

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}

#TODO: Add the actual functionality for these
@app.post("/search")
async def search(SearchRequest: SearchRequest):
        return SearchResponse(results=[])

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

