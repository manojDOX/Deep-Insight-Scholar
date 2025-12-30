import streamlit as st
from services.paper_service import PaperService
from services.rag_service import RAGService
from tools.tavily_search import TavilySearchTool, HybridSearchManager


def render_chat(scoped: bool = False):
    st.header("🤖 Research Chat Assistant")

    papers = PaperService.fetch_all()
    if not papers:
        st.info("📄 No papers available to chat with.")
        return

    if not st.session_state.get("vector_store"):
        st.warning("Vector store not initialized.")
        return

    active_title = st.session_state.get("active_paper_title")

    metadata_filter = None
    if scoped and active_title:
        st.caption(f"💡 Context restricted to **{active_title}**")
        metadata_filter = {"title": active_title}

    else:
        retriever = st.session_state.vector_store.get_retriever(k=5)

    rag_key = f"rag_{active_title}" if scoped and active_title else "rag_global"

    if rag_key not in st.session_state:
        st.session_state[rag_key] = RAGService(
            st.session_state.vector_store
        )

    rag_chain = st.session_state[rag_key]


   
    search_mode = st.radio(
        "Search Mode",
        options =  ["📄 Documents Only"] if scoped else ["📄 Documents Only","🌐 Web Search (Tavily)","🔀 Hybrid (Docs + Web)"],
        horizontal=True,
        key=f"search_mode_{'scoped' if scoped else 'global'}"
    )

    tavily_tool = TavilySearchTool()
    hybrid_search = HybridSearchManager(
        st.session_state.vector_store,
        tavily_tool
    )

   
    query = st.chat_input(
        "Ask your research question",
        key=f"chat_input_{'scoped' if scoped else 'global'}"
    )

    if not query:
        return

    with st.chat_message("user"):
        st.write(query)

    with st.chat_message("assistant"):
        sources = []
        sections_used = []

        if search_mode == "📄 Documents Only":
            result = rag_chain.ask(query,metadata_filter=metadata_filter)
            st.write(result["answer"])

            sources = result.get("sources", [])
            documents = result.get("documents", [])
            sections_used = extract_sections(documents)

        elif search_mode == "🌐 Web Search (Tavily)":
            web_context = tavily_tool.search(query)
            answer = rag_chain.rag.generate(query=query, context=web_context)

            st.write(answer)
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

            answer = rag_chain.rag.generate(query=query, context=context)
            st.write(answer)

            documents = hybrid_results["document_results"]
            sources = list({
                doc.metadata.get("title", "Unknown")
                for doc in documents
            } | {"Tavily Web Search"})

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
