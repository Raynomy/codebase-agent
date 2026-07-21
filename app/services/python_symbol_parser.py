import ast
from pathlib import Path


def parse_python_symbols(file_path: str) -> list[dict]:
    path = Path(file_path)
    source_code = path.read_text(encoding="utf-8")

    tree = ast.parse(source_code)

    symbols = []

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            start_line = node.lineno

            if node.decorator_list:
                start_line = min(decorator.lineno for decorator in node.decorator_list)

            symbols.append(
                {
                    "symbol_name": node.name,
                    "symbol_type": "function",
                    "start_line": start_line,
                    "end_line": node.end_lineno,
                }
            )

        if isinstance(node, ast.ClassDef):
            start_line = node.lineno

            if node.decorator_list:
                start_line = min(decorator.lineno for decorator in node.decorator_list)

            symbols.append(
                {
                    "symbol_name": node.name,
                    "symbol_type": "class",
                    "start_line": start_line,
                    "end_line": node.end_lineno,
                }
            )

    return symbols
