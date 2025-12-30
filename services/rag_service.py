# services/rag_service.py

from pathlib import Path
from core.chain import RAGChain
from core.vector_store import VectorStoreManager


class RAGService:
    """
    Service wrapper around RAGChain.
    Responsible for loading the vector store from disk.
    """

    def __init__(self):
        self.vector_store = self._load_vector_store()
        self.rag = RAGChain(self.vector_store)

    def _load_vector_store(self) -> VectorStoreManager:
        faiss_path = Path("data/faiss_index")

        if not faiss_path.exists():
            raise RuntimeError(
                "FAISS index not found. Ask admin to run prepare_pdf.py"
            )

        vector_store = VectorStoreManager()
        vector_store.load()

        if not vector_store.is_initialized():
            raise RuntimeError("Vector store failed to initialize")

        return vector_store

    def ask(self, query: str, metadata_filter=None):
        return self.rag.query(
            question=query,
            metadata_filter=metadata_filter
        )
