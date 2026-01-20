from pathlib import Path


def get_project_root() -> Path:
    """Find and return the project root directory by searching for a .git folder.

    Traverses up from the current file's directory until it finds a directory
    containing a .git folder, which is assumed to be the project root.

    Returns:
        Path: The absolute path to the project root directory.

    Raises:
        FileNotFoundError: If no .git directory is found in any parent directory.
    """
    current = Path(__file__).resolve().parent
    while current != current.parent:
        if (current / ".git").exists():
            return current
        current = current.parent
    raise FileNotFoundError("Could not find project root (no .git directory found)")

def get_project_path(relative_path: str) -> Path:
    """Convert a relative path to an absolute path within the project.

    Args:
        relative_path: A path relative to the project root. Leading slashes
            are automatically stripped.

    Returns:
        Path: The absolute path combining the project root with the relative path.
    """
    root = get_project_root()
    clean_path = relative_path.lstrip("/\\")
    return root / clean_path
