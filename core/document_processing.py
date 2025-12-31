from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader, TextLoader
from langchain_core.documents import Document
from core.structure import ResearchPaper
from typing import List, Optional,Dict
from pathlib import Path
import re





class DocumentProcessor:
    """
    Handles the loading, processing, and section-based segmentation of documents
    """
    def __init__(self,path:str=None
                 ):
        """
        Initializes the document processor with the file path

        Args:
              path: File path string to the document
        Returns:
              None
        """
        self.path=path

    def load_document(self)->List[Document]:
        """
        Loads the document content using the appropriate loader based on file extension

        Args:
              No arguments
        Returns:
              List of Document objects loaded from the file
        """

        if not Path(self.path).exists():
            raise ValueError(f"File {self.path} does not exist")
        

        if self.path.endswith(".pdf"):
            loader = PyPDFLoader(self.path)
        elif self.path.endswith(".docx"):
            loader = Docx2txtLoader(self.path)
        elif self.path.endswith(".txt"):
            loader = TextLoader(self.path,encoding="utf-8")
        else:
            raise ValueError(f"Unsupported file format {self.path}") 
        return loader.load()
    def _document_to_text(self,document:List[Document])->List[str]:
        """
        Converts a list of Documents into a clean, tokenized list of strings

        Args:
              document: List of Document objects
        Returns:
              List of string tokens from the document content
        """
        text = str()
        for doc in document:
            text+=doc.page_content
            text+=" "
        text = text.lower().replace("\n"," ").replace(":"," ")
        return text.split(" ")
    @property
    def pdf_metadata(self)->Dict:
        """
        Extracts metadata from the loaded document

        Args:
              No arguments
        Returns:
              Dictionary containing document metadata
        """
        doc  = self.load_document()
        _meta = doc[0].metadata
        return _meta

    def _section_info(self,text_list:List[str])->Dict:
        """
        Identifies logical sections in the text based on predefined patterns

        Args:
              text_list: List of string tokens representing the document text
        Returns:
              Dictionary mapping section names to their starting indices
        """
        SECTION_PATTERNS = {
            "abstract": ["abstract","abstract:","abstract."],
            "introduction": ["introduction",r"introduction[a-z\:\-]?"],
            "related_work": ["related work", "background"],
            "methodology": ["methodology", "methods", "approach"],
            "conclusion": ["conclusions", "future work","conclusion"],
            "references": ["references", "bibliography"]
        }
        curr_pos = 0
        page_dict = dict()
        page_dict["Paper title and author info"] = 0
        for key,value in SECTION_PATTERNS.items():
            for pattern in value:
                if pattern in text_list[curr_pos:]:
                    if pattern not in page_dict.keys():
                        page_dict[pattern]=curr_pos+text_list[curr_pos:].index(pattern)
                        curr_pos = page_dict[pattern]
                        break
        print(page_dict)
        return page_dict
    
        

    def _document_prep(self,page_dict:Dict,text_list:List[str])->List[Document]:
        """
        Segments the text list into Document objects corresponding to identified sections

        Args:
              page_dict: Dictionary of section indices
              text_list: List of string tokens
        Returns:
              List of Document objects with section metadata
        """
        value_list = list(page_dict.values())
        key = list(page_dict.keys())
        upadted_document = list()
        j = 1
        t = 0
        for i in range(len(key)-1):
            upadted_document.append(
                Document(
                    page_content = ' '.join(text_list[t:value_list[j]]),
                    metadata = {
                        "section": key[i],
                    }
                )
            )
            t = value_list[j]
            j+=1
        upadted_document.append(
            Document(
                page_content = ' '.join(text_list[t:]),
                metadata = {
                    "section": key[-1]
                }
            )
        )
        return upadted_document
    def process(self)->List[Document]:
        """
        Executes the full pipeline: load, convert, identify sections, and segment document

        Args:
              No arguments
        Returns:
              List of processed Document objects split by section
        """

        loaded_document = self.load_document()
        text = self._document_to_text(loaded_document)
        section_dict = self._section_info(text)
        upadted_document = self._document_prep(section_dict,text)
        return upadted_document