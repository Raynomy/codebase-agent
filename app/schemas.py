from pydantic import BaseModel, Field


class RepositoryScanRequest(BaseModel):
    repo_path: str = Field(min_length=1)


class RepositoryFile(BaseModel):
    path: str
    file_type: str
    size: int


class RepositoryScanResponse(BaseModel):
    repo_path: str
    file_count: int
    files: list[RepositoryFile]


class RepositoryFilesResponse(BaseModel):
    repo_path: str
    files: list[RepositoryFile]


class CodeFileRequest(BaseModel):
    repo_path: str = Field(min_length=1)
    file_path: str = Field(min_length=1)


class CodeLine(BaseModel):
    line_number: int
    content: str


class CodeFile(BaseModel):
    repo_path: str
    file_path: str
    file_type: str
    line_count: int
    lines: list[CodeLine]


class CodeChunk(BaseModel):
    file_path: str
    file_type: str
    start_line: int
    end_line: int
    chunk_type: str
    content: str