from app.schemas import CodeChunk
from app.services.code_reader import read_code_file


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
        return chunk_by_fixed_lines(
            file_path=code_file.file_path,
            file_type=code_file.file_type,
            lines=[line.content for line in code_file.lines],
            chunk_size=chunk_size,
            chunk_type="python_lines",
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


def build_chunk(
    file_path: str,
    file_type: str,
    start_line: int,
    lines: list[str],
    chunk_type: str,
) -> CodeChunk:
    return CodeChunk(
        file_path=file_path,
        file_type=file_type,
        start_line=start_line,
        end_line=start_line + len(lines) - 1,
        chunk_type=chunk_type,
        content="\n".join(lines),
    )
