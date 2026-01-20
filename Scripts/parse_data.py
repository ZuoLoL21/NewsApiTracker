from Libs.Models import ParsedArticleList
from Libs.PathHelpers import get_project_path
from Libs.PydanticHelpers import load_model

TMP_NAME = "2026-01-19_21-09-33.txt"

model:ParsedArticleList = load_model(ParsedArticleList, get_project_path(f"Storage/{TMP_NAME}"))

print(model.model_dump_json(indent=4))