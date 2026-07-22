from app.schemas import CodeChunk
from app.services.code_reader import read_code_file
from app.services.python_symbol_parser import parse_python_symbols


MARKDOWN_TYPES = {"md"}
PYTHON_TYPES = {"py"}


def preview_code_chunks(repo_path: str, file_path: str, chunk_size: int) -> list[CodeChunk]:
    code_file = read_code_file(repo_path=repo_path, file_path=file_path)

    if code_file.file_type in MARKDOWN_TYPES:
        return chunk_markdown_file(
            file_path=code_file.file_path,
            file_type=code_file.file_type,
            lines=[line.content for line in code_file.lines],
            chunk_size=chunk_size,
        )

    if code_file.file_type in PYTHON_TYPES:
        return chunk_python_file_by_symbols(
            file_path=code_file.file_path,
            file_type=code_file.file_type,
            lines=[line.content for line in code_file.lines],
        )

    return chunk_by_fixed_lines(
        file_path=code_file.file_path,
        file_type=code_file.file_type,
        lines=[line.content for line in code_file.lines],
        chunk_size=chunk_size,
        chunk_type="text_lines",
    )


def chunk_markdown_file(
    file_path: str,
    file_type: str,
    lines: list[str],
    chunk_size: int,
) -> list[CodeChunk]:
    heading_chunks = split_markdown_by_headings(lines)
    chunks: list[CodeChunk] = []

    for start_line, section_lines in heading_chunks:
        if len(section_lines) <= chunk_size:
            chunks.append(
                build_chunk(
                    file_path=file_path,
                    file_type=file_type,
                    start_line=start_line,
                    lines=section_lines,
                    chunk_type="markdown_section",
                )
            )
            continue

        chunks.extend(
            chunk_by_fixed_lines(
                file_path=file_path,
                file_type=file_type,
                lines=section_lines,
                chunk_size=chunk_size,
                chunk_type="markdown_lines",
                start_line_offset=start_line,
            )
        )

    return chunks

def chunk_python_file_by_symbols(
    file_path: str,
    file_type: str,
    lines: list[str],
) -> list[CodeChunk]:
    symbols = parse_python_symbols(file_path)

    chunks: list[CodeChunk] = []
    covered_lines: set[int] = set()

    for symbol in symbols:
        start_line = symbol["start_line"]
        end_line = symbol["end_line"]

        symbol_lines = lines[start_line - 1 : end_line]

        chunks.append(
            build_chunk(
                file_path=file_path,
                file_type=file_type,
                start_line=start_line,
                lines=symbol_lines,
                chunk_type=symbol["symbol_type"],
                symbol_name=symbol["symbol_name"],
            )
        )

        covered_lines.update(range(start_line, end_line + 1))

    module_lines = []
    module_start_line = None

    for line_number, line in enumerate(lines, start=1):
        if line_number in covered_lines:
            if module_lines and module_start_line is not None and has_meaningful_content(module_lines):
                chunks.append(
                    build_chunk(
                        file_path=file_path,
                        file_type=file_type,
                        start_line=module_start_line,
                        lines=module_lines,
                        chunk_type="module",
                    )
                )

                module_lines = []
                module_start_line = None

            continue

        if module_start_line is None:
            module_start_line = line_number

        module_lines.append(line)

    if module_lines and module_start_line is not None and has_meaningful_content(module_lines):
        chunks.append(
            build_chunk(
                file_path=file_path,
                file_type=file_type,
                start_line=module_start_line,
                lines=module_lines,
                chunk_type="module",
            )
        )

    chunks.sort(key=lambda chunk: chunk.start_line)

    return chunks


def split_markdown_by_headings(lines: list[str]) -> list[tuple[int, list[str]]]:
    chunks: list[tuple[int, list[str]]] = []
    current_start = 1
    current_lines: list[str] = []

    for index, line in enumerate(lines, start=1):
        is_heading = line.startswith("#")

        if is_heading and current_lines:
            chunks.append((current_start, current_lines))
            current_start = index
            current_lines = []

        current_lines.append(line)

    if current_lines:
        chunks.append((current_start, current_lines))

    return chunks


def chunk_by_fixed_lines(
    file_path: str,
    file_type: str,
    lines: list[str],
    chunk_size: int,
    chunk_type: str,
    start_line_offset: int = 1,
) -> list[CodeChunk]:
    chunks: list[CodeChunk] = []

    for start_index in range(0, len(lines), chunk_size):
        chunk_lines = lines[start_index : start_index + chunk_size]

        if not has_meaningful_content(chunk_lines):
            continue

        start_line = start_line_offset + start_index

        chunks.append(
            build_chunk(
                file_path=file_path,
                file_type=file_type,
                start_line=start_line,
                lines=chunk_lines,
                chunk_type=chunk_type,
            )
        )

    return chunks

def has_meaningful_content(lines: list[str]) -> bool:
    return any(line.strip() for line in lines)


def build_chunk(
    file_path: str,
    file_type: str,
    start_line: int,
    lines: list[str],
    chunk_type: str,
    symbol_name: str | None = None,
) -> CodeChunk:
    return CodeChunk(
        file_path=file_path,
        file_type=file_type,
        start_line=start_line,
        end_line=start_line + len(lines) - 1,
        chunk_type=chunk_type,
        content="\n".join(lines),
        symbol_name=symbol_name,
    )
