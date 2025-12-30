from core.chain import RAGChain

class RAGService:
    def __init__(self, vector_store):
        self.rag = RAGChain(vector_store)

    def ask(self, query: str,metadata_filter=None):
        print("this is from meta:",metadata_filter)
        return self.rag.query(question=query,metadata_filter=metadata_filter)
