from typing import List, Optional, Generator
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_groq import ChatGroq
from config.settings import settings
from core.vector_store import VectorStoreManager


"""
RAG Prompt Template
"""
RAG_PROMPT_TEMPLATE = """
You are an AI Research Analyst working for an Academic Research Intelligence Platform.

Your task is to assist researchers by analyzing, summarizing, and synthesizing information
from scientific research papers provided in the context.

STRICT RULES:
1. Use ONLY the information present in the provided context.
2. Do NOT invent papers, authors, years, results, or citations.
3. If the context is insufficient, clearly say: 
   "The provided papers do not contain enough information to answer this question."
4. When possible, reference paper titles, authors, and years explicitly.
5. Prefer concise, academic-style explanations.
6. If multiple papers are provided, compare and synthesize their findings.
7. Avoid conversational fluff. Be precise and analytical.


Context:
{context}

Question: {question}

Answer: """


class RAGChain:
    """
    Manages the Retrieval-Augmented Generation pipeline including document retrieval, context formatting, and LLM generation
    """
    
    def __init__(
        self,
        vector_store_manager: VectorStoreManager,
        model_name: str = None,
        temperature: float = None
    ):
        """
        Initialize the RAG chain with vector store and model configurations

        Args:
               vector_store_manager: VectorStoreManager instance with indexed documents
               model_name: Groq model name (default from settings)
               temperature: LLM temperature (default from settings)
        Returns:
               None
        """
        self.vector_store = vector_store_manager
        self.model_name = model_name or settings.GPT_MODEL_NAME
        self.temperature = temperature if temperature is not None else settings.TEMPRATURE
        
        self._llm = ChatGroq(
            model=self.model_name,
            temperature=self.temperature,
            api_key=settings.GROQ_API_KEY
        )
        
        self._prompt = ChatPromptTemplate.from_template(RAG_PROMPT_TEMPLATE)
        
        self._output_parser = StrOutputParser()
    
    @property
    def llm(self) -> ChatGroq:
        """
        Retrieves the configured ChatGroq Language Model instance

        Args:
               No arguments
        Returns:
               ChatGroq instance
        """
        return self._llm
    
    def _format_context(self, documents: List[Document]) -> str:
        """
        Formats retrieved documents into a single structured string for the prompt

        Args:
               documents: List of retrieved documents
        Returns:
               Formatted context string containing document source and content
        """
        if not documents:
            return "No relevant context found."
        
        context_parts = []
        for i, doc in enumerate(documents, 1):
            source = doc.metadata.get("title", "Unknown")
            context_parts.append(f"[Document {i}] (Source: {source})\n{doc.page_content}")
        
        return "\n\n".join(context_parts)
    
    def retrieve(
        self,
        query: str,
        k: int = None,
        metadata_filter: dict | None = None
    ) -> List[Document]:
        """
        Searches and retrieves relevant documents from the vector store based on the query

        Args:
               query: User query string
               k: Number of documents to retrieve
               metadata_filter: Dictionary for filtering results based on metadata
        Returns:
               List of relevant Document objects
        """

        if not self.vector_store.is_initialized():
            return []

        if metadata_filter:
            retriever = self.vector_store.get_retriever(
                k=k,
                metadata_filter=metadata_filter
            )
            return retriever.invoke(query)

        return self.vector_store.search(query=query, k=k)

    
    def generate(self, query: str, context: str) -> str:
        """
        Generates a text response using the LLM based on the query and provided context

        Args:
               query: User's question
               context: Retrieved and formatted context string
        Returns:
               Generated response string
        """
        chain = self._prompt | self._llm | self._output_parser
        
        response = chain.invoke({
            "context": context,
            "question": query
        })
        
        return response
    
    def generate_stream(self, query: str, context: str) -> Generator[str, None, None]:
        """
        Generates a streaming text response using the LLM based on the query and context

        Args:
               query: User's question
               context: Retrieved and formatted context string
        Returns:
               Generator yielding response chunks as strings
        """
        chain = self._prompt | self._llm | self._output_parser
        
        for chunk in chain.stream({
            "context": context,
            "question": query
        }):
            yield chunk
    
    def query(self, question: str,metadata_filter:dict | None, k: int = None) -> dict:
        """
        Executes the full RAG pipeline including retrieval, formatting, and generation

        Args:
               question: User's question
               metadata_filter: Dictionary for filtering documents
               k: Number of documents to retrieve
        Returns:
               Dictionary containing the answer, unique sources, context, and raw documents
        """
        documents = self.retrieve(question, k=k,metadata_filter=metadata_filter)
        context = self._format_context(documents)
        
        answer = self.generate(question, context)
        
        sources = [doc.metadata.get("title", "Unknown") for doc in documents]
        return {
            "answer": answer,
            "sources": list(set(sources)), 
            "context": context,
            "documents": documents
        }
    
    def query_stream(self, question: str, k: int = None) -> Generator[str, None, None]:
        """
        Executes the full RAG pipeline and returns a streaming response

        Args:
               question: User's question
               k: Number of documents to retrieve
        Returns:
               Generator yielding the response chunks
        """
        documents = self.retrieve(question, k=k)
        
        context = self._format_context(documents)
        
        for chunk in self.generate_stream(question, context):
            yield chunk