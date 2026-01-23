import logging

from dotenv import load_dotenv
import os
import requests
from datetime import date, timedelta, datetime

from consts import DEFAULT_TOPIC
from libs.models import ParsedArticleList
from libs.local_helpers.pydantic_helpers import save_model
from libs.local_helpers.path_helpers import get_project_path

logger = logging.getLogger(__name__)
load_dotenv()


API_KEY = os.getenv("NEWS_API_KEY")
URL = "https://newsapi.org/v2/everything"
DAYS_OF_INTEREST = 1


def scrape(topic, date_given) -> ParsedArticleList:
    query_data = date_given - timedelta(days=DAYS_OF_INTEREST)

    params = {
        "q": topic,
        "from": query_data.isoformat(),
        "apiKey": API_KEY,
        "language": "en",
        "sortBy": "publishedAt",
    }

    response = requests.get(URL, params=params)

    if response.status_code != 200:
        logging.error(f"{response.status_code}\n{response.text}")
        exit(1)

    data = response.json()

    validated_data = ParsedArticleList.model_validate(data)
    return validated_data


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO, format="%(levelname)s - %(name)s - %(message)s"
    )
    returned_data = scrape(DEFAULT_TOPIC)
    filename = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    save_model(returned_data, get_project_path(f".examples/{filename}.txt"))