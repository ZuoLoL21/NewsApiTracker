import json
from pathlib import Path
from typing import TypeVar

from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)

def save_model(model: BaseModel, file_path: str | Path) -> None:
    path = Path(file_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(model.model_dump_json(indent=2), encoding="utf-8")


def load_model(model_class: type[T], file_path: str | Path) -> T:
    path = Path(file_path)
    data = json.loads(path.read_text(encoding="utf-8"))
    return model_class.model_validate(data)

