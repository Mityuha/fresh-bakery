"""Service main bakery."""


from bakery import Bakery, Cake
from databases import Database
from loguru import logger

from .adapters.db_adapter import ServiceDatabase
from .config import Settings
from .controllers.controller import ServiceController


def get_settings() -> Settings:
    """Get settings."""
    settings: Settings = Settings()
    logger.debug(f"Settings: {settings}")
    return settings


class BackgroundTask:
    """Some background task.

    just for test.
    """

    CALL_COUNT: int = 0

    def __init__(self):
        type(self).CALL_COUNT += 1


class MainBakery(Bakery):
    """Main bakery."""

    config: Settings = Cake(get_settings)

    # Database
    _connection: Database = Cake(
        Database,
        config.postgres_dsn,
        min_size=config.postgres_pool_min_size,
        max_size=config.postgres_pool_max_size,
    )

    database: ServiceDatabase = Cake(
        Cake(
            ServiceDatabase,
            connection=_connection,
        )
    )

    controller: ServiceController = Cake(
        ServiceController,
        database=database,
        logger_name=config.controller_logger_name,
    )

    background_task: BackgroundTask = Cake(BackgroundTask)
