from core.embedding import embeddingmanager
from langchain_community.vectorstores import FAISS
from typing import List,Optional
from config.settings import settings
from langchain_core.documents import Document
import os

class vectorstoremanager:
    
    def __init__(self,embedding_manager:embeddingmanager=None):

        self.embedding_manager=embedding_manager or embeddingmanager()
        self._vector_store:Optional[FAISS]=None
        # self.index_path=settings.FAST_INDEX_PATH 
        self.index_path="data/faiss_index"

    @property
    def vector_store(self)->Optional[FAISS]:
        # Get the vector store instance
        return self._vector_store

    def is_initialized(self)->bool:
        return self._vector_store is not None
    
    def create_from_documents(self,documents:List[Document])->FAISS:
        """
        create a new vector store from documents
        Args:
        documents: list of document object to index
        returns:
        FAISS vector store instance
        """
        self._vector_store=FAISS.from_documents(
            documents=documents,
            embedding=self.embedding_manager.embedding
        )
        
    def add_documents(self,documents:List[Document])->None:
        """
        stroring vector store to disk
        Args:
        documents: list of document object to add to the index
        """
        if not self.is_initialized():
            self.create_from_documents(documents)
        else:
            self._vector_store.add_documents(documents)
        
    def serch(self,query:str,k:int=None)->List[Document]:
        if not self.is_initialized():
            raise ValueError("Vector store is not initialized")
        k=k or settings.TOP_K_RESULTS
        results=self._vector_store.similarity_search(
            query=query,
            k=k
        )
        return results
    def save(self,path:str=None)->None:
        """
        save vectore store to disk
        Args:
        path: path to save the vector store
        """
        if not self.is_initialized():
            raise ValueError("Vector store is not initialized")
        path = path or self.index_path
        os.makedirs(os.path.dirname(path),exist_ok=True)
        self._vector_store.save_local(path)

    def load(self,path:str=None)->FAISS:
        """
        load vector store from disk
        Args:
        path: path to load the vector store
        returns: FAISS vector store instance
        """
        load_path = path or self.index_path
        self._vector_store=FAISS.load_local(
            load_path,
            self.embedding_manager.embedding,
            allow_dangerous_deserialization=True
        )
        return self._vector_store

    def get_retriever(self,k:int=None):
        """
        get a retriver from the vector store
        Args:
        k: number of top results to retrieve
        returns: retriver object compitable with langchain
        """
        if not self.is_initialized():
            raise ValueError("Vector store is not initialized")
        k = k or settings.TOP_K_RESULTS
        return self._vector_store.as_retriever(search_type="similarity",search_kwargs={"k":k})
    def clear(self)->None:
        self._vector_store=None

