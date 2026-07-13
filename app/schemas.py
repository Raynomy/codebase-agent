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
