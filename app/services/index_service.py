from app.services.code_chunker import preview_code_chunks
from app.services.embedding_service import create_embedding
from app.services.vector_store import recreate_collection, upsert_chunks


def index_repository_file(repo_path: str, file_path: str, chunk_size: int) -> dict:
    chunks = preview_code_chunks(
        repo_path=repo_path,
        file_path=file_path,
        chunk_size=chunk_size,
    )

    embeddings = [
        create_embedding(chunk.content)
        for chunk in chunks
    ]

    recreate_collection()

    indexed_count = upsert_chunks(
        chunks=chunks,
        embeddings=embeddings,
    )

    return {
        "repo_path": repo_path,
        "file_path": file_path,
        "chunk_size": chunk_size,
        "chunk_count": len(chunks),
        "indexed_count": indexed_count,
    }