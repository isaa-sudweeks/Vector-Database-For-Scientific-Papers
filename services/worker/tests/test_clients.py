import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from core.embedder import RemoteEmbedder
from core.store import QdrantStore

@pytest.mark.asyncio
async def test_remote_embedder():
    # Patch where it is used or the class itself globally if imported
    with patch('core.embedder.httpx.AsyncClient') as mock_client:
        # Setup the context manager flow
        mock_instance = AsyncMock()
        mock_client.return_value.__aenter__.return_value = mock_instance
        
        # Setup the response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"vector": [0.1, 0.2, 0.3]}
        
        # When post is awaited, it returns mock_response
        mock_instance.post.return_value = mock_response
        
        embedder = RemoteEmbedder("http://localhost:8001")
        vector = await embedder.get_embedding("hello")
        
        assert vector == [0.1, 0.2, 0.3]
        mock_instance.post.assert_called_once()


@pytest.mark.asyncio
async def test_qdrant_store():
    # Patch the class in core.store
    with patch('core.store.AsyncQdrantClient') as mock_qdrant_cls:
        mock_instance = AsyncMock()
        mock_qdrant_cls.return_value = mock_instance
        
        mock_instance.upsert.return_value = True
        
        store = QdrantStore("localhost", 6333)
        
        doc = {
            "text": "content",
            "vector": [0.1, 0.2],
            "metadata": {"title": "Test"},
            "filename": "test.pdf"
        }
        
        await store.save_document(doc)
        
        mock_instance.upsert.assert_awaited_once()
