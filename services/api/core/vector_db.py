from qdrant_client import AsyncQdrantClient, models
import os

class VectorDB:
    def __init__(self, host: str = "qdrant", port: int = 6333):
        self.client = AsyncQdrantClient(host=host, port=port)
    
    async def ensure_collection(self, collection_name: str, vector_size: int = 384):
        if not await self.client.collection_exists(collection_name=collection_name):
            await self.client.create_collection(
                collection_name=collection_name,
                vectors_config=models.VectorParams(size=vector_size, distance=models.Distance.COSINE)
            )

    async def search(self, collection_name: str, query_vector: list[float], limit: int = 10):
        result = await self.client.query_points(
            collection_name=collection_name,
            query=query_vector,
            limit=limit,
            with_payload=True
        )
        return result.points
    async def get_point(self, collection_name: str, point_id: str):
        result = await self.client.retrieve(
            collection_name=collection_name,
            ids=[point_id],
            with_payload=True
        )
        return result[0] if result else None
