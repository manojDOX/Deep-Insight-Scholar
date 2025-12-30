from pydantic import BaseModel, Field
from typing import List, Optional

class ResearchPaper(BaseModel):
    """
    Structured metadata for a research paper.
    """
    title: str = Field(
        description="Exact title of the research paper."
    )

    paper_id: Optional[str] = Field(
        default=None,
        description="Unique identifier such as DOI or paper ID. Null if not found."
    )

    authors: List[str] = Field(
        description="List of author names as strings."
    )

    year: Optional[int] = Field(
        default=None,
        description="Publication year as a 4-digit integer. Use null if not available."
    )

    venue: Optional[str] = Field(
        default=None,
        description="Conference or journal name. Use null if not available."
    )

    keywords: List[str] = Field(
        description="Important keywords representing the core contribution."
    )

    summary: List[str] = Field(
        description=(
            "5–6 concise bullet points summarizing the paper. "
            "Include problem statement and proposed approach."
        )
    )
