import os

from langchain_groq import ChatGroq


def get_groq_llm():
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError("GROQ_API_KEY is required for LLM endpoints")
    return ChatGroq(
        api_key=api_key,
        model=os.environ.get("GROQ_MODEL", "deepseek-r1-distill-llama-70b"),
        temperature=0,
        max_tokens=None,
        reasoning_format="parsed",
        timeout=None,
        max_retries=2,
    )

