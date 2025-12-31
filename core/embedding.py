from config.settings import settings
from langchain_huggingface import HuggingFaceEmbeddings
from typing import List, Dict


class EmbeddingManager:
    """
    Manages text embeddings using a specified HuggingFace model
    """

    def __init__(self, model_name: str = None):
        """
        Initializes the EmbeddingManager with a specific model or default from settings

        Args:
              model_name: Name of the HuggingFace model to use (optional)
        Returns:
              None
        """
        self.model_name = model_name or settings.EMBEDDING_MODEL
        self._embedding = HuggingFaceEmbeddings(
            model_name=self.model_name,
            model_kwargs={"device": "cpu"},
            encode_kwargs={"normalize_embeddings": True}
        )

    @property
    def embedding(self) -> HuggingFaceEmbeddings:
        """
        Retrieves the initialized HuggingFaceEmbeddings instance

        Args:
              No arguments
        Returns:
              HuggingFaceEmbeddings instance
        """
        return self._embedding

    def embed_text(self, text: str) -> List[float]:
        """
        Generates an embedding vector for a single text string

        Args:
              text: The input string to be embedded
        Returns:
              List of floats representing the text embedding
        """
        return self.embedding.embed_query(text)

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """
        Generates embedding vectors for a list of text strings

        Args:
              texts: List of input strings to be embedded
        Returns:
              List of lists containing float embeddings for each text
        """
        return self.embedding.embed_documents(texts)

    def embed_chunks(self, chunks: List[Dict]) -> List[List[float]]:
        """
        Extracts text from chunks and generates embeddings for them

        Args:
              chunks: List of dictionaries containing 'text' keys
        Returns:
              List of lists containing float embeddings for the chunk texts
        """
        texts = [chunk["text"] for chunk in chunks]
        return self.embedding.embed_documents(texts)

    def get_embedding_dimension(self) -> int:
        """
        Calculates the dimension size of the embeddings produced by the current model

        Args:
              No arguments
        Returns:
              Integer representing the length of the embedding vector
        """
        sample_embedding = self.embed_text("earth")
        return len(sample_embedding)