"""Test store."""

from __future__ import annotations

import sys
import types
from collections.abc import AsyncIterator, Callable, Iterator
from dataclasses import dataclass
from typing import (
    Any,
    ClassVar,
    cast,
    no_type_check,
)

import pytest

from bakery import Bakery, Cake, PieceOfCake, bake, cake_name, is_baked, unbake

from . import aclosing


async def test_simple_bakery1() -> None:
    """Test simple bakery."""

    class CPU:
        """Settings."""

        def __init__(self, core_num: int, manufacturer: str) -> None:
            self.core_num: int = core_num
            self.manufacturer: str = manufacturer

    class MyPC(Bakery):
        """My bakery."""

        core_num: int = Cake(4)
        manufacturer: str = Cake("Intel")
        cpu1: CPU = Cake(CPU, core_num=core_num, manufacturer=manufacturer)
        cpu2: CPU = Cake(CPU, core_num=2, manufacturer="AMD")

    exception: type[Exception] = AttributeError
    if sys.version_info >= (3, 11):
        exception = TypeError

    with pytest.raises(exception):
        # Can only be used with instance
        async with MyPC:  # type: ignore[attr-defined]
            pass

    async with MyPC() as my_pc:
        assert my_pc.core_num == 4
        assert my_pc.manufacturer == "Intel"
        assert my_pc.cpu1.core_num == 4
        assert my_pc.cpu1.manufacturer == "Intel"
        assert my_pc.cpu2.core_num == 2
        assert my_pc.cpu2.manufacturer == "AMD"


@no_type_check
async def test_simple_bakery2() -> None:
    """Test simple bakery."""

    class CPU:
        """Settings."""

        def __init__(self, core_num: int, manufacturer: str) -> None:
            self.core_num: int = core_num
            self.manufacturer: str = manufacturer

    class MyPC(Bakery):
        """My bakery."""

        core_num: int = Cake(4)
        manufacturer: str = Cake("Intel")
        cpu1: CPU = Cake(CPU, core_num=core_num, manufacturer=manufacturer)
        cpu2: CPU = Cake(CPU, core_num=2, manufacturer="AMD")

    async with MyPC():
        assert MyPC.core_num() == 4
        assert MyPC.manufacturer() == "Intel"
        assert MyPC.cpu1.core_num() == 4
        assert MyPC.cpu1().core_num == 4
        assert MyPC.cpu1.manufacturer() == "Intel"
        assert MyPC.cpu1().manufacturer == "Intel"
        assert MyPC.cpu2.core_num() == 2
        assert MyPC.cpu2().core_num == 2
        assert MyPC.cpu2.manufacturer() == "AMD"
        assert MyPC.cpu2().manufacturer == "AMD"

    with pytest.raises(ValueError, match="core_num"):
        # if test fails here check stuff.is_baked method
        # to make sure getattr gets right private attribute
        _ = MyPC.core_num()

    recipe_expected: list[tuple[Callable, Any]] = [
        (MyPC.core_num, 4),
        (MyPC.manufacturer, "Intel"),
        (MyPC.cpu1.core_num, 4),
        (MyPC.cpu1.manufacturer, "Intel"),
        (MyPC.cpu2.core_num, 2),
        (MyPC.cpu2.manufacturer, "AMD"),
    ]

    await MyPC.aopen()
    for recipe, expected in recipe_expected:
        assert recipe() == expected

    await MyPC.aclose()

    for recipe, _ in recipe_expected:
        with pytest.raises(ValueError, match="is not baked. Just bake it!"):
            _ = recipe()


async def test_simple_recipe1() -> None:
    """Test recipe."""

    class Box:
        """My juice box."""

        def __init__(self, desc: str) -> None:
            self.desc = desc

    desc: str = "apple juice box"
    recipe1: Box = Cake(Box, desc=desc)

    async with recipe1 as box:  # type: ignore[attr-defined]
        assert box.desc == desc

        piece_of_cake: PieceOfCake = cast(PieceOfCake, recipe1.desc)
        assert piece_of_cake() == desc

    with pytest.raises(ValueError, match=f"{recipe1} is not baked. Just bake it!"):
        _ = recipe1.desc()  # type: ignore[operator]

    box = await bake(recipe1)  # type: ignore[arg-type]
    assert recipe1().desc == box.desc  # type: ignore[operator]
    assert box.desc == desc
    assert recipe1.desc() == desc  # type: ignore[operator]
    await unbake(recipe1)  # type: ignore[arg-type]


async def test_piece_of_cake() -> None:
    """Test piece of cake.

    Not worry about saving piece of cakes. I.e. test piece of cake copying.
    """

    class CPU:
        """Cpu."""

        def __init__(self, core_num: int, manufacturer: str) -> None:
            self.core_num: int = core_num
            self.manufacturer: str = manufacturer

    class MyPC:
        """My pc."""

        def __init__(self, *cpus: CPU) -> None:
            self.cpus = cpus

    class Computer(Bakery):
        """My bakery."""

        core_num: int = Cake(4)
        manufacturer: str = Cake("Intel")
        cpu1: CPU = Cake(CPU, core_num=core_num, manufacturer=manufacturer)
        cpu2: CPU = Cake(CPU, core_num=2, manufacturer="AMD")
        my_pc: MyPC = Cake(MyPC, cpu1, cpu2)

    async with Computer():
        cpu1 = Computer.my_pc.cpus[0]
        assert cpu1.core_num() == Computer.core_num()
        assert cpu1.core_num() == Computer.core_num()
        assert cpu1.manufacturer() == Computer.manufacturer()
        assert cpu1.manufacturer() == Computer.manufacturer()


async def test_complex_bakery1() -> None:
    """Test complex bakery."""

    @dataclass
    class Core:
        """Core."""

        num: int

    @dataclass
    class CPU:
        """CPU."""

        core: Core

    @dataclass
    class PComp:
        """PComp."""

        cpu: CPU

    @dataclass
    class Home:
        """Home."""

        pcomp: PComp

    class MyHome(Bakery):
        """My bakery."""

        core_num: int = Cake(4)
        my_core: Core = Cake(Core, core_num)
        my_cpu: CPU = Cake(CPU, my_core)
        my_comp: PComp = Cake(PComp, my_cpu)
        home: Home = Cake(Home, my_comp)

    async with MyHome() as home:
        assert home.home.pcomp.cpu.core.num == home.core_num

        assert MyHome.home.pcomp.cpu.core.num() == MyHome.core_num()
        assert home.home.pcomp.cpu.core.num == MyHome.home.pcomp.cpu.core.num()

    home2: MyHome = await MyHome.aopen()
    assert home2.home.pcomp.cpu.core.num == home2.core_num
    assert MyHome.home.pcomp.cpu.core.num() == MyHome.core_num()

    await MyHome.aclose()

    with pytest.raises(ValueError, match="Cake 'home' is not baked. Just bake it!"):
        _ = MyHome.home.pcomp.cpu.core()


async def test_complex_bakery2() -> None:
    """Test complex bakery."""

    @dataclass
    class Core:
        """Core."""

        num: int

    class CPU:
        """CPU."""

        def __init__(self, core: Core) -> None:
            self.cores: dict[str, Core] = {"core": core}

    class PComp:
        """PComp."""

        def __init__(self, cpu: CPU) -> None:
            self.cpus: list[CPU] = [cpu]

    @dataclass
    class Home:
        """Home."""

        pcomp: PComp

    class MyHome(Bakery):
        """My bakery."""

        core_num: int = Cake(4)
        my_core: Core = Cake(Core, core_num)
        my_cpu: CPU = Cake(CPU, my_core)
        my_comp: PComp = Cake(PComp, my_cpu)
        home: Home = Cake(Home, my_comp)

    async with MyHome() as home:
        assert home.home.pcomp.cpus[0].cores["core"].num == home.core_num

        assert MyHome.home.pcomp.cpus[0].cores["core"].num() == MyHome.core_num()
        assert MyHome.home.pcomp.cpus[0].cores["core"]().num == MyHome.core_num()
        assert MyHome.home.pcomp.cpus[0].cores()["core"].num == MyHome.core_num()
        assert MyHome.home.pcomp.cpus[0]().cores["core"].num == MyHome.core_num()
        assert MyHome.home.pcomp.cpus()[0].cores["core"].num == MyHome.core_num()
        assert MyHome.home.pcomp().cpus[0].cores["core"].num == MyHome.core_num()
        assert MyHome.home().pcomp.cpus[0].cores["core"].num == MyHome.core_num()
        assert MyHome().home.pcomp.cpus[0].cores["core"].num == MyHome.core_num()
        assert (
            home.home.pcomp.cpus[0].cores["core"].num
            == MyHome.home.pcomp.cpus[0].cores["core"].num()
        )

    home = await MyHome.aopen()
    assert home.home.pcomp.cpus[0].cores["core"].num == home.core_num
    assert MyHome.home.pcomp.cpus[0].cores["core"].num() == MyHome.core_num()
    assert (
        MyHome().home.pcomp.cpus[0].cores["core"].num
        == MyHome.home.pcomp.cpus[0].cores["core"]().num
    )

    await MyHome.aclose()

    with pytest.raises(ValueError, match="Cake 'home' is not baked. Just bake it!"):
        _ = MyHome.home.pcomp.cpus[0].cores["core"]()


async def test_closed_bakery() -> None:
    """Test closed bakery."""

    class MyBakery(Bakery):
        """My bakery."""

        browny: str = Cake("browny")

    with pytest.raises(ValueError, match="Cake 'browny' is not baked. Just bake it!"):
        _ = MyBakery().browny

    async with MyBakery():
        assert MyBakery().browny == "browny"
        assert MyBakery.browny() == "browny"

    await MyBakery.aopen()
    async with aclosing(MyBakery):
        assert MyBakery().browny == "browny"
        assert MyBakery.browny() == "browny"


def gen() -> Iterator:
    """Just stub."""
    yield from range(3)


async def async_gen() -> AsyncIterator:
    """Just stub."""
    for i in gen():
        yield i


@pytest.mark.parametrize(
    "obj",
    [
        True,
        False,
        bytearray([1, 2]),
        bytes(1),
        classmethod(cast(Callable, lambda: 1)),
        complex(1, 2),
        {"a": 1},
        1.1,
        frozenset({1, 2, 3}),
        2,
        [1, 2],
        (x for x in [1, 2]),
        memoryview(b""),
        property(cast(Callable, lambda: 1)),
        range(1, 2),
        set({1, 2}),
        slice(1, 2),
        staticmethod(lambda: 1),
        "123",
        super(object),
        (1, 2),
        zip([], []),
        None,
        Ellipsis,
        async_gen(),
        gen(),
        types.ModuleType("asd"),
        types.SimpleNamespace(),
    ],
)
async def test_bakery_builtins(obj: Any) -> None:
    """Test builtins."""

    class MyBuiltin(Bakery):
        """Mybuilt-in object."""

        my_obj: Any = Cake(obj)

    class MyBuiltin2(Bakery):
        """Mybuilt-in object with no cake."""

        my_obj: Any = obj

    async with MyBuiltin() as mybuilt, MyBuiltin2() as mybuilt2:
        assert mybuilt.my_obj == obj
        assert mybuilt2.my_obj == obj

        assert MyBuiltin.my_obj() == obj
        assert MyBuiltin2.my_obj() == obj


async def test_bakery_value_wrapping() -> None:
    """Test value wrapping."""

    class Wrapper(Bakery):
        """Wrapper."""

        num1: int = 4
        num2: int = Cake(4)

        txt1: str = "asd"
        txt2: str = Cake("asd")

    async with Wrapper() as wrap:
        assert wrap.num1 == wrap.num2 == Wrapper.num1() == Wrapper.num2()
        assert wrap.txt1 == wrap.txt2 == Wrapper.txt1() == Wrapper.txt2()

        assert cake_name(Wrapper.num1) == "num1"
        assert cake_name(Wrapper.num2) == "num2"
        assert cake_name(Wrapper.txt1) == "txt1"
        assert cake_name(Wrapper.txt2) == "txt2"


async def test_bakery_caches() -> None:
    """Test bakery caches."""

    class MyBakery(Bakery):
        """Bakery."""

        cake_num: int = 1
        receipt: str = "receipt"
        prices: ClassVar[dict] = {1: 1, 2: 2}

    bakery_items1: dict = {}
    async with MyBakery() as shelf1:
        bakery_items1 = MyBakery.__bakery_items__  # type: ignore[assignment]
        async with MyBakery() as shelf2:
            assert shelf1.prices is shelf2.prices

        shelf2 = await MyBakery.aopen()
        assert shelf1.prices is shelf2.prices
        await MyBakery.aclose()

    bakery1 = await MyBakery.aopen()
    async with MyBakery() as bakery2:
        assert bakery1.prices is bakery2.prices

    await MyBakery.aclose()

    assert MyBakery.__bakery_items__ == bakery_items1


async def test_object_wrapped_is_object() -> None:
    """Test that object wrapped by cake is simply object."""

    class Car:
        """Car."""

        def __init__(self, brand: str) -> None:
            self.brand = brand

    class Garage(Bakery):
        """Garage."""

        car1: Car = Cake(Car("VAZ"))
        car2: Car = Cake(Car("VAZ"))

    async with Garage() as garage:
        assert garage.car1.brand == garage.car2.brand == "VAZ"
        assert cake_name(Garage.car2) == "car2"


async def test_no_cakes() -> None:
    """What if no cakes specified?."""

    @dataclass
    class Car:
        """Car."""

        brand: str

    @dataclass
    class Garage:
        """Garage."""

        cars: list[Car]

    class House(Bakery):
        """House."""

        car1: Car = Car("VAZ")
        car2: Car = Car("VOLGA")
        garage: Garage = Garage([car1, car2])

    async with House() as house:
        assert house.garage.cars[0].brand == "VAZ"
        assert house.garage.cars[1].brand == "VOLGA"


async def test_multiple_open_close() -> None:
    """Test multiple open close."""

    class MyPC(Bakery):
        """My bakery."""

        core_num: int = 4
        manufacturer: str = "Intel"

    for _ in range(5):
        async with MyPC() as my_pc:
            assert my_pc.core_num == 4
            assert MyPC.core_num() == 4
            assert MyPC().core_num == 4
            assert my_pc.manufacturer == "Intel"
            assert MyPC.manufacturer() == "Intel"
            assert MyPC().manufacturer == "Intel"

    await MyPC.aopen()

    async with MyPC() as my_pc:
        assert my_pc.core_num == 4
        assert MyPC.__bakery_visitors__ == 2
        await MyPC.aclose()
        assert MyPC.__bakery_visitors__ == 1

        assert MyPC.core_num() == 4

    assert MyPC.__bakery_visitors__ == 0

    assert not is_baked(MyPC.core_num)
    assert not is_baked(MyPC.manufacturer)


async def test_bakery_plain_factory() -> None:
    """Bakery cake as a factory."""

    def multiple(*args: float) -> float:
        """Multiple args."""
        res: float = args[0]
        for i in args[1:]:
            res *= i

        return res

    class MultiBakery(Bakery):
        """Multiplication bakery."""

        # alias of
        multy: Callable = Cake(lambda: multiple)

    async with MultiBakery() as worker:
        assert worker.multy(5, 6) == 30
        assert worker.multy(1, 2, 3, 4) == 24
        assert worker.multy(10, 20, 30) == 6000


async def test_cake_subscription() -> None:
    """Test cake subscription."""

    class IndexBook:
        """Index book."""

        def __init__(self, index: dict[int, str]) -> None:
            self.index = index

    class Book(Bakery):
        """Book."""

        index: dict[int, str] = Cake({1: "page1", 2: "page2", 3: "etc."})

        index_book: IndexBook = Cake(IndexBook, index)
        page1 = index[1]
        page2 = index[2]
        page3 = index[3]

    async with Book() as book:
        assert book.index_book.index is book.index
        assert book.page1 == book.index[1]
        assert book.page2 == book.index[2]
        assert book.page3 == book.index[3]


async def test_piece_of_cake_as_argument() -> None:
    """Piece of cake as argument."""

    @dataclass
    class Settings:
        """Some settings."""

        postgres_dsn: str
        some_list: list[str]
        some_dict: dict[str, str]

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

    async with MyBakery() as bakery:
        assert bakery.manager.postgres_dsn == bakery.settings.postgres_dsn
        assert bakery.manager.item_0 == bakery.settings.some_list[0]
        assert bakery.manager.key_value == bakery.settings.some_dict["key"]
