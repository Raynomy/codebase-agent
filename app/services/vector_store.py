from uuid import uuid5, NAMESPACE_URL

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams

from app.schemas import CodeChunk



COLLECTION_NAME = "code_chunks"
VECTOR_SIZE = 1024

client = QdrantClient(":memory:")


def recreate_collection() -> None:
    client.recreate_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(
            size=VECTOR_SIZE,
            distance=Distance.COSINE,
        ),
    )


def upsert_chunks(chunks: list[CodeChunk], embeddings: list[list[float]]) -> int:
    points = []

    for chunk, embedding in zip(chunks, embeddings):
        point_id = str(
            uuid5(
                NAMESPACE_URL,
                f"{chunk.file_path}:{chunk.start_line}:{chunk.end_line}:{chunk.chunk_type}:{chunk.symbol_name}",
            )
        )

        points.append(
            PointStruct(
                id=point_id,
                vector=embedding,
                payload={
                    "file_path": chunk.file_path,
                    "file_type": chunk.file_type,
                    "start_line": chunk.start_line,
                    "end_line": chunk.end_line,
                    "chunk_type": chunk.chunk_type,
                    "symbol_name": chunk.symbol_name,
                    "content": chunk.content,
                },
            )
        )

    client.upsert(
        collection_name=COLLECTION_NAME,
        points=points,
    )

    return len(points)


def search_chunks(
    query_embedding: list[float],
    top_k: int,
    score_threshold: float,
) -> list[dict]:
    response = client.query_points(
        collection_name=COLLECTION_NAME,
        query=query_embedding,
        limit=top_k,
        score_threshold=score_threshold,
    )

    return [
        {
            "score": point.score,
            "payload": point.payload,
        }
        for point in response.points
    ]