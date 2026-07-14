from app.services.code_chunker import chunk_by_fixed_lines, split_markdown_by_headings


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