from abc import ABC, abstractmethod
from enum import Enum

from pydantic import BaseModel

class Sentiment(str, Enum):
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"
    UNKNOWN = "unknown"

class SentimentAnalyzer(ABC):
    @abstractmethod
    def sentiment_analysis(self, topic: str, context:BaseModel) -> Sentiment:
        ...

