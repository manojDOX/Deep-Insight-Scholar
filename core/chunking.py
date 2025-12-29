from langchain_text_splitters import RecursiveCharacterTextSplitter
from config.settings import Settings
from typing import List,Dict
from langchain_core.documents import Document

class Chunking:

    def __init__(
            self,
            document: List[Document],
            chunk_size: int = None,
            chunk_overlap: int = None            
    ):
        self.chunk_size = chunk_size or Settings.CHUNK_SIZE
        self.chunk_overlap = chunk_overlap or Settings.CHUNK_OVERLAP
        self.document = document

    def intiate_chunk(self)-> List[Document]:
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            separators=["\n\n", "\n", "  ", " ",""]
        )
        chunks = text_splitter.split_documents(self.document)
        return chunks