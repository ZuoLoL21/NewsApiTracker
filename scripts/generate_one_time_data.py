from dotenv import load_dotenv
import os
import requests
from datetime import date, timedelta, datetime

from libs.models import ParsedArticleList
from libs.local_helpers.pydantic_helpers import save_model
from libs.local_helpers.path_helpers import get_project_path

load_dotenv()

API_KEY = os.getenv("NEWS_API_KEY")
QUERY = os.getenv("QUERY_TERM")

URL = "https://newsapi.org/v2/everything"

DAYS_OF_INTEREST = 1

today = date.today()
query_data = today - timedelta(days=DAYS_OF_INTEREST)

PARAMS = {
    "q": QUERY,
    "from": query_data.isoformat(),
    "apiKey": API_KEY,
    "language": "en",
    "sortBy": "publishedAt",
}

response = requests.get(URL, params=PARAMS)

if response.status_code != 200:
    print(f"Error: Request failed with status code {response.status_code}")
    print(response.text)
    exit(1)

data = response.json()

validated_data = ParsedArticleList.model_validate(data)

date = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
save_model(validated_data, get_project_path(f"Storage/{date}.txt"))