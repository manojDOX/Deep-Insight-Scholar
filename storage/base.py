from abc import ABC, abstractmethod
from typing import Dict, List

class PaperRepository(ABC):

    @abstractmethod
    def save(self, paper: Dict) -> None:
        pass

    @abstractmethod
    def fetch_all(self) -> List[Dict]:
        pass
