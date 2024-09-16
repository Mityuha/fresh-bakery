"""Test mock after open."""

from bakery import Bakery, Cake
from bakery.testbakery import BakeryMock


async def test_mock_after_open(bakery_mock: BakeryMock) -> None:
    class MyPC(Bakery):
        core_num: int = Cake(4)
        manufacturer: str = Cake("Intel")

    bakery_mock.core_num, bakery_mock.manufacturer = Cake(5), Cake("AMD")

    async with MyPC() as my_pc:
        assert my_pc.core_num == 4
        assert MyPC.core_num() == 4
        assert MyPC().core_num == 4
        assert my_pc.manufacturer == "Intel"
        assert MyPC.manufacturer() == "Intel"
        assert MyPC().manufacturer == "Intel"

        async with bakery_mock(MyPC):
            assert my_pc.core_num == 5
            assert MyPC.core_num() == 5
            assert MyPC().core_num == 5
            assert my_pc.manufacturer == "AMD"
            assert MyPC.manufacturer() == "AMD"
            assert MyPC().manufacturer == "AMD"

        assert my_pc.core_num == 4
        assert MyPC.core_num() == 4
        assert MyPC().core_num == 4
        assert my_pc.manufacturer == "Intel"
        assert MyPC.manufacturer() == "Intel"
        assert MyPC().manufacturer == "Intel"
