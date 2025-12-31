from langchain_text_splitters import RecursiveCharacterTextSplitter
from config.settings import Settings
from typing import List,Dict
from langchain_core.documents import Document

class Chunking:
    """
    Handles the splitting of documents into smaller text chunks for processing
    """

    def __init__(
            self,
            document: List[Document],
            chunk_size: int = None,
            chunk_overlap: int = None            
    ):
        """
        Initializes the chunking processor with documents and splitting parameters

        Args:
              document: List of Document objects to be split
              chunk_size: Maximum size of each text chunk (optional)
              chunk_overlap: Number of overlapping characters between chunks (optional)
        Returns:
              None
        """
        self.chunk_size = chunk_size or Settings.CHUNK_SIZE
        self.chunk_overlap = chunk_overlap or Settings.CHUNK_OVERLAP
        self.document = document

    def intiate_chunk(self)-> List[Document]:
        """
        Splits the stored documents into smaller chunks using RecursiveCharacterTextSplitter

        Args:
              No arguments
        Returns:
              List of split Document objects containing the chunked text
        """
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            separators=["\n\n", "\n", "  ", " ",""]
        )
        chunks = text_splitter.split_documents(self.document)
        return chunks