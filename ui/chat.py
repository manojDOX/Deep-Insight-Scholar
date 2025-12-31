import streamlit as st

from services.paper_service import PaperService
from services.rag_service import RAGService
from tools.tavily_search import TavilySearchTool, HybridSearchManager
from core.chain import RAGChain


def render_chat(scoped: bool = False):
    """
    Renders the Streamlit chat interface, handling user input, search mode selection, and displaying RAG or web search results

    Args:
           scoped: Boolean flag to restrict context to the active paper (default: False)
    Returns:
           None
    """
    st.header("🤖 Research Chat Assistant")

    papers = PaperService.fetch_all()
    if not papers:
        st.info("📄 No papers available to chat with.")
        return

    try:
        rag_service = RAGService()
    except RuntimeError as e:
        st.warning(str(e))
        return

    rag_chain: RAGChain = rag_service.rag

    active_title = st.session_state.get("active_paper_title")
    metadata_filter = None

    if scoped and active_title:
        st.caption(f"💡 Context restricted to **{active_title}**")
        metadata_filter = {"title": active_title}

    with st.form(key=f"chat_form_{'scoped' if scoped else 'global'}"):

        search_mode = st.radio(
            "Search Mode",
            options=(
                ["📄 Documents Only"]
                if scoped
                else [
                    "📄 Documents Only",
                    "🌐 Web Search (Tavily)",
                    "🔀 Hybrid (Docs + Web)",
                ]
            ),
            horizontal=True,
        )

        query = st.text_input(
            "Ask your research question",
            placeholder="Type and press Send",
        )

        submitted = st.form_submit_button("Send")

    if not submitted or not query:
        return

    st.subheader("🧠 Answer")

    tavily_tool = TavilySearchTool()
    hybrid_search = HybridSearchManager(
        rag_service.vector_store,
        tavily_tool
    )

    if search_mode == "📄 Documents Only":
        result = rag_service.ask(
            query=query,
            metadata_filter=metadata_filter
        )
        answer = result["answer"]
        sources = result.get("sources", [])
        sections_used = extract_sections(result.get("documents", []))

    elif search_mode == "🌐 Web Search (Tavily)":
        web_context = tavily_tool.search(query)
        answer = rag_chain.generate(query=query, context=web_context)
        sources = ["Tavily Web Search"]
        sections_used = ["Web Search"]

    else:
        hybrid_results = hybrid_search.search(
            query=query,
            use_web_search=True
        )
        context = hybrid_search.format_hybrid_context(
            hybrid_results["document_results"],
            hybrid_results["web_results"]
        )
        answer = rag_chain.generate(query=query, context=context)
        documents = hybrid_results["document_results"]
        sources = list({
            doc.metadata.get("title", "Unknown")
            for doc in documents
        } | {"Tavily Web Search"})
        sections_used = extract_sections(documents)

    st.write(answer)

    if sources:
        with st.expander("📚 Sources"):
            for src in sources:
                st.write(f"- {src}")

    if sections_used:
        with st.expander("📑 Sections Used"):
            for sec in sections_used:
                st.write(f"- {sec}")



def extract_sections(documents):
    """
    Extracts and deduplicates section names from the metadata of retrieved documents

    Args:
           documents: List of Document objects containing metadata
    Returns:
           Sorted list of unique section names
    """
    sections = []
    for doc in documents:
        section = doc.metadata.get("section")
        if section:
            sections.append(section)
    return sorted(set(sections))