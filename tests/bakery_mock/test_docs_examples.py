"""Test docs examples."""

from dataclasses import dataclass

import pytest

from bakery import Bakery, BakingMethod, Cake, hand_made
from bakery.testbakery import BakeryMock


@dataclass
class Settings:
    dsn: str


class MyBakery(Bakery):
    dsn: str = Cake("real dsn")
    settings: Settings = Cake(Settings, dsn=dsn)


async def test_example_1(bakery_mock: BakeryMock) -> None:
    bakery_mock.dsn = Cake("fake dsn")  # <<< patch dsn
    async with bakery_mock(MyBakery):  # <<< mock against MyBakery
        assert MyBakery().dsn == "fake dsn"
        assert MyBakery().settings.dsn == "fake dsn"


async def test_example_1_no_mock() -> None:
    async with MyBakery(dsn="fake dsn"):  # <<< pass new dsn
        assert MyBakery().dsn == "fake dsn"
        assert MyBakery().settings.dsn == "fake dsn"


async def test_example_1_cant_pass_after_open() -> None:
    await MyBakery.aopen()

    with pytest.raises(TypeError):
        async with MyBakery(dsn="fake dsn"):  # <<< passing new arguments after open is prohibited
            ...

    await MyBakery.aclose()


async def test_example_2(bakery_mock: BakeryMock) -> None:
    await MyBakery.aopen()  # open bakery anywhere

    bakery_mock.dsn = Cake("fake dsn")
    async with bakery_mock(MyBakery):
        assert MyBakery().dsn == "fake dsn"  # patched
        assert MyBakery().settings.dsn == "real dsn"  # not patched

    await MyBakery.aclose()  # closed anywhere


async def test_example_3(bakery_mock: BakeryMock) -> None:
    bakery_mock.settings = hand_made(
        Cake(list),
        cake_baking_method=BakingMethod.BAKE_NO_BAKE,
    )
    async with bakery_mock(MyBakery):
        assert MyBakery().settings is list


async def test_example_3_no_mock() -> None:
    async with MyBakery(
        settings=hand_made(  # type: ignore[arg-type]
            Cake(list),
            cake_baking_method=BakingMethod.BAKE_NO_BAKE,
        )
    ):
        assert MyBakery().settings is list
