from pydantic_settings import BaseSettings
from functools import lru_cache
import os


class Settings(BaseSettings):
    """应用配置，从 .env 文件读取"""

    # 阿里云百炼 DashScope 配置
    DASHSCOPE_API_KEY: str = "sk-xxxxx"
    LLM_MODEL_NAME: str = "qwen3-max"
    LLM_BASE_URL: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    LLM_TEMPERATURE: float = 0.7

    # MySQL 默认连接（可通过 .env 覆盖）
    MYSQL_HOST: str = "localhost"
    MYSQL_PORT: int = 3306
    MYSQL_USER: str = "root"
    MYSQL_PASSWORD: str = ""
    MYSQL_DATABASE: str = ""

    # 连接配置持久化路径
    CONNECTIONS_FILE: str = "./data/connections.json"

    model_config = {
        "env_file": os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"),
        "env_file_encoding": "utf-8",
    }


@lru_cache()
def get_settings() -> Settings:
    """获取配置单例"""
    return Settings()
