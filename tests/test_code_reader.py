from pathlib import Path

import pytest

from app.services.code_reader import read_code_file


def test_read_code_file_returns_lines(tmp_path):
    repo = tmp_path / "demo_repo"
    repo.mkdir()

    file_path = repo / "main.py"
    file_path.write_text(
        "print('hello')\nprint('world')\n",
        encoding="utf-8",
    )

    result = read_code_file(
        repo_path=str(repo),
        file_path="main.py",
    )

    assert result.file_path == "main.py"
    assert result.file_type == "py"
    assert result.line_count == 2
    assert result.lines[0].line_number == 1
    assert result.lines[0].content == "print('hello')"
    assert result.lines[1].line_number == 2
    assert result.lines[1].content == "print('world')"


def test_read_code_file_rejects_outside_path(tmp_path):
    repo = tmp_path / "demo_repo"
    repo.mkdir()

    outside_file = tmp_path / "secret.txt"
    outside_file.write_text("secret", encoding="utf-8")

    with pytest.raises(ValueError) as exc_info:
        read_code_file(
            repo_path=str(repo),
            file_path="../secret.txt",
        )

    assert "outside repository" in str(exc_info.value)