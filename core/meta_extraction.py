# core/meta_extraction.py

from pathlib import Path
from typing import List, Dict
import json

from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.documents import Document

from config.settings import settings
from core.structure import ResearchPaper


METADATA_PATH = Path(settings.METADATA_FILE)


class MetaExtraction:
    """
    Extracts structured research paper metadata and persists it to JSON
    """

    def __init__(self, page_metadata: Dict, section_doc: List[Document]) -> None:
        """
        Initialize the MetaExtraction system with page metadata and section documents

        Args:
              page_metadata: Dictionary containing page-level metadata
              section_doc: List of Document objects representing sections
        Returns:
              None
        """
        self.page_metadata = page_metadata
        self.section_doc = section_doc

        self.llm = ChatGroq(
            model=settings.GPT_MODEL_NAME,
            temperature=settings.TEMPRATURE
        )

        self.prompt = ChatPromptTemplate.from_messages([
            (
                "system",
                """You are an academic metadata extraction system.
                Extract ONLY verified information.
                Output must strictly match the schema.
                """
            ),
            ("human", "Extract structured metadata from this PDF content:\n\n{pdf_section}")
        ])

        METADATA_PATH.parent.mkdir(parents=True, exist_ok=True)

    def _load_metadata(self) -> list[dict]:
        """
        Loads existing metadata records from the JSON storage file

        Args:
              No arguments
        Returns:
              List of dictionaries containing metadata records
        """
        if METADATA_PATH.exists():
            with open(METADATA_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        return []

    def _save_metadata(self, store: list[dict]) -> None:
        """
        Writes the provided list of metadata records to the JSON storage file

        Args:
              store: List of dictionaries to save
        Returns:
              None
        """
        with open(METADATA_PATH, "w", encoding="utf-8") as f:
            json.dump(store, f, indent=2, ensure_ascii=False)

    def _upsert_metadata(self, record: dict) -> None:
        """
        Updates an existing metadata record or appends a new one based on paper_id

        Args:
              record: Dictionary containing the metadata record to upsert
        Returns:
              None
        """
        store = self._load_metadata()

        for i, existing in enumerate(store):
            if existing.get("paper_id") == record.get("paper_id"):
                store[i] = record
                self._save_metadata(store)
                return

        store.append(record)
        self._save_metadata(store)

    def _attach_metadata(self, metadata: dict) -> None:
        """
        Updates the metadata of the stored section documents with the extracted metadata

        Args:
              metadata: Dictionary of extracted metadata to attach
        Returns:
              None
        """
        for doc in self.section_doc:
            doc.metadata.update(metadata)

    def _build_pdf_context(self) -> str:
        """
        Constructs a limited-word context string from the first few document chunks

        Args:
              No arguments
        Returns:
              String containing the concatenated text context
        """
        MAX_WORDS = 1500
        context_words = []
        total_words = 0

        for idx, doc in enumerate(self.section_doc):
            if idx >= 3:   # only first 3 chunks
                break

            words = doc.page_content.strip().split()
            remaining = MAX_WORDS - total_words

            if remaining <= 0:
                break

            if len(words) > remaining:
                words = words[:remaining]

            context_words.extend(words)
            total_words += len(words)

            print(f"Chunk {idx}: added {len(words)} words | total = {total_words}")
            print("=" * 80)

        return " ".join(context_words)


    def update_metadata(self) -> List[Document]:
        """
        Extracts metadata using LLM, persists it, and updates the document objects

        Args:
              No arguments
        Returns:
              List of Document objects with updated metadata
        """
        structured_llm = self.llm.with_structured_output(ResearchPaper)

        pdf_section = self._build_pdf_context()
        print(len(pdf_section.split(" ")))
        prompt_value = self.prompt.invoke({
            "pdf_section": pdf_section
        })
        
        paper: ResearchPaper = structured_llm.invoke(
            prompt_value.to_messages()
        )

        metadata = {
            "paper_id": paper.paper_id,
            "title": paper.title,
            "authors": paper.authors,
            "year": paper.year,
            "venue": paper.venue,
            "keywords": paper.keywords,
            "summary": paper.summary
        }

        self._upsert_metadata(metadata)
        self._attach_metadata(metadata)

        return self.section_doc