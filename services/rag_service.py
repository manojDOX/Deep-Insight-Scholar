from core.chain import RAGChain

class RAGService:
    def __init__(self, vector_store):
        self.rag = RAGChain(vector_store)

    def ask(self, query: str):
        return self.rag.query(query)
