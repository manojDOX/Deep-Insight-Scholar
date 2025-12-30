# core/meta_extraction.py

from pathlib import Path
from typing import List, Dict
import json

from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.documents import Document

from config.settings import settings
from core.structure import ResearchPaper


METADATA_PATH = Path("data/metadata/metadata.json")


class MetaExtraction:
    """
    Extracts structured research paper metadata
    and persists it to JSON (backend-only).
    """

    def __init__(self, page_metadata: Dict, section_doc: List[Document]):
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

    # ---------------------------
    # Metadata persistence
    # ---------------------------

    def _load_metadata(self) -> list[dict]:
        if METADATA_PATH.exists():
            with open(METADATA_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        return []

    def _save_metadata(self, store: list[dict]) -> None:
        with open(METADATA_PATH, "w", encoding="utf-8") as f:
            json.dump(store, f, indent=2, ensure_ascii=False)

    def _upsert_metadata(self, record: dict) -> None:
        store = self._load_metadata()

        for i, existing in enumerate(store):
            if existing.get("paper_id") == record.get("paper_id"):
                store[i] = record
                self._save_metadata(store)
                return

        store.append(record)
        self._save_metadata(store)

    # ---------------------------
    # Helpers
    # ---------------------------

    def _attach_metadata(self, metadata: dict) -> None:
        for doc in self.section_doc:
            doc.metadata.update(metadata)

    def _build_pdf_context(self) -> str:
        """
        Build context from document chunks with a strict global word limit.
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

            # Trim current chunk if it exceeds remaining budget
            if len(words) > remaining:
                words = words[:remaining]

            context_words.extend(words)
            total_words += len(words)

            print(f"Chunk {idx}: added {len(words)} words | total = {total_words}")
            print("=" * 80)

        return " ".join(context_words)


    # ---------------------------
    # Public API
    # ---------------------------

    def update_metadata(self) -> List[Document]:
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
