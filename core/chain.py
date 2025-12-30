"""
RAG Chain Module
================
DAY 3: This module orchestrates the RAG pipeline.

SOLID Principle: Single Responsibility Principle (SRP)
- This class has ONE job: orchestrate retrieval and generation

Topics to teach:
- LLM integration with Groq (FREE!)
- Prompt templates
- Chain composition
- Context injection
- Response generation
"""

from typing import List, Optional, Generator
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_groq import ChatGroq

from config.settings import settings
from core.vector_store import VectorStoreManager


# RAG Prompt Template
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
    Orchestrates the RAG (Retrieval-Augmented Generation) pipeline.
    
    Uses:
    - Groq for LLM inference (FREE!)
    - FAISS for vector retrieval
    - Custom prompts for response generation
    """
    
    def __init__(
        self,
        vector_store_manager: VectorStoreManager,
        model_name: str = None,
        temperature: float = None
    ):
        """
        Initialize the RAG chain.
        
        Args:
            vector_store_manager: VectorStoreManager instance with indexed documents
            model_name: Groq model name (default from settings)
            temperature: LLM temperature (default from settings)
        """
        self.vector_store = vector_store_manager
        self.model_name = model_name or settings.GPT_MODEL_NAME
        self.temperature = temperature if temperature is not None else settings.TEMPRATURE
        
        # Initialize Groq LLM
        self._llm = ChatGroq(
            model=self.model_name,
            temperature=self.temperature,
            api_key=settings.GROQ_API_KEY
        )
        
        # Initialize prompt template
        self._prompt = ChatPromptTemplate.from_template(RAG_PROMPT_TEMPLATE)
        
        # Output parser
        self._output_parser = StrOutputParser()
    
    @property
    def llm(self) -> ChatGroq:
        """Get the LLM instance."""
        return self._llm
    
    def _format_context(self, documents: List[Document]) -> str:
        """
        Format retrieved documents into a context string.
        
        Args:
            documents: List of retrieved documents
            
        Returns:
            Formatted context string
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
        Generate a response given query and context.
        
        Args:
            query: User's question
            context: Retrieved context string
            
        Returns:
            Generated response
        """
        # Create the chain: prompt -> llm -> parser
        chain = self._prompt | self._llm | self._output_parser
        
        # Invoke the chain
        response = chain.invoke({
            "context": context,
            "question": query
        })
        
        return response
    
    def generate_stream(self, query: str, context: str) -> Generator[str, None, None]:
        """
        Generate a streaming response.
        
        Args:
            query: User's question
            context: Retrieved context string
            
        Yields:
            Response chunks as they're generated
        """
        # Create the chain
        chain = self._prompt | self._llm | self._output_parser
        
        # Stream the response
        for chunk in chain.stream({
            "context": context,
            "question": query
        }):
            yield chunk
    
    def query(self, question: str,metadata_filter:dict | None, k: int = None) -> dict:
        """
        Complete RAG pipeline: retrieve and generate.
        
        Args:
            question: User's question
            k: Number of documents to retrieve
            
        Returns:
            Dictionary with 'answer', 'sources', and 'context'
        """
        # Step 1: Retrieve relevant documents
        documents = self.retrieve(question, k=k,metadata_filter=metadata_filter)
        # Step 2: Format context
        context = self._format_context(documents)
        
        # Step 3: Generate response
        answer = self.generate(question, context)
        
        # Extract sources
        sources = [doc.metadata.get("title", "Unknown") for doc in documents]
        return {
            "answer": answer,
            "sources": list(set(sources)),  # Unique sources
            "context": context,
            "documents": documents
        }
    
    def query_stream(self, question: str, k: int = None) -> Generator[str, None, None]:
        """
        Complete RAG pipeline with streaming response.
        
        Args:
            question: User's question
            k: Number of documents to retrieve
            
        Yields:
            Response chunks as they're generated
        """
        # Step 1: Retrieve relevant documents
        documents = self.retrieve(question, k=k)
        
        # Step 2: Format context
        context = self._format_context(documents)
        
        # Step 3: Stream response
        for chunk in self.generate_stream(question, context):
            yield chunk