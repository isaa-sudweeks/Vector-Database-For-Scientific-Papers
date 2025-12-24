import httpx
from typing import List, Union

class EmbeddingClient:
    def __init__(self, base_url: str = "http://embeddings:8001"):
        self.base_url = base_url

    async def get_embedding(self, text: str) -> List[float]:
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{self.base_url}/embed", json={"text": text})
            response.raise_for_status()
            return response.json()["vector"]

    async def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{self.base_url}/embed", json={"text": texts})
            response.raise_for_status()
            return response.json()["vector"]
