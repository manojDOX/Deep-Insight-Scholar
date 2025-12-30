from config.settings import Settings
from langchain_groq import ChatGroq
from core.structure import ResearchPaper
from langchain_core.prompts import ChatPromptTemplate
from typing import List, Dict
from langchain_core.documents import Document
import streamlit as st

INFO_PDF = """
use this context to extract the following information from the document and Metadata:
don't inculde any other information than from given text information.
Metadata:
{metadata}

Document Sections:
{section_context}
"""


class MetaExtraction:
    """
    Extracts structured metadata from a research paper
    and stores it in Streamlit session memory (temporary).
    """

    def __init__(
        self,
        page_metadata: Dict,
        section_doc: List[Document]
    ):
        self.page_metadata = page_metadata
        self.section_doc = section_doc

        # ✅ Streamlit session memory init (SAFE)
        if "paper_metadata_store" not in st.session_state:
            st.session_state.paper_metadata_store = []

        self.llm = ChatGroq(
            model=Settings.GPT_MODEL_NAME,
            temperature=Settings.TEMPRATURE
        )

        self.prompt = ChatPromptTemplate.from_messages([
            (
                "system",
                """Extract structured information from the given research paper.
                In summary, rewrite the content in a clear, concise, and easy-to-read academic style.

                Instructions for summary:
                - Use simple and formal academic language
                - Avoid unnecessary jargon and repetition
                - Keep sentences short and well structured
                - Preserve the original meaning and technical accuracy
                - Do NOT introduce new information
                - Present the summary as a coherent paragraph

                The output should be suitable for:
                - Research paper summaries
                - Academic dashboards
                - Structured information storage
                """
            ),
            ("human", INFO_PDF)
        ])

    def build_context(self) -> str:
        if not self.section_doc:
            raise ValueError("No document sections provided")

        context = ""
        for doc in self.section_doc[:3]:
            context += f"\n{doc.metadata.get('section', '')}\n"
            context += doc.page_content

        return context

    def build_prompt(self):
        return self.prompt.invoke({
            "metadata": self.page_metadata,
            "section_context": self.build_context()
        })

    def metadata_doc(self, prompt_response: Dict):
        for doc in self.section_doc:
            doc.metadata.update(prompt_response)
        return self.section_doc

    def save_metadata_to_session(self, updated_meta: Dict):
        """
        Store or update research paper metadata in Streamlit session memory.
        Title is used as PRIMARY KEY.
        """
        store = st.session_state.paper_metadata_store

        # UPSERT by title
        for i, existing in enumerate(store):
            if existing["title"] == updated_meta["title"]:
                store[i] = updated_meta
                return

        store.append(updated_meta)
    def update_metadata(self):
        structured_llm = self.llm.with_structured_output(ResearchPaper)

        prompt_value = self.build_prompt()

        paper: ResearchPaper = structured_llm.invoke(
            prompt_value.to_messages()
        )

        updated_meta = {
            "title": paper.title,
            "paper_id": paper.paper_id,
            "authors": paper.authors,
            "year": paper.year,
            "venue": paper.venue,
            "keywords": paper.keywords,
            "summary": paper.summary
        }

        # ✅ Store in session (instead of SQLite)
        self.save_metadata_to_session(updated_meta)

        # ✅ Attach metadata to all document chunks
        self.metadata_doc(updated_meta)

        return self.section_doc
