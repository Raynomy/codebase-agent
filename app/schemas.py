from pydantic import BaseModel, Field


class RepositoryScanRequest(BaseModel):
    repo_path: str = Field(min_length=1)


class RepositoryScanResponse(BaseModel):
    repo_path: str
    file_count: int


class RepositoryFilesResponse(BaseModel):
    repo_path: str
    files: list[str]