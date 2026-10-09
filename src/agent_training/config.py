import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


def required_env(name: str) -> str:
    value = os.getenv(name)

    if value is None or not value.strip():
        raise RuntimeError(
            f"Missing required environment variable: {name}"
        )

    return value


@dataclass(frozen=True)
class Settings:
    mysql_host: str
    mysql_port: int
    mysql_user: str
    mysql_password: str
    mysql_database: str
    llm_model: str
    dashscope_api_key: str | None


def get_settings() -> Settings:
    port_str = required_env("MYSQL_PORT")

    try:
        port = int(port_str)
    except ValueError as exc:
        raise RuntimeError(
            "MYSQL_PORT must be an integer"
        ) from exc

    if not 1 <= port <= 65535:
        raise RuntimeError(
            "MYSQL_PORT must be between 1 and 65535"
        )

    return Settings(
        mysql_host=required_env("MYSQL_HOST"),
        mysql_port=port,
        mysql_user=required_env("MYSQL_USER"),
        mysql_password=required_env("MYSQL_PASSWORD"),
        mysql_database=required_env("MYSQL_DATABASE"),
        llm_model=os.getenv("LLM_MODEL", "qwen-plus"),
        dashscope_api_key=(
            os.getenv("DASHSCOPE_API_KEY") or None
        ),
    )