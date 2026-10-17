import os

from dotenv import load_dotenv


load_dotenv()


class Settings:
    ENVIRONMENT: str = os.getenv(
        "ENVIRONMENT",
        "development",
    )

    OPENAI_API_KEY: str | None = os.getenv(
        "OPENAI_API_KEY",
    )

    OPENAI_MODEL: str | None = os.getenv(
        "OPENAI_MODEL",
    )

    SECURITY_LIVE_TESTS_ENABLED: bool = os.getenv(
        "SECURITY_LIVE_TESTS_ENABLED", "false"
    ).strip().lower() in {"true", "1", "yes"}
    SECURITY_LIVE_ALLOWED_HOSTS: tuple[str, ...] = tuple(
        item.strip()
        for item in os.getenv("SECURITY_LIVE_ALLOWED_HOSTS", "").split(",")
        if item.strip()
    )
    SECURITY_LIVE_ALLOWED_PATHS: tuple[str, ...] = tuple(
        item.strip()
        for item in os.getenv("SECURITY_LIVE_ALLOWED_PATHS", "").split(",")
        if item.strip()
    )
    SECURITY_LIVE_ALLOWED_PORTS: tuple[int, ...] = tuple(
        int(item.strip())
        for item in os.getenv("SECURITY_LIVE_ALLOWED_PORTS", "").split(",")
        if item.strip().isdigit()
    )
    SECURITY_LIVE_ENVIRONMENT: str | None = os.getenv("SECURITY_LIVE_ENVIRONMENT")


settings = Settings()
