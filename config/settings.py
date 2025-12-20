from dotenv import load_dotenv
from dataclasses import dataclass
import os

load_dotenv()

@dataclass
class Settings:

    _FAISS_INDEX_PATH:str = os.getenv("FAISS_INDEX_PATH")
    EMBEDDING_MODEL:str = os.getenv("EMBEDDING_MODEL")
    CHUNK_SIZE:int=int(os.getenv("CHUNK_SIZE"))
    CHUNK_OVERLAP:int=int(os.getenv("CHUNK_OVERLAP"))
    TOP_K_RESULTS:int=int(os.getenv("TOP_K_RESULTS"))

settings = Settings()