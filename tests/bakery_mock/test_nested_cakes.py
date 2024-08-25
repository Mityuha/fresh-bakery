from typing import Any, List

from bakery import Bakery, Cake
from bakery.testbakery import BakeryMock


async def test_nested_cakes_mock_simple(bakery_mock: BakeryMock) -> None:
    def make_list(*args: Any) -> List:
        return list(*args)

    class MyBakery(Bakery):
        value: float = Cake(
            sum,  # type: ignore
            Cake(
                Cake(
                    make_list,  # type: ignore
                    [Cake(sum, [1, 2, 3])],  # type: ignore
                ),
            ),
        )

    async with MyBakery() as bakery:
        assert bakery.value == 6

    bakery_mock.value = Cake(10)
    async with bakery_mock(MyBakery):
        assert MyBakery().value == 10

    bakery_mock.value = Cake(sum, Cake(make_list, (1, 2, 3, 4)))  # type: ignore
    async with bakery_mock(MyBakery):
        assert MyBakery().value == 10


async def test_nested_cakes_mock_complex(bakery_mock: BakeryMock) -> None:
    class Database:
        def __init__(self, table: str):
            self.connected: bool = False
            self.table: str = table

        async def __aenter__(self) -> "Database":
            self.connected = True
            return self

        async def __aexit__(self, *_args: Any) -> None:
            self.connected = False

    class MyBakery(Bakery):
        database: Database = Cake(Cake(Database, table=Cake("table")))

    async with MyBakery() as bakery:
        assert bakery.database.connected

    bakery_mock.database = Cake(None)

    async with bakery_mock(MyBakery):
        assert MyBakery().database is None
