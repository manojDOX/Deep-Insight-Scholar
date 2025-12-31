from pathlib import Path
from core.chain import RAGChain
from core.vector_store import VectorStoreManager


class RAGService:
    """
    Service wrapper for RAGChain that handles vector store initialization and query execution
    """

    def __init__(self):
        """
        Initializes the RAG service by loading the vector store and setting up the chain

        Args:
               No arguments
        Returns:
               None
        """
        self.vector_store = self._load_vector_store()
        self.rag = RAGChain(self.vector_store)

    def _load_vector_store(self) -> VectorStoreManager:
        """
        Checks for existing FAISS index and loads it into a VectorStoreManager

        Args:
               No arguments
        Returns:
               Initialized VectorStoreManager instance
        """
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
        """
        Delegates the user query to the RAGChain with optional filtering

        Args:
               query: User's question string
               metadata_filter: Optional dictionary for filtering search results
        Returns:
               Dictionary containing the answer, sources, and context
        """
        return self.rag.query(
            question=query,
            metadata_filter=metadata_filter
        )