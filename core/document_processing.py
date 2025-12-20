import pypdf
from pathlib import Path
from langchain_community.document_loaders import PyPDFLoader,TextLoader
from typing import List,Optional
from langchain_core.documents import Document
from core.structure import PaperSection, ResearchPaper
from langchain_text_splitters import RecursiveCharacterTextSplitter
from config import settings

class DocumentProcessor:

    def __init__(self, chunk_size: int = None, chunk_overlap: int = None):
        # Provide default values if both settings and parameters are None
        self.chunk_size = chunk_size if chunk_size is not None else (settings.CHUNK_SIZE if settings.CHUNK_SIZE is not None else 1000)
        self.chunk_overlap = chunk_overlap if chunk_overlap is not None else (settings.CHUNK_OVERLAP if settings.CHUNK_OVERLAP is not None else 200)

        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )
        self.SECTION_HEADERS = [
            "abstract",
            "introduction",
            "method",
            "methodology",
            "results",
            "conclusion",
            "references"
        ]

    def load_pdf(self, file_path:str)-> List[Document]:
        """
        Load and extract text from a PDF,txt,doc or other file.
        Args:
            file_path (str): The path to the PDF,txt,doc or other file.
        Returns:
            str: The extracted text from the PDF,txt,doc or other.
        """
        extension =  Path(file_path).suffix.lower()

        if extension == ".pdf":
            loader = PyPDFLoader(str(file_path))
        elif extension in [".txt", ".doc", ".docx"]:
            loader = TextLoader(str(file_path))
        else:
            raise ValueError(f"Unsupported file format: {extension} please provide a PDF,txt,doc or other file.")
        return loader.load()
    
    def documents_to_texts(self, documents: List[Document]) -> str:
        """
        Convert a list of Document objects to text strings.
        Args:
            documents (List[Document]): A list of Document objects.
        Returns:
            str: complete text strings extracted from the Document objects.
        """
        return "\n".join(doc.page_content for doc in documents)
    
    def extract_sections_from_text(self, text: str) -> List[PaperSection]:
        sections = []
        current_section = None
        current_content = []

        for line in text.split("\n"):
            stripped_line = line.strip().lower()

            matched_section = None
            for header in self.SECTION_HEADERS:
                if stripped_line.startswith(header) or stripped_line.endswith(header):
                    matched_section = header
                    break

            if matched_section:
                if current_section:
                    sections.append(
                        PaperSection(
                            section_name=current_section,
                            content="\n".join(current_content).strip()
                        )
                    )
                current_section = matched_section
                current_content = []
            else:
                if current_section:
                    current_content.append(line)

        if current_section:
            sections.append(
                PaperSection(
                    section_name=current_section,
                    content="\n".join(current_content).strip()
                )
            )

        return sections
    
    def build_research_paper(
            self,
            paper_id: str,
            sections: List[PaperSection],
            full_text: str,
            title: str,
            authors: List[str],
            year: Optional[int] = None,
            venue: Optional[str] = None,
            keywords: Optional[List[str]] = None
        ) -> ResearchPaper:
            """
            Build a ResearchPaper object from extracted sections and user metadata
            """

            # Extract abstract automatically from sections
            abstract = ""
            for sec in sections:
                if sec.section_name == "abstract":
                    abstract = sec.content
                    break

            paper = ResearchPaper(
                paper_id=paper_id,
                title=title,
                authors=authors,
                abstract=abstract,
                full_text=full_text,
                sections=sections,
                year=year,
                venue=venue,
                keywords=keywords or []
            )

            return paper
    def chunk_research_paper(self, paper: ResearchPaper):
        """
        Convert ResearchPaper sections into chunks with metadata
        """
        chunks = []

        for section in paper.sections:
            # Optional: skip references from embeddings
            if section.section_name == "references":
                continue

            section_chunks = self.text_splitter.split_text(section.content)

            for chunk in section_chunks:
                chunks.append({
                    "text": chunk,
                    "metadata": {
                        "paper_id": paper.paper_id,
                        "section": section.section_name,
                        "year": paper.year,
                        "venue": paper.venue
                    }
                })

        return chunks

    
    def process(
        self,
        file_path: str,
        paper_id: str,
        title: str,
        authors: List[str],
        year: Optional[int] = None,
        venue: Optional[str] = None,
        keywords: Optional[List[str]] = None
    ):
        """
        Full pipeline:
        PDF → Sections → ResearchPaper → Chunks
        """

        # Step 1: Load PDF
        documents = self.load_pdf(file_path)

        # Step 2: Combine text
        full_text = self.documents_to_texts(documents)

        # Step 3: Extract sections
        sections = self.extract_sections_from_text(full_text)

        # Step 4: Build ResearchPaper (user + extracted metadata)
        paper = self.build_research_paper(
            paper_id=paper_id,
            sections=sections,
            full_text=full_text,
            title=title,
            authors=authors,
            year=year,
            venue=venue,
            keywords=keywords
        )

        # Step 5: Chunk the paper
        chunks = self.chunk_research_paper(paper)

        return paper, chunks