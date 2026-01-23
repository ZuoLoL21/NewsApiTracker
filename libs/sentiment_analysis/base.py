from abc import ABC, abstractmethod
from enum import Enum

from pydantic import BaseModel

class Sentiment(str, Enum):
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"
    UNKNOWN = "unknown"

class SentimentAnalyzer(ABC):
    def __init__(self, topic: str):
        self.topic = topic

    @abstractmethod
    def sentiment_analysis(self, context:dict) -> Sentiment:
        ...

