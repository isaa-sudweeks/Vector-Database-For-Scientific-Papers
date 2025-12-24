import asyncio
import pytest
import sys
import os
from qdrant_client import models

# Add the parent directory to sys.path to allow importing from core
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.embedding_client import EmbeddingClient
from core.vector_db import VectorDB

@pytest.mark.asyncio
async def test_e2e_embedding_and_search():
    print("Starting Integration Test...")

    # 1. Setup Clients
    # Pointing to localhost ports as exposed by docker-compose
    embedder = EmbeddingClient(base_url="http://localhost:8001")
    vector_db = VectorDB(host="localhost", port=6333)
    
    collection_name = "test_collection"
    
    # Ensure collection exists
    print(f"Ensuring collection '{collection_name}' exists...")
    await vector_db.ensure_collection(collection_name)
    
    # 2. Test Data
    test_docs = [
        "The quick brown fox jumps over the lazy dog.",
        "Machine learning is a subset of artificial intelligence.",
        "Photosynthesis is the process by which green plants create food."
    ]
    
    metadatas = [
        {"title": "Fox Story", "category": "fiction"},
        {"title": "ML Intro", "category": "tech"},
        {"title": "Bio Basics", "category": "science"}
    ]
    
    # 3. Embed Data
    print("Generating embeddings for test documents...")
    try:
        embeddings = await embedder.get_embeddings(test_docs)
    except Exception as e:
        print(f"Failed to get embeddings: {e}")
        return

    if not embeddings or len(embeddings) != len(test_docs):
        print(f"Error: Expected {len(test_docs)} embeddings, got {len(embeddings) if embeddings else 0}")
        return
        
    print(f"Successfully generated {len(embeddings)} embeddings.")

    # 4. Insert into Qdrant
    print("Upserting data into Qdrant...")
    points = [
        models.PointStruct(
            id=idx + 1000, # Use IDs that won't conflict with real data likely
            vector=vector,
            payload=metadata
        )
        for idx, (vector, metadata) in enumerate(zip(embeddings, metadatas))
    ]
    
    try:
        await vector_db.client.upsert(
            collection_name=collection_name,
            points=points
        )
        print("Upsert successful.")
    except Exception as e:
        print(f"Failed to upsert to Qdrant: {e}")
        return
    
    # 5. Search
    search_query = "AI and computers"
    print(f"Searching for: '{search_query}'")
    
    try:
        query_vector = await embedder.get_embedding(search_query)
        results = await vector_db.search(collection_name, query_vector, limit=1)
        
        print("\n--- Search Results ---")
        for res in results:
            print(f"ID: {res.id}, Score: {res.score}")
            print(f"Payload: {res.payload}")
            
        if results and results[0].payload["title"] == "ML Intro":
             print("\nSUCCESS: Correct document returned as top result!")
        else:
             print("\nFAILURE: Did not get expected document 'ML Intro' as top result.")

    except Exception as e:
        print(f"Search failed: {e}")
        return

if __name__ == "__main__":
    asyncio.run(run_test())
