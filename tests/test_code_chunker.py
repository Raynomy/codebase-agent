from app.services.code_chunker import (
    chunk_by_fixed_lines,
    chunk_python_file_by_symbols,
    split_markdown_by_headings,
)


def test_chunk_by_fixed_lines_keeps_line_range():
    chunks = chunk_by_fixed_lines(
        file_path="app/main.py",
        file_type="py",
        lines=["line1", "line2", "line3", "line4", "line5"],
        chunk_size=2,
        chunk_type="python_lines",
    )

    assert len(chunks) == 3

    assert chunks[0].start_line == 1
    assert chunks[0].end_line == 2
    assert chunks[0].content == "line1\nline2"

    assert chunks[1].start_line == 3
    assert chunks[1].end_line == 4
    assert chunks[1].content == "line3\nline4"

    assert chunks[2].start_line == 5
    assert chunks[2].end_line == 5
    assert chunks[2].content == "line5"


def test_split_markdown_by_headings():
    lines = [
        "# Title",
        "",
        "intro",
        "## Section",
        "content",
    ]

    sections = split_markdown_by_headings(lines)

    assert len(sections) == 2

    assert sections[0][0] == 1
    assert sections[0][1] == [
        "# Title",
        "",
        "intro",
    ]

    assert sections[1][0] == 4
    assert sections[1][1] == [
        "## Section",
        "content",
    ]




def test_chunk_python_file_by_symbols_keeps_functions_as_chunks(tmp_path):
    file_path = tmp_path / "sample.py"
    file_path.write_text(
        "\n".join(
            [
                "import os",
                "",
                "def hello():",
                "    return 'hi'",
                "",
                "def add(a, b):",
                "    return a + b",
            ]
        ),
        encoding="utf-8",
    )

    lines = file_path.read_text(encoding="utf-8").splitlines()

    chunks = chunk_python_file_by_symbols(
        file_path=str(file_path),
        file_type="py",
        lines=lines,
    )

    assert [(chunk.chunk_type, chunk.symbol_name, chunk.start_line, chunk.end_line) for chunk in chunks] == [
        ("module", None, 1, 2),
        ("function", "hello", 3, 4),
        ("function", "add", 6, 7),
    ]


def test_chunk_python_file_by_symbols_keeps_classes_as_chunks(tmp_path):
    file_path = tmp_path / "sample.py"
    file_path.write_text(
        "\n".join(
            [
                "from pydantic import BaseModel",
                "",
                "class User(BaseModel):",
                "    id: int",
                "    name: str",
                "",
                "class Task(BaseModel):",
                "    title: str",
            ]
        ),
        encoding="utf-8",
    )

    lines = file_path.read_text(encoding="utf-8").splitlines()

    chunks = chunk_python_file_by_symbols(
        file_path=str(file_path),
        file_type="py",
        lines=lines,
    )

    assert [(chunk.chunk_type, chunk.symbol_name, chunk.start_line, chunk.end_line) for chunk in chunks] == [
        ("module", None, 1, 2),
        ("class", "User", 3, 5),
        ("class", "Task", 7, 8),
    ]