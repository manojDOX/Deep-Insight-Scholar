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
        """
        Initialize the DocumentProcessor with text splitting parameters.
        Args:
            chunk_size (int, optional): The size of each text chunk. Defaults to None, which uses settings.CHUNK_SIZE.
            chunk_overlap (int, optional): The overlap between text chunks. Defaults to None, which uses settings.CHUNK_OVERLAP.
        """
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
        """
        Extract sections from the full text of a research paper.
        Args:
            text (str): The full text of a research paper.
        Returns:
            List[PaperSection]: A list of PaperSection objects.
        """
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
            Build a ResearchPaper object from extracted sections and metadata.
            Args:
                sections (List[PaperSection]): A list of PaperSection objects.
                full_text (str): The full text of the research paper.
                title (str): The title of the research paper.
                authors (List[str]): A list of authors of the research paper.
                year (Optional[int], optional): The year of publication of the research paper. Defaults to None.
                venue (Optional[str], optional): The venue of publication of the research paper. Defaults to None.
                keywords (Optional[List[str]], optional): A list of keywords associated with the research paper. Defaults to None.    
            Returns:
                ResearchPaper: A ResearchPaper object.
            """

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
        Chunk the research paper into smaller text segments with metadata.
        Args:
            paper (ResearchPaper): The research paper to be chunked.
        Returns:
            List[Dict]: A list of dictionaries, each containing 'text' and 'metadata' keys.
        """
        chunks = []

        for section in paper.sections:
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
        Process a research paper from a file and return the ResearchPaper object and its chunks.
        Args:
            file_path (str): The path to the research paper file.
            paper_id (str): The unique identifier for the research paper.
            title (str): The title of the research paper.
            authors (List[str]): A list of authors of the research paper.
            year (Optional[int], optional): The year of publication of the research paper. Defaults to None.
            venue (Optional[str], optional): The venue of publication of the research paper. Defaults to None.
            keywords (Optional[List[str]], optional): A list of keywords associated with the research paper. Defaults to None.
        Returns:
            Tuple[ResearchPaper, List[Dict]]: A tuple containing the ResearchPaper object and its chunks.
        """

        documents = self.load_pdf(file_path)

        full_text = self.documents_to_texts(documents)


        sections = self.extract_sections_from_text(full_text)

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
        chunks = self.chunk_research_paper(paper)

        return paper, chunks