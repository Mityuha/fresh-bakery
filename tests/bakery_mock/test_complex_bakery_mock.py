from dataclasses import dataclass
from typing import Dict, List

from bakery import Bakery, Cake, is_baked
from bakery.testbakery import BakeryMock


async def test_complex_bakery_mock1(bakery_mock: BakeryMock) -> None:
    @dataclass
    class CPU:
        core_num: int
        manufacturer: str

    class MyPC:
        def __init__(self, *cpus: CPU):
            self.cpus = cpus

    class Comp(Bakery):
        core_num: int = Cake(4)
        manufacturer: str = Cake("Intel")
        cpu1: CPU = Cake(CPU, core_num=core_num, manufacturer=manufacturer)
        mypc: MyPC = Cake(MyPC, cpu1)

    bakery_mock.core_num = Cake(8)
    bakery_mock.manufacturer = Cake("AMD")

    await bakery_mock.patch(Comp)

    async with Comp() as my_pc:
        assert my_pc.mypc.cpus[0].core_num == 8
        assert Comp.mypc.cpus[0].core_num() == 8
        assert Comp().mypc.cpus[0].core_num == 8
        assert my_pc.mypc.cpus[0].manufacturer == "AMD"
        assert Comp.mypc.cpus[0].manufacturer() == "AMD"
        assert Comp.mypc.cpus[0]().manufacturer == "AMD"
        assert Comp.mypc.cpus()[0].manufacturer == "AMD"
        assert Comp.mypc().cpus[0].manufacturer == "AMD"
        assert Comp().mypc.cpus[0].manufacturer == "AMD"

        await bakery_mock.reset()

    async with Comp() as my_pc:
        assert my_pc.core_num == 4
        assert Comp.core_num() == 4
        assert Comp().core_num == 4
        assert my_pc.mypc.cpus[0].manufacturer == "Intel"
        assert Comp.mypc.cpus[0].manufacturer() == "Intel"
        assert Comp.mypc.cpus[0]().manufacturer == "Intel"
        assert Comp.mypc.cpus()[0].manufacturer == "Intel"
        assert Comp.mypc().cpus[0].manufacturer == "Intel"
        assert Comp().mypc.cpus[0].manufacturer == "Intel"

        assert my_pc.mypc.cpus[0].core_num == 4
        assert Comp.mypc.cpus[0].core_num() == 4
        assert Comp().mypc.cpus[0].core_num == 4
        assert my_pc.mypc.cpus[0].manufacturer == "Intel"
        assert Comp.mypc.cpus[0].manufacturer() == "Intel"
        assert Comp.mypc.cpus()[0].manufacturer == "Intel"
        assert Comp().core_num == 4
        assert Comp().manufacturer == "Intel"


async def test_complex_bakery_mock2(bakery_mock: BakeryMock) -> None:
    @dataclass
    class Settings:
        postgres_dsn: str
        some_list: List[str]
        some_dict: Dict[str, str]

    @dataclass
    class Manager:
        postgres_dsn: str
        item_0: str
        key_value: str

    class MyBakery(Bakery):
        settings: Settings = Cake(
            Settings,
            postgres_dsn="some dsn",
            some_list=["item0", "item_1"],
            some_dict={"key": "value"},
        )
        manager: Manager = Cake(
            Manager,
            postgres_dsn=settings.postgres_dsn,
            item_0=settings.some_list[0],
            key_value=settings.some_dict["key"],
        )

    postgres_dsn_mock: str = "mock"
    some_list_mock: List[str] = ["mock0", "mock1"]
    some_dict_mock: Dict[str, str] = {"key": "mock"}

    new_settings = Cake(
        Settings,
        postgres_dsn=postgres_dsn_mock,
        some_list=some_list_mock,
        some_dict=some_dict_mock,
    )
    bakery_mock.settings = new_settings

    async with bakery_mock(MyBakery):
        assert MyBakery().manager.postgres_dsn == postgres_dsn_mock
        assert MyBakery().manager.item_0 == some_list_mock[0]
        assert MyBakery().manager.key_value == some_dict_mock["key"]
        assert is_baked(new_settings)  # type: ignore
        assert MyBakery().settings == new_settings()  # type: ignore
