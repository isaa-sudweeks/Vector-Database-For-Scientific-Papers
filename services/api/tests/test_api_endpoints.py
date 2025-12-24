import pytest
import httpx
import asyncio

BASE_URL = "http://localhost:8000"

@pytest.mark.asyncio
async def test_root():
    async with httpx.AsyncClient(base_url=BASE_URL) as client:
        response = await client.get("/")
        assert response.status_code == 200
        assert response.json() == {"Hello": "World"}

@pytest.mark.asyncio
async def test_search_endpoint():
    # Note: This test assumes that the 'papers' collection is populated or exists.
    # The 'ensure_collection' is called on API startup, so it should exist.
    # However, it might be empty if we haven't added data to the 'papers' collection specifically.
    # The previous test added data to 'test_collection'.
    
    # We might need to add data to 'papers' collection via some mechanism if we want meaningful results.
    # But for now, we can at least test that the endpoint doesn't crash and returns a valid response structure.
    
    payload = {
        "query": "machine learning",
        "top_k": 5
    }
    
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=30.0) as client:
        response = await client.post("/search", json=payload)
        
        assert response.status_code == 200
        data = response.json()
        assert "results" in data
        assert isinstance(data["results"], list)
        # We can't guarantee results if the DB is empty, but we verified structure.

if __name__ == "__main__":
    # verification via manual run
    asyncio.run(test_root())
    asyncio.run(test_search_endpoint())
    print("API Endpoint tests passed!")
