
<p align="center">
  <a href="https://fresh-bakery.readthedocs.io/en/latest/"><img width="300px" src="https://user-images.githubusercontent.com/17745407/187294435-a3bc6b26-b7df-43e5-abd3-0d7a7f92b71e.png" alt='fresh-bakery'></a>
</p>
<p align="center">
    <em>🍰 The little DI framework that taste like a cake. 🍰</em>
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
This piece of code shows how to use IoC in conjunction with FastAPI. The specific IoC container itself can be viewed in more [detail here](./examples/bakery_tester2/test_app/bakery.py)
```python
import bakery
from fastapi import FastAPI
from loguru import logger

from bakery import Cakeable
from .bakery import MainBakery
from .controllers.controller import PersonIn, ServiceController
from .views.common import router as common_router


async def startup() -> None:
    logger.info("Init resources...")
    bakery.logger = logger
    await MainBakery.aopen()


async def shutdown() -> None:
    logger.info("Shutdown resources...")
    await MainBakery.aclose()


APP: FastAPI = FastAPI(
    on_startup=[startup],
    on_shutdown=[shutdown],
)


@APP.post(
    '/person',
    response_model=TypedDict("PersonId", {"person_id": int}),
    status_code=201
)
async def create_person(
    request: PersonIn,
    controller: ServiceController = Depends(MainBakery.controller),
) -> Dict:
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
