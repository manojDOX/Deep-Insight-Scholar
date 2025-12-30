# services/paper_service.py

from typing import List, Dict, Tuple, Optional
from pathlib import Path
import json


METADATA_PATH = Path("data/metadata/metadata.json")


class PaperService:
    """
    Reads and filters paper metadata from persisted JSON storage.
    Data source: data/metadata/metadata.json
    """

    @staticmethod
    def fetch_all() -> List[Dict]:
        """
        Fetch all papers from metadata.json.
        Returns empty list if file does not exist.
        """
        if not METADATA_PATH.exists():
            return []

        with open(METADATA_PATH, "r", encoding="utf-8") as f:
            return json.load(f)

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
        """
        filtered = papers

        if year_range:
            min_year, max_year = year_range
            filtered = [
                p for p in filtered
                if p.get("year") is not None
                and min_year <= p["year"] <= max_year
            ]

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
