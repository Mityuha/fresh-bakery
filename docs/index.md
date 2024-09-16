# Fresh Bakery
Fresh Bakery is a lightweight [Dependency Injection](dependency_injection.md) framework. 

Actually, the only two asyncronious things about Fresh Bakery are its opening and its closing.
It doesn't add up how you open and close your bakery: just make it asynchronously. That's it.

Fresh Bakery is suitable for integrating against any async Web framework, such as [Starlette][starlette], [aiohttp][aiohttp], [FastAPI][fastapi], [Litestar][litestar] and so forth.

**Requirements**: Python 3.8+

---

## Installation

```shell
$ pip install fresh-bakery
```

---

## Quickstart


```shell
$ pip install fresh-bakery
```

For this example we'll define some simple classes:   

* Settings class with `database_dsn` and `info_id_list` fields  
* Database class that performs `fetch_info` query  
* InfoManager class that performs `fetch_info` query and enrich result with some extra data.  

After that we'll define `MyBakery` class, that inherited from library `Bakery` class.

Thereafter within main function we open up `MyBakery` and within context assert some statements.


```python
import asyncio
from dataclasses import dataclass
from bakery import Bakery, Cake


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


class MyBakery(Bakery):
    settings: Settings = Cake(Settings, database_dsn="my_dsn", info_id_list=[1, 2, 3])
    database: Database = Cake(Database, dsn=settings.database_dsn)
    manager: InfoManager = Cake(InfoManager, database=database)


async def main() -> None:
    async with MyBakery() as bakery:
        for info_id in bakery.settings.info_id_list:
            info: dict = await bakery.manager.fetch_full_info(info_id)
            assert info["dsn"] == bakery.settings.database_dsn
            assert info["info_id"] == info_id
            assert info["full"]


if __name__ == "__main__":
    asyncio.run(main())
```

Note that you can also open and close `MyBakery` directly.

```python
async def main() -> None:
    bakery: MyBakery = await MyBakery.aopen()
    # some statements here
    await MyBakery.aclose()
```

You can also get cake's value directly from `MyBakery` class (not instance) by calling corresponding cake or cake attribute.

```python
async def main() -> None:
    async with MyBakery() as bakery:
        dsn1: str = bakery.settings.database_dsn
        dsn2: str = MyBakery.settings().database_dsn
        # or even so
        dsn3: str = MyBakery.settings.database_dsn()
        assert dsn1 == dsn2 == dsn3
```

---

<p align="center"><i>Fresh Bakery is <a href="https://github.com/Mityuha/fresh-bakery/blob/main/LICENSE">MIT licensed</a> code.</p>




[starlette]: https://github.com/encode/starlette
[aiohttp]: https://github.com/aio-libs/aiohttp
[fastapi]: https://github.com/tiangolo/fastapi
[litestar]: https://github.com/litestar-org/litestar
