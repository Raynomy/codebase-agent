from fastapi import FastAPI, HTTPException

from app.schemas import (
    RepositoryFilesResponse,
    RepositoryScanRequest,
    RepositoryScanResponse,
)
from app.services.repository_scanner import scan_repository

app = FastAPI(
    title="Codebase Agent",
    version="0.1.0",
)


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post("/repositories/scan", response_model=RepositoryScanResponse)
def scan_repository_api(request: RepositoryScanRequest):
    try:
        files = scan_repository(request.repo_path)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return RepositoryScanResponse(
        repo_path=request.repo_path,
        file_count=len(files),
        files=files,
    )


@app.get("/repositories/files", response_model=RepositoryFilesResponse)
def list_repository_files(repo_path: str):
    try:
        files = scan_repository(repo_path)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return RepositoryFilesResponse(
        repo_path=repo_path,
        files=files,
    )
