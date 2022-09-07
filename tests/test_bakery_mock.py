"""Test bakery mock."""


from dataclasses import dataclass
from time import sleep
from typing import Any, Dict, List

from bakery import Bakery, Cake, is_baked
from bakery.testbakery import BakeryMock


async def test_bakery_mock1(bakery_mock: BakeryMock) -> None:
    """Test bakery mock."""

    class MyPC(Bakery):
        """My bakery."""

        core_num: int = Cake(4)
        manufacturer: str = Cake("Intel")

    bakery_mock.core_num, bakery_mock.manufacturer = 5, "AMD"

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


async def test_bakery_patch_before_open(bakery_mock: BakeryMock) -> None:
    """Test bakery patch before open."""

    class MyPC(Bakery):
        """My bakery."""

        core_num: int = Cake(4)
        manufacturer: str = Cake("Intel")

    bakery_mock.core_num = Cake(6)
    bakery_mock.manufacturer = "AMD"

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


async def test_complex_bakery_mock1(bakery_mock: BakeryMock) -> None:
    """Test bakery mock complex enough."""

    @dataclass
    class CPU:
        """Cpu."""

        core_num: int
        manufacturer: str

    class MyPC:
        """My pc."""

        def __init__(self, *cpus: CPU):
            self.cpus = cpus

    class Comp(Bakery):
        """Bakery."""

        core_num: int = Cake(4)
        manufacturer: str = Cake("Intel")
        cpu1: CPU = Cake(CPU, core_num=core_num, manufacturer=manufacturer)
        mypc: MyPC = Cake(MyPC, cpu1)

    bakery_mock.core_num = 8
    bakery_mock.manufacturer = "AMD"

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
    """Test bakery mock."""

    @dataclass
    class Settings:
        """Some settings."""

        postgres_dsn: str
        some_list: List[str]
        some_dict: Dict[str, str]

    @dataclass
    class Manager:
        """Some manager."""

        postgres_dsn: str
        item_0: str
        key_value: str

    class MyBakery(Bakery):
        """My bakery."""

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


async def test_bakery_mock_replace_recipe(bakery_mock: BakeryMock) -> None:
    """Test recipe replacement."""

    def sleeper(sleep_for: float) -> float:
        """Simply sleep."""
        sleep(sleep_for)
        return sleep_for

    class Comp(Bakery):
        """Comp."""

        sleeper1: float = Cake(sleeper, 100)
        sleeper2: float = Cake(sleeper, 200)
        some_list: list = Cake([1, 2, Cake(sleeper, 300)])
        total: float = Cake(sum, (sleeper1, sleeper2, some_list[2]))  # type: ignore

    class Comp2(Bakery):
        """Comp2."""

        comp: Comp = Cake(Comp())

    bakery_mock.sleeper1 = lambda *_args: 100
    bakery_mock.sleeper2 = lambda *_args: 200
    bakery_mock.some_list = [1, 2, 300]

    async with bakery_mock(Comp):
        assert Comp().sleeper1 == 100
        assert Comp().sleeper2 == 200
        assert Comp().some_list[2] == 300
        assert Comp().total == 600

    async with bakery_mock(Comp), Comp2():
        assert Comp2().comp.sleeper1 == 100
        assert Comp2().comp.sleeper2 == 200
        assert Comp2().comp.some_list[2] == 300
        assert Comp2().comp.total == 600


async def test_nested_cakes_mock_simple(bakery_mock: BakeryMock) -> None:
    """Test simple nested cakes mock."""

    class MyBakery(Bakery):
        """MyBakery."""

        value: float = Cake(
            sum,
            Cake(
                Cake(
                    list,
                    [Cake(sum, [1, 2, 3])],  # type: ignore
                ),
            ),
        )

    async with MyBakery() as bakery:
        assert bakery.value == 6

    bakery_mock.value = Cake(10)
    async with bakery_mock(MyBakery):
        assert MyBakery().value == 10

    bakery_mock.value = lambda *args: sum(*args, 4)  # type: ignore
    async with bakery_mock(MyBakery):
        assert MyBakery().value == 10


async def test_nested_cakes_mock(bakery_mock: BakeryMock) -> None:
    """Test nested cakes mock."""

    class Database:
        """Database."""

        def __init__(self, table: str):
            self.connected: bool = False
            self.table: str = table

        async def __aenter__(self) -> "Database":
            self.connected = True
            return self

        async def __aexit__(self, *_args: Any) -> None:
            self.connected = False

    class MyBakery(Bakery):
        """MyBakery."""

        database: Database = Cake(Cake(Database, table=Cake("table")))

    async with MyBakery() as bakery:
        assert bakery.database.connected

    bakery_mock.database = Cake(None)

    async with bakery_mock(MyBakery):
        assert MyBakery().database is None
