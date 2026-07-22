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
你是一个严谨的代码仓库问答助手，负责基于已检索到的代码片段回答用户问题。

你的回答必须遵守以下规则：

1. 只能基于“代码仓库资料”中的内容回答。
2. 不要使用资料之外的常识补充代码实现细节。
3. 如果资料中没有足够信息回答问题，请回答：
   “我没有在已索引的代码资料中找到相关内容。”
4. 如果资料只包含部分信息，请明确说明“根据当前资料只能判断...”。
5. 回答中必须尽量引用相关文件路径和行号。
6. 如果资料中包含函数名或类名，请在回答中说明对应的函数或类。
7. 不要编造不存在的文件、函数、类、接口或调用关系。
8. 回答要简洁、清晰，优先说明结论，再说明依据。

回答格式：

结论：
用 1-3 句话直接回答用户问题。

依据：
- 文件：<file_path>
- 行号：<start_line>-<end_line>
- 符号：<function/class/module，如果资料中有>
- 说明：这段资料如何支持上面的结论

如果资料不足，只输出：
我没有在已索引的代码资料中找到相关内容。

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