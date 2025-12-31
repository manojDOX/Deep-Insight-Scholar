import os
from typing import List, Optional, Literal
from langchain_tavily import TavilySearch

from config.settings import settings


class TavilySearchTool:
    """
    Web search tool using Tavily API for retrieving current events or external information
    """
    
    def __init__(
        self,
        max_results: int = 3,
        topic: Literal["general", "news", "finance"] = "general"
    ):
        """
        Initialize the Tavily search tool with configuration parameters

        Args:
               max_results: Maximum number of search results to return
               topic: Search topic category - "general", "news", or "finance"
        Returns:
               None
        """
        self.max_results = max_results
        self.topic = topic
        
        # Set Tavily API key in environment (required by langchain-tavily)
        os.environ["TAVILY_API_KEY"] = settings.TAVILY_API_KEY
        
        # Initialize Tavily search
        self._search = TavilySearch(
            max_results=self.max_results,
            topic=self.topic
        )
    
    @property
    def tool(self) -> TavilySearch:
        """
        Get the underlying Tavily search tool instance

        Args:
               No arguments
        Returns:
               TavilySearch instance
        """
        return self._search
    
    def search(self, query: str) -> str:
        """
        Perform a web search and return the results as a formatted string

        Args:
               query: Search query string
        Returns:
               Formatted string containing search results
        """
        results = self._search.invoke(query)
        return self._format_results(results)
    
    def _format_results(self, results: dict) -> str:
        """
        Format raw Tavily results dictionary into a readable string

        Args:
               results: Raw dictionary returned by Tavily API
        Returns:
               Formatted string of search results or "No results found."
        """
        if not results:
            return "No search results found."
        
        formatted_parts = []
        
        # Add answer if available
        if results.get("answer"):
            formatted_parts.append(f"Summary: {results['answer']}")
        
        # Add individual results
        if results.get("results"):
            for i, result in enumerate(results["results"], 1):
                title = result.get("title", "No title")
                content = result.get("content", "No content")
                url = result.get("url", "")
                formatted_parts.append(f"[{i}] {title}\n{content}\nSource: {url}")
        
        return "\n\n".join(formatted_parts) if formatted_parts else "No results found."
    
    def search_with_context(self, query: str) -> dict:
        """
        Perform a web search and return structured results with metadata

        Args:
               query: Search query string
        Returns:
               Dictionary containing query, raw results, formatted text, and source info
        """
        raw_results = self._search.invoke(query)
        
        return {
            "query": query,
            "results": raw_results,
            "formatted": self._format_results(raw_results),
            "source": "tavily_web_search"
        }


class HybridSearchManager:
    """
    Manages hybrid search strategy combining local document search with web search

    Args:
           No arguments for class definition
    Returns:
           HybridSearchManager instance
    """
    
    def __init__(
        self,
        vector_store_manager,
        tavily_tool: TavilySearchTool = None
    ):
        """
        Initialize hybrid search manager with vector store and optional web search tool

        Args:
               vector_store_manager: VectorStoreManager instance for document search
               tavily_tool: TavilySearchTool instance for web search (optional)
        Returns:
               None
        """
        self.vector_store = vector_store_manager
        self.tavily = tavily_tool or TavilySearchTool()
    
    def search(
        self,
        query: str,
        use_web_search: bool = False,
        doc_k: int = 3
    ) -> dict:
        """
        Perform hybrid search across documents and optionally the web

        Args:
               query: Search query string
               use_web_search: Boolean flag to enable/disable web search
               doc_k: Number of documents to retrieve from vector store
        Returns:
               Dictionary containing document results and web results
        """
        results = {
            "query": query,
            "document_results": [],
            "web_results": None
        }
        
        # Document search (if vector store is initialized)
        if self.vector_store.is_initialized:
            docs = self.vector_store.search(query, k=doc_k)
            results["document_results"] = docs
        
        # Web search (if enabled)
        if use_web_search:
            web_results = self.tavily.search(query)
            results["web_results"] = web_results
        
        return results
    
    def format_hybrid_context(
        self,
        doc_results: List,
        web_results: Optional[str] = None
    ) -> str:
        """
        Format combined hybrid search results into a single context string

        Args:
               doc_results: List of Document objects from local search
               web_results: Formatted string of web search results (optional)
        Returns:
               Combined context string formatted for LLM consumption
        """
        context_parts = []
        
        # Add document context
        if doc_results:
            context_parts.append("=== From Your Documents ===")
            for i, doc in enumerate(doc_results, 1):
                source = doc.metadata.get("source", "Unknown")
                context_parts.append(f"[Doc {i}] ({source}):\n{doc.page_content}")
        
        # Add web context
        if web_results:
            context_parts.append("\n=== From Web Search ===")
            context_parts.append(web_results)
        
        return "\n\n".join(context_parts) if context_parts else "No context available."