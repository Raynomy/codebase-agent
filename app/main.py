from fastapi import FastAPI

from app.schemas import (
    RepositoryFilesResponse,
    RepositoryScanRequest,
    RepositoryScanResponse,
)

app = FastAPI(
    title="Codebase Agent",
    version="0.1.0",
)


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post("/repositories/scan", response_model=RepositoryScanResponse)
def scan_repository(request: RepositoryScanRequest):
    return RepositoryScanResponse(
        repo_path=request.repo_path,
        file_count=0,
    )


@app.get("/repositories/files", response_model=RepositoryFilesResponse)
def list_repository_files(repo_path: str):
    return RepositoryFilesResponse(
        repo_path=repo_path,
        files=[],
    )