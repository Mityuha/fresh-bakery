
<p align="center">
  <a href="https://fresh-bakery.readthedocs.io/en/latest/"><img width="300px" src="https://user-images.githubusercontent.com/17745407/187294435-a3bc6b26-b7df-43e5-abd3-0d7a7f92b71e.png" alt='fresh-bakery'></a>
</p>
<p align="center">
    <em>🍰 The little DI framework that tastes like a cake. 🍰</em>
</p>

---

**Documentation**: [https://fresh-bakery.readthedocs.io/en/latest/](https://fresh-bakery.readthedocs.io/en/latest/)

---

# Fresh Bakery

Fresh bakery is a lightweight [Dependency Injection][DI] framework/toolkit,
which is ideal for building object dependencies in Python.

It is [nearly] production-ready, and gives you the following:

* A lightweight, stupidly simple DI framework.
* Fully asynchronous, no synchronous mode.
* Any async backends compatible (`asyncio`, `trio`).
* Zero dependencies.
* `Mypy` compatible (no probably need for `# type: ignore`).
* `FastAPI` fully compatible.
* `Pytest` fully compatible (Fresh Bakery encourages the use of `pytest`).
* Ease of testing.
* Easily extended (contribution is welcome).

## Requirements

Python 3.6+

## Installation

```shell
$ pip3 install fresh-bakery
```

## Examples

### Raw example
In this example, you can see how to create a specific IoC container using the fresh bakery library in plain python code 
```python
import asyncio

from dataclasses import dataclass
from bakery import Bakery, Cake


# your dependecies
@dataclass
class Settings:
    database_dsn: str
    info_id_list: list[int]


class Database:
    def __init__(self, dsn: str):
        self.dsn: str = dsn

    async def fetch_info(self, info_id: int) -> dict:
        return {"dsn": self.dsn, "info_id": info_id}


class InfoManager:
    def __init__(self, database: Database):
        self.database: Database = database

    async def fetch_full_info(self, info_id: int) -> dict:
        info: dict = await self.database.fetch_info(info_id)
        info["full"] = True
        return info


# specific ioc container, all magic happens here
class MyBakeryIOC(Bakery):
    settings: Settings = Cake(Settings, database_dsn="my_dsn", info_id_list=[1,2,3])
    database: Database = Cake(Database, dsn=settings.database_dsn)
    manager: InfoManager = Cake(InfoManager, database=database)


# code in your application that needs those dependencies ↑
async def main() -> None:
    async with MyBakery() as bakery:
        for info_id in bakery.settings.info_id_list:
            info: dict = await bakery.manager.fetch_full_info(info_id)
            assert info["dsn"] == bakery.settings.database_dsn
            assert info["info_id"] == info_id
            assert info["full"]


# just a piece of service code
if __name__ == "__main__":
    asyncio.run(main())
```

### FastAPI example
This is a full-fledged complex example of how you can use IoC with your FastAPI application:
```python
import typing

import bakery
import fastapi
import pydantic
from loguru import logger
from databases import Database
from databases.interfaces import Record


# This is your dependencies (example)
class ServiceDatabase:
    """Service database."""

    def __init__(self, connection: Database) -> None:
        self._connection: Database = connection

    async def __aenter__(self) -> "ServiceDatabase":
        """On startup."""
        await self._connection.connect()
        return self

    async def __aexit__(self, *_args: typing.Any) -> None:
        """On shutdown."""
        await self._connection.disconnect()

    async def fetch_person(self, person_id: int) -> typing.Mapping:
        """Fetch tenant table data by tenant name."""
        query: str = """
        SELECT *
        FROM person p
        WHERE p.id=:person_id;"""
        values: dict[str, int] = dict(person_id=person_id)
        logger.debug(f"Get person by id {query = }, {values = }")
        row: typing.Optional[Record] = await self._connection.fetch_one(
            query=query,
            values=values,
        )
        return row if row else {}  # type: ignore

    async def insert_person(self, first_name: str, second_name: str, age: int) -> int:
        """Insert person."""
        query: str = """
        INSERT INTO person(first_name, second_name, age)
        VALUES (:first_name, :second_name, :age)
        RETURNING id"""

        values: dict = dict(
            first_name=first_name,
            second_name=second_name,
            age=age,
        )
        logger.debug(f"Insert into person table {query = }, {values = }")
        return await self._connection.fetch_val(query=query, values=values)


class Settings(pydantic.BaseSettings):
    """Service settings."""

    postgres_dsn: pydantic.PostgresDsn = pydantic.Field(
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


class DatabaseInterface(typing.Protocol):
    """Database interface."""

    async def fetch_person(self, person_id: int) -> typing.Mapping:
        """Fetch person."""

    async def insert_person(self, first_name: str, second_name: str, age: int) -> int:
        """Insert person."""


class PersonIn(pydantic.BaseModel):
    """Person in."""

    first_name: str
    second_name: str
    age: int


class PersonOut(PersonIn):
    """Person out."""

    person_id: int


class ServiceController:
    """Service controller."""

    def __init__(
        self,
        *,
        database: DatabaseInterface,
        logger_name: str,
    ):
        """Init."""

        self._database = database
        self._logger_name = logger_name

    def __repr__(self) -> str:
        return self._logger_name

    async def insert_person(self, person: PersonIn, /) -> int:
        """Insert person.

        return id.
        """
        logger.debug(f"{self}: inserting person {person}")
        person_id: int = await self._database.insert_person(
            first_name=person.first_name,
            second_name=person.second_name,
            age=person.age,
        )
        logger.debug(f"{self}: person successfully inserted with id {person_id}")
        return person_id

    async def fetch_person(self, person_id: int, /) -> typing.Optional[PersonOut]:
        """Fetch person by id."""
        logger.debug(f"{self}: fetching person by id {person_id}")
        person: typing.Optional[typing.Mapping] = await self._database.fetch_person(person_id)
        if not person:
            logger.info(f"{self}: person {person_id} not found.")
            return None
        res: PersonOut = PersonOut(
            first_name=person["first_name"],
            second_name=person["second_name"],
            age=person["age"],
            person_id=person["id"],
        )
        logger.info(f"{self}: person {person_id} found: {res}")
        return res


def get_settings() -> Settings:
    """Get settings."""
    settings: Settings = Settings()
    logger.debug(f"Settings: {settings}")
    return settings


# Here is your specific IoC container
class MainBakeryIOC(bakery.Bakery):
    """Main bakery."""

    config: Settings = bakery.Cake(get_settings)
    _connection: Database = bakery.Cake(
        Database,
        config.postgres_dsn,
        min_size=config.postgres_pool_min_size,
        max_size=config.postgres_pool_max_size,
    )
    database: ServiceDatabase = bakery.Cake(
        bakery.Cake(
            ServiceDatabase,
            connection=_connection,
        )
    )
    controller: ServiceController = bakery.Cake(
        ServiceController,
        database=database,
        logger_name=config.controller_logger_name,
    )


async def startup() -> None:
    logger.info("Init resources...")
    bakery.logger = logger
    await MainBakeryIOC.aopen()


async def shutdown() -> None:
    logger.info("Shutdown resources...")
    await MainBakeryIOC.aclose()


MY_APP: fastapi.FastAPI = fastapi.FastAPI(
    on_startup=[startup],
    on_shutdown=[shutdown],
)


# And, finally, an example of how you can use your dependencies
@MY_APP.post(
    '/person',
    response_model=typing.TypedDict("PersonId", {"person_id": int}),
    status_code=201
)
async def create_person(
    request: PersonIn,
    controller: ServiceController = fastapi.Depends(MainBakeryIOC.controller),
) -> dict:
    person_id: int = await controller.insert_person(request)
    return {"person_id": person_id}
```

For a more complete example, see [bakery examples](https://github.com/Mityuha/fresh-bakery/tree/main/examples).

## Dependencies

No dependencies ;)

## Changelog
You can see the release history here: https://github.com/Mityuha/fresh-bakery/releases/

---

<p align="center"><i>Fresh Bakery is <a href="https://github.com/Mityuha/fresh-bakery/blob/main/LICENSE">MIT licensed</a> code.</p>
