from sentence_transformers import SentenceTransformer

class EmbeddingService:
    def __init__(self):
        self.model_name = "sentence-transformers/all-MiniLM-L6-v2"
        self.model = SentenceTransformer(self.model_name)


    def generate_embedding(self, text: str) -> list[float]:

        if not text.strip():
            raise ValueError("Text Cannot be Empty")

        embedding = self.model.encode(text, normalize_embeddings=True)

        return embedding.tolist()

    def generate_embeddings(self, texts: list[str]) -> list[list[float]]:

        if not texts:
            return []

        if any(not text.strip() for text in texts):
            raise ValueError("Texts Cannot Contain Empty Values")

        embeddings = self.model.encode(texts, batch_size=32, normalize_embeddings=True, show_progress_bar=False)

        return embeddings.tolist()

        

