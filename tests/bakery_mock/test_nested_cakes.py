"""Test bested cakes."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from typing_extensions import Self

from bakery import Bakery, Cake

if TYPE_CHECKING:
    from bakery.testbakery import BakeryMock


async def test_nested_cakes_mock_simple(bakery_mock: BakeryMock) -> None:
    def make_list(*args: Any) -> list:
        return list(*args)

    class MyBakery(Bakery):
        value: float = Cake(
            sum,
            Cake(
                Cake(
                    make_list,
                    [Cake(sum, [1, 2, 3])],
                ),
            ),
        )

    async with MyBakery() as bakery:
        assert bakery.value == 6

    bakery_mock.value = Cake(10)
    async with bakery_mock(MyBakery):
        assert MyBakery().value == 10

    bakery_mock.value = Cake(sum, Cake(make_list, (1, 2, 3, 4)))
    async with bakery_mock(MyBakery):
        assert MyBakery().value == 10


async def test_nested_cakes_mock_complex(bakery_mock: BakeryMock) -> None:
    class Database:
        def __init__(self, table: str) -> None:
            self.connected: bool = False
            self.table: str = table

        async def __aenter__(self) -> Self:
            self.connected = True
            return self

        async def __aexit__(self, *_args: object) -> None:
            self.connected = False

    class MyBakery(Bakery):
        database: Database = Cake(Cake(Database, table=Cake("table")))

    async with MyBakery() as bakery:
        assert bakery.database.connected

    bakery_mock.database = Cake(None)

    async with bakery_mock(MyBakery):
        assert MyBakery().database is None
