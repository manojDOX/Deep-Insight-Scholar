from pydantic import BaseModel
from typing import List, Optional


class PaperSection(BaseModel):
    section_name: str
    content: str


class ResearchPaper(BaseModel):
    paper_id: str
    title: str
    authors: List[str]
    abstract: str
    full_text: str
    sections: List[PaperSection]
    year: Optional[int]
    venue: Optional[str]
    keywords: List[str]
