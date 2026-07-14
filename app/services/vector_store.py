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

    for index, (chunk, embedding) in enumerate(zip(chunks, embeddings), start=1):
        points.append(
            PointStruct(
                id=index,
                vector=embedding,
                payload={
                    "file_path": chunk.file_path,
                    "file_type": chunk.file_type,
                    "start_line": chunk.start_line,
                    "end_line": chunk.end_line,
                    "chunk_type": chunk.chunk_type,
                    "content": chunk.content,
                },
            )
        )

    client.upsert(
        collection_name=COLLECTION_NAME,
        points=points,
    )

    return len(points)