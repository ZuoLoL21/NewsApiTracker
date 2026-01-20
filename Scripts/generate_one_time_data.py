from dotenv import load_dotenv
import os
import requests
from datetime import date, timedelta

from Libs.Models import Articles

load_dotenv()

API_KEY = os.getenv("NewsAPIKey")
URL = "https://newsapi.org/v2/everything"

QUERY = "Cloud Computing"
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

validated_data = Articles.model_validate(data)

print(validated_data.model_dump_json(indent=4))