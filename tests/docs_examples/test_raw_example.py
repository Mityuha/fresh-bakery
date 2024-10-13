from __future__ import annotations

import asyncio
from dataclasses import dataclass

from bakery import Bakery, Cake


# your dependecies
@dataclass
class Settings:
    database_dsn: str
    info_id_list: list[int]


class Database:
    def __init__(self, dsn: str) -> None:
        self.dsn: str = dsn

    async def fetch_info(self, info_id: int) -> dict:
        return {"dsn": self.dsn, "info_id": info_id}


class InfoManager:
    def __init__(self, database: Database) -> None:
        self.database: Database = database

    async def fetch_full_info(self, info_id: int) -> dict:
        info: dict = await self.database.fetch_info(info_id)
        info["full"] = True
        return info


# specific ioc container, all magic happens here
class MyBakeryIOC(Bakery):
    settings: Settings = Cake(Settings, database_dsn="my_dsn", info_id_list=[1, 2, 3])
    database: Database = Cake(Database, dsn=settings.database_dsn)
    manager: InfoManager = Cake(InfoManager, database=database)


# code in your application that needs those dependencies ↑
async def test_raw_example() -> None:
    async with MyBakeryIOC() as bakery:
        for info_id in bakery.settings.info_id_list:
            info: dict = await bakery.manager.fetch_full_info(info_id)
            assert info["dsn"] == bakery.settings.database_dsn
            assert info["info_id"] == info_id
            assert info["full"]


if __name__ == "__main__":
    asyncio.run(main())
