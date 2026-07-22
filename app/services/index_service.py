from app.services.code_chunker import preview_code_chunks
from app.services.embedding_service import create_embedding
from app.services.vector_store import recreate_collection, upsert_chunks


def index_repository_files(
    repo_path: str,
    file_paths: list[str],
    chunk_size: int,
) -> dict:
    all_chunks = []

    for file_path in file_paths:
        chunks = preview_code_chunks(
            repo_path=repo_path,
            file_path=file_path,
            chunk_size=chunk_size,
        )

        all_chunks.extend(chunks)

    embeddings = [
        create_embedding(chunk.content)
        for chunk in all_chunks
    ]

    recreate_collection()

    indexed_count = upsert_chunks(
        chunks=all_chunks,
        embeddings=embeddings,
    )

    return {
        "repo_path": repo_path,
        "file_paths": file_paths,
        "chunk_size": chunk_size,
        "file_count": len(file_paths),
        "chunk_count": len(all_chunks),
        "indexed_count": indexed_count,
    }