
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

## Example

**example.py**:

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
    settings: Settings = Cake(Settings, database_dsn="my_dsn", info_id_list=[1,2,3])
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

For a more complete example, see [bakery examples](https://github.com/Mityuha/fresh-bakery/tree/main/examples).

## Dependencies

No dependencies ;)

---

<p align="center"><i>Fresh Bakery is <a href="https://github.com/Mityuha/fresh-bakery/blob/main/LICENSE">MIT licensed</a> code.</p>
