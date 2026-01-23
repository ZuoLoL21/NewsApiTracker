import logging

from libs.models import ParsedArticleList
from libs.local_helpers.path_helpers import get_project_path
from libs.local_helpers.pydantic_helpers import load_model
from libs.sentiment_analysis.base import SentimentAnalyzer
from libs.sentiment_analysis.llm import LLMSentimentAnalyzer
from consts import QUERY_TERM

logging.basicConfig(level=logging.INFO, format="%(levelname)s - %(name)s - %(message)s")

TMP_NAME = "2026-01-19_21-14-29.txt"

sentiment_analyser:SentimentAnalyzer = LLMSentimentAnalyzer(QUERY_TERM)
model: ParsedArticleList = load_model(ParsedArticleList, get_project_path(f"Storage/{TMP_NAME}"))

for article in model.articles:
    answer = sentiment_analyser.sentiment_analysis(article.model_dump())

    logging.info(answer)