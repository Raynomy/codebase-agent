import os

from dotenv import load_dotenv
from openai import OpenAI, OpenAIError


load_dotenv()

client = OpenAI(
    api_key=os.getenv("AIHUBMIX_API_KEY"),
    base_url=os.getenv("AIHUBMIX_BASE_URL"),
)

EMBEDDING_MODEL = os.getenv("AIHUBMIX_EMBEDDING_MODEL", "text-embedding-3-small")


def create_embedding(text: str) -> list[float]:
    try:
        response = client.embeddings.create(
            model=EMBEDDING_MODEL,
            input=text,
        )
    except OpenAIError as exc:
        raise RuntimeError("Failed to create embedding") from exc

    return response.data[0].embedding