from typing import List, Dict
from langchain_core.documents import Document


class DocumentAdapter:

    @staticmethod
    def chunks_to_documents(chunks: List[Dict]) -> List[Document]:
        """
        Convert a list of text chunks with metadata into a list of Document objects.
        Args:
            chunks (List[Dict]): A list of dictionaries, each containing 'text' and 'metadata' keys.
            Returns:
            List[Document]: A list of Document objects.
        """
        return [
            Document(
                page_content=chunk["text"],
                metadata=chunk["metadata"]
            )
            for chunk in chunks
        ]
