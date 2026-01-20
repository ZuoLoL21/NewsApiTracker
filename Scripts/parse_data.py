from Libs.Models import ParsedArticleList
from Libs.LocalHelpers.PathHelpers import get_project_path
from Libs.LocalHelpers.PydanticHelpers import load_model

TMP_NAME = "2026-01-19_21-14-29.txt"

model:ParsedArticleList = load_model(ParsedArticleList, get_project_path(f"Storage/{TMP_NAME}"))

print(model.model_dump_json(indent=4))