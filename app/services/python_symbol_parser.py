import ast
from pathlib import Path


def parse_python_symbols(file_path: str) -> list[dict]:
    path = Path(file_path)
    source_code = path.read_text(encoding="utf-8")

    tree = ast.parse(source_code)

    symbols = []

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            symbols.append(
                {
                    "symbol_name": node.name,
                    "symbol_type": "function",
                    "start_line": node.lineno,
                    "end_line": node.end_lineno,
                }
            )

        if isinstance(node, ast.ClassDef):
            symbols.append(
                {
                    "symbol_name": node.name,
                    "symbol_type": "class",
                    "start_line": node.lineno,
                    "end_line": node.end_lineno,
                }
            )

    return symbols