from bakery import Bakery, Cake
from bakery.testbakery import BakeryMock


async def test_bakery_patch_before_open(bakery_mock: BakeryMock) -> None:
    class MyPC(Bakery):

        core_num: int = Cake(4)
        manufacturer: str = Cake("Intel")

    bakery_mock.core_num = Cake(6)
    bakery_mock.manufacturer = Cake("AMD")

    await bakery_mock.patch(MyPC)

    async with MyPC() as my_pc:
        assert my_pc.core_num == 6
        assert MyPC.core_num() == 6
        assert MyPC().core_num == 6
        assert my_pc.manufacturer == "AMD"
        assert MyPC.manufacturer() == "AMD"
        assert MyPC().manufacturer == "AMD"

    await bakery_mock.reset()

    async with MyPC() as my_pc:
        assert my_pc.core_num == 4
        assert MyPC.core_num() == 4
        assert MyPC().core_num == 4
        assert my_pc.manufacturer == "Intel"
        assert MyPC.manufacturer() == "Intel"
        assert MyPC().manufacturer == "Intel"
