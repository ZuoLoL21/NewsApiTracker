import logging

from dotenv import load_dotenv
import os
import requests
from datetime import date, timedelta, datetime

from consts import QUERY_TERM
from libs.models import ParsedArticleList
from libs.local_helpers.pydantic_helpers import save_model
from libs.local_helpers.path_helpers import get_project_path

logger = logging.getLogger(__name__)

load_dotenv()


API_KEY = os.getenv("NEWS_API_KEY")

URL = "https://newsapi.org/v2/everything"

DAYS_OF_INTEREST = 1


def main() -> str:
    today = date.today()
    query_data = today - timedelta(days=DAYS_OF_INTEREST)

    params = {
        "q": QUERY_TERM,
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

    filename = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    save_model(validated_data, get_project_path(f"Storage/{filename}.txt"))

    return filename

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)s - %(name)s - %(message)s"
    )
    main()