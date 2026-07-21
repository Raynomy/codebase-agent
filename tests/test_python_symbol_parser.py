from pathlib import Path

from app.services.python_symbol_parser import parse_python_symbols


def test_parse_python_symbols_finds_functions(tmp_path):
    file_path = tmp_path / "sample.py"
    file_path.write_text(
        """
def hello():
    return "hi"


def add(a, b):
    return a + b
""",
        encoding="utf-8",
    )

    symbols = parse_python_symbols(str(file_path))

    assert symbols == [
        {
            "symbol_name": "hello",
            "symbol_type": "function",
            "start_line": 2,
            "end_line": 3,
        },
        {
            "symbol_name": "add",
            "symbol_type": "function",
            "start_line": 6,
            "end_line": 7,
        },
    ]


def test_parse_python_symbols_finds_classes(tmp_path):
    file_path = tmp_path / "sample.py"
    file_path.write_text(
        """
class User:
    pass


class Task:
    pass
""",
        encoding="utf-8",
    )

    symbols = parse_python_symbols(str(file_path))

    assert symbols == [
        {
            "symbol_name": "User",
            "symbol_type": "class",
            "start_line": 2,
            "end_line": 3,
        },
        {
            "symbol_name": "Task",
            "symbol_type": "class",
            "start_line": 6,
            "end_line": 7,
        },
    ]