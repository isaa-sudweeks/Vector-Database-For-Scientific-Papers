from qdrant_client import QdrantClient
import os

class VectorDB:
    def __init__(self, host: str = "qdrant", port: int = 6333):
        self.client = QdrantClient(host=host, port=port)
    
    def search(self, collection_name: str, query_vector: list[float], limit: int = 10):
        return self.client.search(
            collection_name=collection_name,
            query_vector=query_vector,
            limit=limit
        )
