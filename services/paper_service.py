from typing import List, Dict, Tuple, Optional
import streamlit as st


class PaperService:
    """
    Reads and filters paper metadata from Streamlit session memory.
    Data source: st.session_state.paper_metadata_store
    """

    @staticmethod
    def fetch_all() -> List[Dict]:
        """
        Fetch all papers from session memory.
        Returns empty list if no papers exist.
        """
        return st.session_state.get("paper_metadata_store", [])

    @staticmethod
    def get_years(papers: List[Dict]) -> List[int]:
        """
        Extract unique years from papers.
        """
        return sorted(
            {p.get("year") for p in papers if p.get("year") is not None}
        )

    @staticmethod
    def filter(
        papers: List[Dict],
        year_range: Optional[Tuple[int, int]] = None,
        keyword: Optional[str] = None
    ) -> List[Dict]:
        """
        Filter papers by year range and keyword.

        Args:
            papers: List of paper dictionaries
            year_range: (min_year, max_year)
            keyword: keyword to search in title, summary, or keywords

        Returns:
            Filtered list of papers
        """
        filtered = papers

        # ✅ Year filter
        if year_range:
            min_year, max_year = year_range
            filtered = [
                p for p in filtered
                if p.get("year") is not None
                and min_year <= p["year"] <= max_year
            ]

        # ✅ Keyword filter
        if keyword:
            kw = keyword.lower()
            filtered = [
                p for p in filtered
                if (
                    kw in p.get("title", "").lower()
                    or kw in p.get("summary", "").lower()
                    or kw in " ".join(p.get("keywords", [])).lower()
                )
            ]

        return filtered
