from abc import ABC, abstractmethod
from enum import Enum


class Sentiment(str, Enum):
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"
    UNKNOWN = "unknown"
    INVALID = "invalid"

class SentimentAnalyzer(ABC):
    def __init__(self, topic: str):
        self.topic = topic

    @abstractmethod
    def sentiment_analysis(self, context:dict) -> Sentiment:
        ...

