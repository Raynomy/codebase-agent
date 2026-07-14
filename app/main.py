from fastapi import FastAPI, HTTPException

from app.schemas import (
    ChunkPreviewRequest,
    ChunkPreviewResponse,
    CodeFile,
    CodeFileRequest,
    RepositoryFilesResponse,
    RepositoryScanRequest,
    RepositoryScanResponse,
)
from app.services.code_chunker import preview_code_chunks
from app.services.code_reader import read_code_file
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


@app.post("/code/files/read", response_model=CodeFile)
def read_code_file_api(request: CodeFileRequest):
    try:
        return read_code_file(
            repo_path=request.repo_path,
            file_path=request.file_path,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

@app.post("/repositories/chunks/preview", response_model=ChunkPreviewResponse)
def preview_repository_chunks(request: ChunkPreviewRequest):
    try:
        chunks = preview_code_chunks(
            repo_path=request.repo_path,
            file_path=request.file_path,
            chunk_size=request.chunk_size,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return ChunkPreviewResponse(
        repo_path=request.repo_path,
        file_path=request.file_path,
        chunk_size=request.chunk_size,
        chunk_count=len(chunks),
        chunks=chunks,
    )