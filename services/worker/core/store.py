from qdrant_client import AsyncQdrantClient
from qdrant_client.http import models
import uuid
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class QdrantStore:
    def __init__(self, host: str, port: int, collection_name: str = "papers"):
        self.client = AsyncQdrantClient(host=host, port=port)
        self.collection_name = collection_name

    async def save_document(self, document: Dict[str, Any]) -> bool:
        """
        Saves the document to Qdrant.
        """
        try:
            # Ensure collection exists (this should ideally be checking or created at startup)
            # For simplicity, we assume it's created or we try to create?
            # Better to assume creation is handled or just try upsert.
            
            # Generate a UUID if not present
            doc_id = str(uuid.uuid4())
            
            vector = document.pop("vector")
            
            # Upsert
            await self.client.upsert(
                collection_name=self.collection_name,
                points=[
                    models.PointStruct(
                        id=doc_id,
                        vector=vector,
                        payload=document
                    )
                ]
            )
            return True
        except Exception as e:
            logger.error(f"Failed to save to Qdrant: {e}")
            raise e
