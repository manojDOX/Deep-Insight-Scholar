import json
import os
from typing import Dict, List
from storage.base import PaperRepository

class JsonPaperRepository(PaperRepository):
    """
    Temporary JSON-based repository.
    Suitable for Streamlit Cloud session-level persistence.
    """

    def __init__(self, file_path: str = None):
        # Streamlit Cloud safe path
        self.file_path = file_path or "/tmp/research_papers.json"
        self._ensure_file()

    def _ensure_file(self):
        if not os.path.exists(self.file_path):
            with open(self.file_path, "w") as f:
                json.dump([], f)

    def _read(self) -> List[Dict]:
        with open(self.file_path, "r") as f:
            return json.load(f)

    def _write(self, data: List[Dict]) -> None:
        with open(self.file_path, "w") as f:
            json.dump(data, f, indent=2)

    def save(self, paper: Dict) -> None:
        data = self._read()

        # UPSERT by title
        updated = False
        for i, existing in enumerate(data):
            if existing["title"] == paper["title"]:
                data[i] = paper
                updated = True
                break

        if not updated:
            data.append(paper)

        self._write(data)

    def fetch_all(self) -> List[Dict]:
        return self._read()
