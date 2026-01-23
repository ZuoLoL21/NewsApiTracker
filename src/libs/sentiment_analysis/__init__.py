from src.libs.sentiment_analysis.absa import ABSASentimentAnalyzer
from src.libs.sentiment_analysis.base import SentimentAnalyzer
from src.libs.sentiment_analysis.llm import LLMSentimentAnalyzer

__all__ = ["ABSASentimentAnalyzer", "LLMSentimentAnalyzer", "get_sentiment_analyzer"]

TYPE_TO_SA = {
    "llm": LLMSentimentAnalyzer,
    "absa": ABSASentimentAnalyzer,
}
def get_sentiment_analyzer(type_:str, topic: str) -> SentimentAnalyzer:
    return TYPE_TO_SA[type_](topic)
