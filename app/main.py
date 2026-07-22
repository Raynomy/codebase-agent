from fastapi import FastAPI, HTTPException

from app.schemas import (
    AskRequest,
    AskResponse,
    ChunkPreviewRequest,
    ChunkPreviewResponse,
    CodeFile,
    CodeFileRequest,
    RepositoryFilesResponse,
    RepositoryIndexRequest,
    RepositoryIndexResponse,
    RepositoryScanRequest,
    RepositoryScanResponse,
)
from app.services.code_chunker import preview_code_chunks
from app.services.code_reader import read_code_file
from app.services.index_service import index_repository_files
from app.services.repository_scanner import scan_repository
from app.services.rag_service import ask_codebase

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


@app.post("/repositories/index", response_model=RepositoryIndexResponse)
def index_repository(request: RepositoryIndexRequest):
    try:
        result = index_repository_files(
            repo_path=request.repo_path,
            file_paths=request.file_paths,
            chunk_size=request.chunk_size,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    return RepositoryIndexResponse(**result)



@app.post("/repositories/ask", response_model=AskResponse)
def ask_repository(request: AskRequest):
    try:
        result = ask_codebase(
            question=request.question,
            top_k=request.top_k,
            score_threshold=request.score_threshold,
        )
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    return AskResponse(
        question=request.question,
        answer=result["answer"],
        sources=result["sources"],
    )
