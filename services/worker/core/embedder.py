import httpx
from typing import List

class RemoteEmbedder:
    def __init__(self, base_url: str):
        self.base_url = base_url

    async def get_embedding(self, text: str) -> List[float]:
        """
        Calls the embeddings service to get vectors.
        """
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/embed",
                json={"text": text}
            )
            response.raise_for_status()
            data = response.json()
            return data["vector"]
