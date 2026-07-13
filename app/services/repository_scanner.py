from pathlib import Path

from app.schemas import RepositoryFile


IGNORED_DIRS = {
    ".git",
    ".venv",
    "__pycache__",
    ".pytest_cache",
}

IGNORED_FILE_SUFFIXES = {
    ".pyc",
    ".pyo",
    ".DS_Store",
}

TEXT_FILE_SUFFIXES = {
    ".py",
    ".md",
    ".txt",
    ".json",
    ".toml",
    ".yaml",
    ".yml",
    ".env.example",
}


def scan_repository(repo_path: str) -> list[RepositoryFile]:
    root = Path(repo_path).expanduser().resolve()

    if not root.exists():
        raise ValueError(f"Repository path does not exist: {repo_path}")

    if not root.is_dir():
        raise ValueError(f"Repository path is not a directory: {repo_path}")

    files: list[RepositoryFile] = []

    for path in root.rglob("*"):
        if should_ignore_path(path):
            continue

        if not path.is_file():
            continue

        if not is_supported_text_file(path):
            continue

        relative_path = path.relative_to(root)

        files.append(
            RepositoryFile(
                path=str(relative_path),
                file_type=get_file_type(path),
                size=path.stat().st_size,
            )
        )

    return files


def should_ignore_path(path: Path) -> bool:
    return any(part in IGNORED_DIRS for part in path.parts)


def is_supported_text_file(path: Path) -> bool:
    if path.name in IGNORED_FILE_SUFFIXES:
        return False

    if path.suffix in TEXT_FILE_SUFFIXES:
        return True

    if path.name == ".env.example":
        return True

    return False


def get_file_type(path: Path) -> str:
    if path.suffix:
        return path.suffix.lstrip(".")

    return "unknown"