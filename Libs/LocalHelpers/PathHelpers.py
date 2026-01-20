from pathlib import Path

def get_project_root() -> Path:
    current = Path(__file__).resolve().parent
    while current != current.parent:
        if (current / ".git").exists():
            return current
        current = current.parent
    raise FileNotFoundError("Could not find project root (no .git directory found)")


def get_project_path(relative_path: str) -> Path:
    root = get_project_root()
    clean_path = relative_path.lstrip("/\\")
    return root / clean_path
