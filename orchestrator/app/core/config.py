from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings"""

    app_name: str = "Docker Orchestration API"
    app_version: str = "1.0.0"
    debug: bool = False

    # Docker settings
    docker_host: Optional[str] = None
    docker_timeout: int = 30

    # Port management
    port_start: int = 8000
    port_end: int = 9000

    # API settings
    api_host: str = "0.0.0.0"
    api_port: int = 9000

    class Config:
        env_file = ".env"


# Global settings instance
settings = Settings()
