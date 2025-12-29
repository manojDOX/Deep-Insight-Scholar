from config.settings import settings
from langchain_huggingface import HuggingFaceEmbeddings
from typing import List, Dict


class EmbeddingManager:
    """
    Manages text embeddings using a specified HuggingFace model.
    """

    def __init__(self, model_name: str = None):
        self.model_name = model_name or settings.EMBEDDING_MODEL
        self._embedding = HuggingFaceEmbeddings(
            model_name=self.model_name,
            model_kwargs={"device": "cpu"},
            encode_kwargs={"normalize_embeddings": True}
        )

    @property
    def embedding(self) -> HuggingFaceEmbeddings:
        """
        Get the HuggingFaceEmbeddings instance.
        Returns:
            HuggingFaceEmbeddings: The HuggingFaceEmbeddings instance.
        """
        return self._embedding

    def embed_text(self, text: str) -> List[float]:
        """
        Embed a text string using the HuggingFace model.
        Args:
            text (str): The text to be embedded.
        Returns:
            List[float]: The embedded representation of the text.
        """
        return self.embedding.embed_query(text)

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """
        Embed a list of text strings using the HuggingFace model.
        Args:
            texts (List[str]): A list of text strings to be embedded.
        Returns:
            List[List[float]]: A list of embedded representations of the text strings.
        """
        return self.embedding.embed_documents(texts)

    def embed_chunks(self, chunks: List[Dict]) -> List[List[float]]:
        """
        Embed a list of text chunks using the HuggingFace model.
        Args:
            chunks (List[Dict]): A list of dictionaries, each containing 'text' and 'metadata' keys.
        Returns:
            List[List[float]]: A list of embedded representations of the text chunks.
        """
        texts = [chunk["text"] for chunk in chunks]
        return self.embedding.embed_documents(texts)

    def get_embedding_dimension(self) -> int:
        """
        Get the dimension of the embeddings produced by the model.
        Returns:
            int: The dimension of the embeddings.
        """
        sample_embedding = self.embed_text("earth")
        return len(sample_embedding)
