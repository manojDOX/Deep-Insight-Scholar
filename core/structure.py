from pydantic import BaseModel,Field
from typing import List, Optional


class ResearchPaper(BaseModel):
    """
    A class representing a research paper.
    """
    title: str = Field(description="The title of the research paper. check in the query itself")
    paper_id: str = Field(description="A unique identifier for the research paper. usually mentioned in abstract or page info")
    authors: List[str] = Field(description="A list of authors of the research paper. in string- name; mail id; then appended list of that string") 
    year: int = Field(description="The year of publication of the research paper.")
    venue: str = Field(description="The venue where the research paper was published.")
    keywords: List[str] = Field(description="A list of keywords associated with the research paper which are important and justify the paper core meaning")
    summary: List[str] = Field(description="summarise the paper, Short Summary (5–6 bullets) in this format: Problem statement, Proposed approach this two appeneded in list")