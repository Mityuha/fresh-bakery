"""Settings."""


from pydantic import BaseSettings, Field, PostgresDsn  # pylint: disable=no-name-in-module


class Settings(BaseSettings):
    """Service settings."""

    postgres_dsn: PostgresDsn = Field(
        default="postgresql://bakery_tester:bakery_tester@0.0.0.0:5432/bakery_tester"
    )
    postgres_pool_min_size: int = 5
    postgres_pool_max_size: int = 20

    controller_logger_name: str = "[Controller]"

    def __str__(self) -> str:
        return (
            f"postgres_pool_min_size: {self.postgres_pool_min_size}, "
            f"postgres_pool_max_size: {self.postgres_pool_max_size}, "
            f"controller_logger_name: {self.controller_logger_name}"
        )
