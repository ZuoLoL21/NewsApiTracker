import logging

from libs.models import ParsedArticleList
from libs.local_helpers.path_helpers import get_project_path
from libs.local_helpers.pydantic_helpers import load_model

# Enable logging to see what's happening during fetching
# Change level to logging.DEBUG for more verbose output
logging.basicConfig(level=logging.INFO, format="%(levelname)s - %(name)s - %(message)s")

TMP_NAME = "2026-01-19_21-14-29.txt"

model: ParsedArticleList = load_model(ParsedArticleList, get_project_path(f"Storage/{TMP_NAME}"))

for article in model.articles:
    break
