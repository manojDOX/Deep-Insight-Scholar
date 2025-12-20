from config.settings import settings
from langchain_huggingface import HuggingFaceEmbeddings
from typing import List, Dict


class embeddingmanager:

    def __init__(self, model_name: str = None):
        self.model_name = model_name or settings.EMBEDDING_MODEL
        self._embedding = HuggingFaceEmbeddings(
            model_name=self.model_name,
            model_kwargs={"device": "cpu"}
        )

    @property
    def embedding(self) -> HuggingFaceEmbeddings:
        return self._embedding

    def embed_text(self, text: str) -> List[float]:
        return self.embedding.embed_query(text)

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        return self.embedding.embed_documents(texts)

    def embed_chunks(self, chunks: List[Dict]) -> List[List[float]]:
        texts = [chunk["text"] for chunk in chunks]
        return self.embedding.embed_documents(texts)

    def get_embedding_dimension(self) -> int:
        sample_embedding = self.embed_text("earth")
        return len(sample_embedding)
