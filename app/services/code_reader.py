from pathlib import Path

from app.schemas import CodeFile, CodeLine


def read_code_file(repo_path: str, file_path: str) -> CodeFile:
    root = Path(repo_path).expanduser().resolve()
    target = (root / file_path).resolve()

    if not root.exists():
        raise ValueError(f"Repository path does not exist: {repo_path}")

    if not root.is_dir():
        raise ValueError(f"Repository path is not a directory: {repo_path}")

    if not is_safe_child_path(root, target):
        raise ValueError(f"File path is outside repository: {file_path}")

    if not target.exists():
        raise ValueError(f"File path does not exist: {file_path}")

    if not target.is_file():
        raise ValueError(f"File path is not a file: {file_path}")

    content = target.read_text(encoding="utf-8")

    raw_lines = content.splitlines()

    lines = [
        CodeLine(
            line_number=index,
            content=line,
        )
        for index, line in enumerate(raw_lines, start=1)
    ]

    return CodeFile(
        repo_path=str(root),
        file_path=str(target.relative_to(root)),
        file_type=get_file_type(target),
        line_count=len(lines),
        lines=lines,
    )


def is_safe_child_path(root: Path, target: Path) -> bool:
    try:
        target.relative_to(root)
    except ValueError:
        return False

    return True


def get_file_type(path: Path) -> str:
    if path.suffix:
        return path.suffix.lstrip(".")

    return "unknown"