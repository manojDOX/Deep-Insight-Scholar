from typing import List, Dict
from langchain_core.documents import Document


class DocumentAdapter:

    @staticmethod
    def chunks_to_documents(chunks: List[Dict]) -> List[Document]:
        return [
            Document(
                page_content=chunk["text"],
                metadata=chunk["metadata"]
            )
            for chunk in chunks
        ]
