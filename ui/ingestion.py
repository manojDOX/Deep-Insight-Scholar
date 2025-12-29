import streamlit as st
from core.document_processing import DocumentProcessor
from core.chunking import Chunking
from core.meta_extraction import MetaExtraction
from core.vector_store import VectorStoreManager
from ui.components import save_uploaded_file

def render_ingestion():
    st.header("📄 Load & Embed Research Papers")

    uploaded_files = st.file_uploader(
        "Upload PDF papers",
        type=["pdf"],
        accept_multiple_files=True
    )

    if st.button("⚙️ Process & Embed"):
        if "vector_store" not in st.session_state or st.session_state.vector_store is None:
            st.session_state.vector_store = VectorStoreManager()

        vector_store = st.session_state.vector_store


        for file in uploaded_files:
            path = save_uploaded_file(file)

            processor = DocumentProcessor(path=path)
            docs = processor.process()
            meta = processor.pdf_metadata

            extractor = MetaExtraction(meta, docs)
            enriched_docs = extractor.update_metadata()

            chunker = Chunking(document=enriched_docs)
            chunks = chunker.intiate_chunk()

            vector_store.add_documents(chunks)
            # vector_store.create_from_documents(chunks)

        st.session_state.vector_store = vector_store
        st.session_state.papers_loaded = True

        st.success("Papers embedded successfully")
