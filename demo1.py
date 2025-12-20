from core import DocumentProcessor
from core.embedding import embeddingmanager
from core.vector_store import vectorstoremanager
from core.document_adapter import DocumentAdapter


def main():

    print("\nSTEP 1. Processing document and creating chunks")

    processor = DocumentProcessor(chunk_size=500, chunk_overlap=100)

    paper, chunks = processor.process(
        file_path="attention_all_you_need.pdf",
        paper_id="ATTN_2017_001",
        title="Attention Is All You Need",
        authors=["Ashish Vaswani", "Noam Shazeer", "Niki Parmar"],
        year=2017,
        venue="NeurIPS",
        keywords=["transformer", "attention"]
    )

    print(f"Document processed into {len(chunks)} chunks")

    print("\nSTEP 2. Creating embedding manager")

    embedder = embeddingmanager(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    print("Embedding model loaded:")
    print(f"Model name: {embedder.model_name}")
    print(f"Embedding dimension: {embedder.get_embedding_dimension()}")

    print("\nSTEP 3. Converting chunks to LangChain Documents")

    documents = DocumentAdapter.chunks_to_documents(
        chunks
    )

    print("\nSTEP 4. Building vector store")

    vs_manager = vectorstoremanager(embedding_manager=embedder)
    vs_manager.create_from_documents(documents)

    print(f"Vector store created with {len(documents)} documents")

    print("\nSTEP 5. Semantic search (top-3)")

    test_queries = [
        "What is the main idea of the transformer?",
        "How does attention work in this paper?",
        "What experiments were conducted?"
    ]

    for query in test_queries:
        print(f"\nQuery: {query}")

        results = vs_manager.serch(query, k=3)

        for doc in results:
            print("=" * 70)
            print("SECTION:", doc.metadata.get("section"))
            print(doc.page_content[:400])
            print("=" * 70)


    print("\nSTEP 6. Saving vector store")

    vs_manager.save()
    print(f"Vector store saved to {vs_manager.index_path}")


    print("\nSTEP 7. Loading vector store and re-testing")

    vs_loader = vectorstoremanager(embedding_manager=embedder)
    vs_loader.load()

    retriever = vs_loader.get_retriever(k=3)

    test_results = retriever.invoke(
        "Explain the attention mechanism used in the transformer"
    )

    print("\nTest search after loading vector store:")

    for r in test_results:
        print("=" * 70)
        print("SECTION:", r.metadata.get("section"))
        print(r.page_content[:400])
        print("=" * 70)


if __name__ == "__main__":
    main()
