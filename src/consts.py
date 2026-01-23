from datetime import date
from enum import Enum
from pathlib import Path

DEFAULT_TOPIC="Cloud Computing"

TOPICS=["Cloud Computing"]

class TypesOfSA(str, Enum):
    LLM = "llm"
    ABSA = "absa"

SENTIMENT_ANALYSIS_MODEL:TypesOfSA=TypesOfSA.ABSA

SCRAPING_END_DATE = date.today()

LOGGING_LOCATION=(Path(__file__).parent.resolve() / "logs.log").absolute().resolve()

