from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader, TextLoader
from langchain_core.documents import Document
from core.structure import ResearchPaper
from typing import List, Optional,Dict
from pathlib import Path
import re





class DocumentProcessor:
    def __init__(self,path:str=None
                 ):
        self.path=path

    def load_document(self)->List[Document]:

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
        text = str()
        for doc in document:
            text+=doc.page_content
            text+=" "
        text = text.lower().replace("\n"," ").replace(":"," ")
        return text.split(" ")
    @property
    def pdf_metadata(self)->Dict:
        doc  = self.load_document()
        _meta = doc[0].metadata
        return _meta

    def _section_info(self,text_list:List[str])->Dict:
        """
        Extracts section based on the SECTION_PATTERNS values mentioned if found then
        the text view is redused to that section and update the page_dict with section 
        list position
        Args:
            text (str): string containing text of the document
            Dict: dictionary of sections list position for extraction
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

        loaded_document = self.load_document()
        text = self._document_to_text(loaded_document)
        section_dict = self._section_info(text)
        upadted_document = self._document_prep(section_dict,text)
        return upadted_document
    
        