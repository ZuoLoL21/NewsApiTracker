import logging

from dotenv import load_dotenv

from libs.db_helpers import add_to_db
from libs.models import ParsedArticleList
from libs.local_helpers.path_helpers import get_project_path
from libs.local_helpers.pydantic_helpers import load_model
from libs.sentiment_analysis import get_sentiment_analyzer
from libs.sentiment_analysis.base import SentimentAnalyzer, Sentiment
from consts import DEFAULT_TOPIC, SENTIMENT_ANALYSIS_MODEL

logger = logging.getLogger(__name__)
load_dotenv()

def _retry_unknown(article) -> Sentiment:
    # TODO: Add scraping for UNKNOWN to improve
    return Sentiment.UNKNOWN


def process(model:ParsedArticleList, topic:str) -> None:
    sentiment_analyser: SentimentAnalyzer = get_sentiment_analyzer(SENTIMENT_ANALYSIS_MODEL.value, DEFAULT_TOPIC)

    for article in model.articles:
        answer = sentiment_analyser.sentiment_analysis(article.model_dump())
        if answer is Sentiment.INVALID:
            continue

        if answer is Sentiment.UNKNOWN:
            answer_t = _retry_unknown(article)
            logger.debug(f"Retrying unknown article previous {answer}, current {answer_t}")
            answer = answer_t

        logger.info(f"{article.title}\n{answer}")

        add_to_db(article, answer, topic)


if __name__ == "__main__":
    TMP_NAME = "2026-01-19_21-14-29.txt"

    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)s - %(name)s - %(message)s"
    )
    logging.getLogger("httpx").setLevel(logging.WARNING)

    parsed_list: ParsedArticleList = load_model(
        ParsedArticleList, get_project_path(f".examples/{TMP_NAME}")
    )
    process(parsed_list, DEFAULT_TOPIC)

