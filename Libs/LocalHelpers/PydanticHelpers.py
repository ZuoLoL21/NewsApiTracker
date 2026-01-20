import json
from pathlib import Path
from typing import TypeVar

from pydantic import BaseModel


def save_model(model: BaseModel, file_path: str | Path) -> None:
    """Save a Pydantic model to a JSON file.

    Creates parent directories if they don't exist. The model is serialized
    with 2-space indentation for readability.

    Args:
        model: The Pydantic model instance to save.
        file_path: The destination file path (as string or Path object).
    """
    path = Path(file_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(model.model_dump_json(indent=2), encoding="utf-8")

T = TypeVar("T", bound=BaseModel)


def load_model(model_class: type[T], file_path: str | Path) -> T:
    """Load a Pydantic model from a JSON file.

    Args:
        model_class: The Pydantic model class to instantiate.
        file_path: The source file path (as string or Path object).

    Returns:
        An instance of model_class populated with data from the file.

    Raises:
        FileNotFoundError: If the file does not exist.
        ValidationError: If the JSON data doesn't match the model schema.
    """
    path = Path(file_path)
    data = json.loads(path.read_text(encoding="utf-8"))
    return model_class.model_validate(data)

