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


settings = Settings()