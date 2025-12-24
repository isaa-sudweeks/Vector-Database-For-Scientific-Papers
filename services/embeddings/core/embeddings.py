from sentence_transformers import SentenceTransformer
import torch

class Embedder:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"Loading model {model_name} on {self.device}...")
        self.model = SentenceTransformer(model_name, device=self.device)
        print("Model loaded successfully.")
    
    def get_embedding(self, text: str):
        return self.model.encode(text).tolist()

    def get_embeddings(self, texts: list[str]):
        return self.model.encode(texts).tolist()
