from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Union
from core.embeddings import Embedder
from contextlib import asynccontextmanager

# --- Models ---
class EmbedRequest(BaseModel):
    text: Union[str, List[str]]

class EmbedResponse(BaseModel):
    vector: Union[List[float], List[List[float]]]

# --- Lifecycle ---
models = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load model on startup
    models["embedder"] = Embedder()
    yield
    models.clear()

app = FastAPI(lifespan=lifespan)

# --- Endpoints ---
@app.get("/")
def read_root():
    return {"status": "ok", "service": "embeddings"}

@app.post("/embed", response_model=EmbedResponse)
async def embed(request: EmbedRequest):
    embedder = models.get("embedder")
    if not embedder:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    if isinstance(request.text, str):
        vector = embedder.get_embedding(request.text)
        return EmbedResponse(vector=vector)
    else:
        vectors = embedder.get_embeddings(request.text)
        return EmbedResponse(vector=vectors)
