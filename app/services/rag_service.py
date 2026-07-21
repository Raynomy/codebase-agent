import os

from dotenv import load_dotenv
from openai import OpenAI, OpenAIError

from app.services.embedding_service import create_embedding
from app.services.vector_store import search_chunks


load_dotenv()

client = OpenAI(
    api_key=os.getenv("AIHUBMIX_API_KEY"),
    base_url=os.getenv("AIHUBMIX_BASE_URL"),
)

CHAT_MODEL = os.getenv("AIHUBMIX_MODEL", "deepseek-v4-flash")


def build_context(search_results: list[dict]) -> str:
    context_parts = []

    for index, result in enumerate(search_results, start=1):
        payload = result["payload"]

        symbol_name = payload.get("symbol_name")
        chunk_type = payload.get("chunk_type")

        if symbol_name:
            symbol_text = f"{chunk_type} {symbol_name}"
        else:
            symbol_text = chunk_type or "unknown"

        context_parts.append(
            f"""资料 {index}
        文件：{payload["file_path"]}
        位置：{symbol_text}
        行号：{payload["start_line"]}-{payload["end_line"]}
        内容：
        {payload["content"]}
        """
        )

    return "\n".join(context_parts)


def build_grounding_prompt(question: str, context: str) -> str:
    return f"""
你是一个代码仓库理解助手。

请严格基于下面提供的代码仓库资料回答问题。

要求：
1. 只能使用资料中的信息回答
2. 如果资料不足，请明确说“我没有在已索引的代码资料中找到相关内容”
3. 不要编造资料中没有出现的文件、函数、类或实现细节
4. 回答要简洁清晰

代码仓库资料：
{context}

用户问题：
{question}
"""


def ask_codebase(
    question: str,
    top_k: int,
    score_threshold: float,
) -> dict:
    query_embedding = create_embedding(question)

    search_results = search_chunks(
        query_embedding=query_embedding,
        top_k=top_k,
        score_threshold=score_threshold,
    )

    if not search_results:
        return {
            "answer": "我没有在已索引的代码资料中找到相关内容。",
            "sources": [],
        }

    context = build_context(search_results)
    prompt = build_grounding_prompt(question=question, context=context)

    try:
        response = client.chat.completions.create(
            model=CHAT_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": "你是一个严谨的代码仓库理解助手。",
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
            temperature=0.2,
        )
    except OpenAIError as exc:
        raise RuntimeError("Failed to generate answer") from exc

    answer = response.choices[0].message.content

    sources = []
    for result in search_results:
        payload = result["payload"]

        sources.append(
            {
                "file_path": payload["file_path"],
                "start_line": payload["start_line"],
                "end_line": payload["end_line"],
                "score": result["score"],
                "content": payload["content"],
                "chunk_type": payload["chunk_type"],
                "symbol_name": payload.get("symbol_name"),
            }
        )

    return {
        "answer": answer,
        "sources": sources,
    }