"""Test bakery methods."""
from typing import Any, Iterator
from uuid import UUID, uuid4

from bakery import Bakery, BakingMethod, Cake, hand_made


async def test_bakery_auto_call() -> None:
    """Test bakery auto call."""

    class House:
        """House."""

        def __init__(self):
            self.inside: bool = False

        async def __aenter__(self) -> "House":
            return self.__enter__()

        async def __aexit__(self, *_args: Any) -> None:
            return self.__exit__()

        def __enter__(self) -> "House":
            assert not self.inside
            self.inside = True
            return self

        def __exit__(self, *_args: Any) -> None:
            assert self.inside
            self.inside = False

    class Company(Bakery):
        """Company."""

        house: House = Cake(House)

    async with Company() as company:
        assert not company.house.inside

        async with company.house as house:
            assert house.inside
        assert not company.house.inside

        with company.house as house:
            assert house.inside
        assert not company.house.inside


async def test_cake_methods() -> None:
    """Test bake context focuses."""

    class House:
        """Car."""

        def __init__(self, value: str, avalue: str):
            self.inside: bool = False
            self.ainside: bool = False
            self.value: str = value
            self.avalue: str = avalue

        async def __aenter__(self) -> str:
            assert not self.ainside
            self.ainside = True
            return self.avalue

        def __call__(self) -> str:
            return "something"

        async def __aexit__(self, *_args: Any) -> None:
            assert self.ainside
            self.ainside = False

        def __enter__(self) -> str:
            assert not self.inside
            self.inside = True
            return self.value

        def __exit__(self, *_args: Any) -> None:
            assert self.inside
            self.inside = False

        async def open(self) -> str:
            """Open the door."""
            return "door"

    class Town(Bakery):
        """Town."""

        _value: str = Cake("value")
        _avalue: str = Cake("avalue")

        house1: House = Cake(House, value=_value, avalue=_avalue)
        house1_value = hand_made(
            Cake(house1),
            cake_baking_method=BakingMethod.BAKE_FROM_CM,
        )
        house1_avalue = hand_made(
            Cake(house1),
            cake_baking_method=BakingMethod.BAKE_FROM_ACM,
        )
        house1_smth = hand_made(
            Cake(house1),
            cake_baking_method=BakingMethod.BAKE_FROM_CALL,
        )

    async with Town() as town:
        assert town.house1_value == town.house1.value
        assert town.house1_avalue == town.house1.avalue
        assert town.house1_smth == "something"


async def test_cake_baking_auto_method_priority() -> None:
    """Test auto baking priority.

    BAKE_FROM_CORO_FUNC > BAKE_FROM_AWAITABLE > BAKE_FROM_ACM > BAKE_FROM_CM >BAKE_FROM_BUILTIN
    > BAKE_FROM_CALL
    """

    async def coro_func(*args: float) -> float:
        """Sum args."""
        return sum(args)

    class AwaitvsAsyncCm:
        """Awaitable > async cm."""

        def __await__(self) -> Iterator[str]:
            return "await"
            yield  # make a generator

        async def __aenter__(self) -> None:
            assert False

        async def __aexit__(self, *_args: Any) -> None:
            assert False

    class AsyncvsSync:
        """Async cm > sync cm."""

        async def __aenter__(self) -> str:
            return "aenter"

        async def __aexit__(self, *_args: Any) -> None:
            return

        def __enter__(self) -> None:
            assert False

        def __exit__(self, *_args: Any) -> None:
            assert False

    class SyncCMvsCall:
        """Sync cm > call."""

        def __enter__(self) -> str:
            return "enter"

        def __exit__(self, *_args: Any) -> None:
            return

        def __call__(self) -> None:
            assert False

    class Comparison(Bakery):
        """Comparison."""

        coro_func_sum: float = Cake(coro_func, 1, 2, 3)  # type: ignore
        coro_sum: float = Cake(coro_func(5, 6, 7))
        await_vs_asynccm: str = Cake(AwaitvsAsyncCm())  # type: ignore
        async_vs_sync: str = Cake(AsyncvsSync())
        synccm_vs_call: str = Cake(SyncCMvsCall())

    async with Comparison() as cmp:
        assert cmp.coro_func_sum == 6
        assert cmp.coro_sum == 18
        assert cmp.async_vs_sync == "aenter"
        assert cmp.await_vs_asynccm == "await"
        assert cmp.synccm_vs_call == "enter"


async def test_cake_no_bake() -> None:
    """Test no bake method."""

    value: UUID = uuid4()

    class MyBakery(Bakery):
        """My bakery."""

        cake: UUID = Cake(value)

    async with MyBakery():
        assert MyBakery.cake() == value

    async with MyBakery():
        assert MyBakery.cake() == value
