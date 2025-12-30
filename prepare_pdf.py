# scripts/prepare_pdf.py

from pathlib import Path

from core.document_processing import DocumentProcessor
from core.chunking import Chunking
from core.meta_extraction import MetaExtraction
from core.vector_store import VectorStoreManager


RAW_PDF_DIR = Path("data/raw_pdf")
FAISS_DIR = Path("data/faiss_index")


def prepare_directories() -> None:
    FAISS_DIR.mkdir(parents=True, exist_ok=True)


def ingest_pdfs() -> None:
    prepare_directories()

    vector_store = VectorStoreManager()

    pdf_files = list(RAW_PDF_DIR.glob("*.pdf"))
    if not pdf_files:
        raise RuntimeError("No PDF files found in data/raw_pdf")

    for pdf_path in pdf_files:
        processor = DocumentProcessor(path=str(pdf_path))
        docs = processor.process()
        pdf_metadata = processor.pdf_metadata

        extractor = MetaExtraction(pdf_metadata, docs)
        enriched_docs = extractor.update_metadata()  # ✅ JSON saved HERE

        chunker = Chunking(document=enriched_docs)
        chunks = chunker.intiate_chunk()

        vector_store.add_documents(chunks)

    vector_store.save()


if __name__ == "__main__":
    ingest_pdfs()
    print("✅ PDFs processed, FAISS index & structured metadata saved.")
