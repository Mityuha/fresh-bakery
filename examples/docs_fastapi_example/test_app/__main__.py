from __future__ import annotations

import asyncio
import random
from contextlib import asynccontextmanager
from typing import Any, AsyncIterator, Final, Literal, Mapping

from fastapi import Depends, FastAPI
from loguru import logger
from pydantic import BaseModel, Field, PostgresDsn
from pydantic_settings import BaseSettings
from typing_extensions import Annotated, Self

import bakery
from bakery import Bakery, Cake

# ruff: noqa: S311


# The following is a long and boring list of dependencies
class PersonOut(BaseModel):
    """Person out."""

    first_name: str
    second_name: str
    age: int
    person_id: int


class FakeDbConnection:
    """Fake db connection."""

    def __init__(self, *_: Any, **__: Any) -> None: ...


class DatabaseFakeService:
    """Fake database layer."""

    def __init__(self, connection: FakeDbConnection) -> None:
        # wannabe connection only for test purposes
        self._connection: Final = connection

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(self, *_args: object) -> None:
        await asyncio.sleep(0)

    async def fetch_person(
        self, person_id: int
    ) -> dict[Literal["first_name", "second_name", "age", "id"], str | int]:
        """Fetch (fictitious) person."""
        return {
            "first_name": random.choice(("John", "Danku", "Ichigo", "Sakura", "Jugem", "Ittō")),
            "second_name": random.choice(
                ("Dow", "Kurosaki", "Amaterasu", "Kasō", "HiryuGekizokuShintenRaiho")
            ),
            "age": random.randint(18, 120),
            "id": person_id,
        }


class Settings(BaseSettings):
    """Service settings."""

    postgres_dsn: PostgresDsn = Field(
        default="postgresql://bakery_tester:bakery_tester@0.0.0.0:5432/bakery_tester"
    )
    postgres_pool_min_size: int = 5
    postgres_pool_max_size: int = 20
    controller_logger_name: str = "[Controller]"


class ServiceController:
    """Service controller."""

    def __init__(
        self,
        *,
        database: DatabaseFakeService,
        logger_name: str,
    ) -> None:
        self._database = database
        self._logger_name = logger_name

    def __repr__(self) -> str:
        return self._logger_name

    async def fetch_person(self, person_id: int, /) -> PersonOut | None:
        """Fetch person by id."""
        person: Mapping | None = await self._database.fetch_person(person_id)
        if not person:
            return None
        res: PersonOut = PersonOut(
            first_name=person["first_name"],
            second_name=person["second_name"],
            age=person["age"],
            person_id=person_id,
        )
        return res


def get_settings() -> Settings:
    """Get settings."""
    return Settings()


# Here is your specific IoC container
class MainBakeryIOC(Bakery):
    """Main bakery."""

    config: Settings = Cake(get_settings)
    _connection: FakeDbConnection = Cake(
        FakeDbConnection,
        config.postgres_dsn,
        min_size=config.postgres_pool_min_size,
        max_size=config.postgres_pool_max_size,
    )
    database: DatabaseFakeService = Cake(
        Cake(
            DatabaseFakeService,
            connection=_connection,
        )
    )
    controller: ServiceController = Cake(
        ServiceController,
        database=database,
        logger_name=config.controller_logger_name,
    )


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    logger.info("Init resources...")
    bakery.logger = logger
    async with MainBakeryIOC():
        yield
    logger.info("Shutdown resources...")


MY_APP: Final = FastAPI(lifespan=lifespan)


# Finally, an example of how you can use your dependencies
@MY_APP.get("/person/random/")
async def create_person(
    inversed_controller: Annotated[ServiceController, Depends(MainBakeryIOC.controller)],
) -> PersonOut | None:
    """Fetch random person from the «database»."""
    person_id: int = random.randint(10**1, 10**6)
    return await inversed_controller.fetch_person(person_id)
