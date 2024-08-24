from dataclasses import dataclass

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
