from typing import Protocol, Dict, List, Any

class ParserProto(Protocol):
    def parse(self, file_path: str) -> Dict[str, Any]:
        """Parses a file and returns parsed data."""
        ...

class EmbedderProto(Protocol):
    async def get_embedding(self, text: str) -> List[float]:
        """Gets embedding for the given text."""
        ...

class DataStoreProto(Protocol):
    async def save_document(self, document: Dict[str, Any]) -> bool:
        """Saves the document to the database."""
        ...
