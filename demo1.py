from core.document_processing import DocumentProcessor
from core.embedding import EmbeddingManager
from core.vector_store import VectorStoreManager
from core.chain import RAGChain
from core.structure import ResearchPaper
from core.chunking import Chunking
from core.meta_extraction import MetaExtraction
from langchain_core.documents import Document
from pathlib import Path
import sqlite3


print("\nSTEP 0. Loading document ")
# dir_path = "Nvidia_tidar.pdf"
dir_path = "attention_all_you_need.pdf"
print(f"Document path: {dir_path}")

print("\nSTEP 1. Processing document ")
processor = DocumentProcessor(path=dir_path)
document_ext = processor.process()
pdf_meta = processor.pdf_metadata

print("\nSTEP 2. Meta Extraction")

meta_extract = MetaExtraction(pdf_meta,document_ext)
document = meta_extract.update_metadata()
# print(document[0].metadata)

print("\nSTEP 3. Chunking document")
chunk_prosessor = Chunking(document=document)
chunk = chunk_prosessor.intiate_chunk()
print("\nSTEP 4. Embedding document")
embed = EmbeddingManager()
vs_man = VectorStoreManager()
vs_man.create_from_documents(chunk)

rag = RAGChain(vs_man)

result = rag.query("explain the attension mechanism in transformer")

print(result["answer"])
print("="*70)
print(f"Sources: {result['sources']}")

db_path = "data/sqlite_db/research_papers.db"

print("\n print the table in db")

conn = sqlite3.connect(db_path)
cursor = conn.cursor()
cursor.execute("SELECT * FROM research_papers")
rows = cursor.fetchall()
for row in rows:
    print(row)