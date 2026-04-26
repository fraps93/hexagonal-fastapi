"""Application configuration via pydantic-settings.

Values are read from environment variables (case-insensitive).
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(case_sensitive=False)

    app_name: str = "Hexagonal Fastapi"
    app_version: str = "0.1.0"
    app_description: str = (
        "Demonstrating Hexagonal Architecture, Dependency Injection "
        "(dependency-injector), Pydantic v2, and FastAPI."
    )

    host: str = "0.0.0.0"
    port: int = 8000
    reload: bool = False

    log_level: str = "info"
    debug: bool = False


settings = Settings()
