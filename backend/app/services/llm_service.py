"""
LLM 服务层 - Qwen3-max via DashScope OpenAI 兼容端点
基于 playground/test_qwen3.py 实测验证
"""

from langchain_openai import ChatOpenAI
from app.config import get_settings


def get_llm(streaming: bool = False) -> ChatOpenAI:
    """
    获取 Qwen3-max LLM 实例

    Args:
        streaming: 是否启用流式输出

    Returns:
        ChatOpenAI 实例，已配置 DashScope 兼容端点
    """
    settings = get_settings()
    return ChatOpenAI(
        model=settings.LLM_MODEL_NAME,
        api_key=settings.DASHSCOPE_API_KEY,
        base_url=settings.LLM_BASE_URL,
        streaming=streaming,
        temperature=settings.LLM_TEMPERATURE,
    )
