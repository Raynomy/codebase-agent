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
    symbol_name: str | None = None


class ChunkPreviewRequest(BaseModel):
    repo_path: str = Field(min_length=1)
    file_path: str = Field(min_length=1)
    chunk_size: int = Field(default=40, ge=1, le=200)


class ChunkPreviewResponse(BaseModel):
    repo_path: str
    file_path: str
    chunk_size: int
    chunk_count: int
    chunks: list[CodeChunk]


class RepositoryIndexRequest(BaseModel):
    repo_path: str = Field(min_length=1)
    file_path: str = Field(min_length=1)
    chunk_size: int = Field(default=40, ge=1, le=200)


class RepositoryIndexResponse(BaseModel):
    repo_path: str
    file_path: str
    chunk_size: int
    chunk_count: int
    indexed_count: int



class AskRequest(BaseModel):
    question: str = Field(min_length=1)
    top_k: int = Field(default=3, ge=1, le=10)
    score_threshold: float = Field(default=0.5, ge=0, le=1)


class SourceChunk(BaseModel):
    file_path: str
    start_line: int
    end_line: int
    score: float
    content: str


class AskResponse(BaseModel):
    question: str
    answer: str
    sources: list[SourceChunk]