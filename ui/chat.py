import streamlit as st
from services.paper_service import PaperService
from services.rag_service import RAGService
from tools.tavily_search import TavilySearchTool, HybridSearchManager


def render_chat():
    st.header("🤖 Research Chat Assistant")

    papers = PaperService.fetch_all()

    if not papers:
        st.info("📄 No papers available to chat with.")
        st.markdown("Please upload and process research papers first.")
        return

    if not st.session_state.get("vector_store"):
        st.warning("Vector store not initialized.")
        return

    # Initialize RAG service once
    if "rag_chain" not in st.session_state or st.session_state.rag_chain is None:
        st.session_state.rag_chain = RAGService(
            st.session_state.vector_store
        )


    search_mode = st.radio(
        "Search Mode",
        options=[
            "📄 Documents Only",
            "🌐 Web Search (Tavily)",
            "🔀 Hybrid (Docs + Web)"
        ],
        horizontal=True
    )

    # Initialize Tavily + Hybrid search tools
    tavily_tool = TavilySearchTool()
    hybrid_search = HybridSearchManager(
        st.session_state.vector_store,
        tavily_tool
    )


    query = st.chat_input("Ask your research question")

    if not query:
        return

    with st.chat_message("user"):
        st.write(query)


    with st.chat_message("assistant"):
        sources = []


        if search_mode == "📄 Documents Only":
            result = st.session_state.rag_chain.ask(query)

            st.write(result["answer"])
            sources = result.get("sources", [])
            documents = result.get("documents", [])
            sections_used = extract_sections(documents)

        elif search_mode == "🌐 Web Search (Tavily)":
            web_context = tavily_tool.search(query)

            answer = st.session_state.rag_chain.rag.generate(
                query=query,
                context=web_context
            )

            st.write(answer)
            sources = ["Tavily Web Search"]
            sections_used = ["Web Search (No document sections)"]

        else:
            hybrid_results = hybrid_search.search(
                query=query,
                use_web_search=True
            )

            context = hybrid_search.format_hybrid_context(
                hybrid_results["document_results"],
                hybrid_results["web_results"]
            )

            answer = st.session_state.rag_chain.rag.generate(
                query=query,
                context=context
            )

            st.write(answer)
            documents = hybrid_results["document_results"]
            # Collect document + web sources
            doc_sources = [
                doc.metadata.get("title", "Unknown")
                for doc in documents
            ]

            sources = list(set(doc_sources + ["Tavily Web Search"]))
            sections_used = extract_sections(documents)

        if sources:
            with st.expander("📚 Sources"):
                for src in sources:
                    st.write(f"- {src}")
        if sections_used:
            with st.expander("📑 Sections Used"):
                for sec in sections_used:
                    st.write(f"- {sec}")

def extract_sections(documents):
    sections = []
    for doc in documents:
        section = doc.metadata.get("section")
        if section:
            sections.append(section)
    return sorted(set(sections))