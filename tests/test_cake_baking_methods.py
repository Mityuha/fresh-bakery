"""Test bakery methods."""

from dataclasses import dataclass
from typing import Any, Generator
from uuid import UUID, uuid4

import pytest

from bakery import Bakery, BakingMethod, Cake, hand_made


async def test_bakery_auto_call() -> None:
    """Test bakery auto call."""

    class House:
        """House."""

        def __init__(self) -> None:
            self.inside: bool = False

        async def __aenter__(self) -> "House":
            return self.__enter__()

        async def __aexit__(self, *_args: object) -> None:
            return self.__exit__()

        def __enter__(self) -> "House":
            assert not self.inside
            self.inside = True
            return self

        def __exit__(self, *_args: object) -> None:
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

        def __init__(self, value: str, avalue: str) -> None:
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

        async def __aexit__(self, *_args: object) -> None:
            assert self.ainside
            self.ainside = False

        def __enter__(self) -> str:
            assert not self.inside
            self.inside = True
            return self.value

        def __exit__(self, *_args: object) -> None:
            assert self.inside
            self.inside = False

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

        def __await__(self) -> Generator[Any, Any, str]:
            async def coro_wrap() -> str:
                return "await"

            return coro_wrap().__await__()

        async def __aenter__(self) -> None:
            raise AssertionError

        async def __aexit__(self, *_args: object) -> None:
            raise AssertionError

    class AsyncvsSync:
        """Async cm > sync cm."""

        async def __aenter__(self) -> str:
            return "aenter"

        async def __aexit__(self, *_args: object) -> None:
            return

        def __enter__(self) -> None:
            raise AssertionError

        def __exit__(self, *_args: object) -> None:
            raise AssertionError

    class SyncCMvsCall:
        """Sync cm > call."""

        def __enter__(self) -> str:
            return "enter"

        def __exit__(self, *_args: object) -> None:
            return

        def __call__(self) -> None:
            raise AssertionError

    class Comparison(Bakery):
        """Comparison."""

        coro_func_sum: float = Cake(coro_func, 1, 2, 3)
        coro_sum: float = Cake(coro_func(5, 6, 7))
        await_vs_asynccm: str = Cake(AwaitvsAsyncCm())
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


@pytest.mark.parametrize("hand_made_cake", [True, False])
async def test_hand_made_any_object(*, hand_made_cake: bool) -> None:
    """Test hand made any object.

    https://github.com/Mityuha/fresh-bakery/issues/26
    """

    class House:
        """Car."""

        def __init__(self, value: str, avalue: str) -> None:
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

        async def __aexit__(self, *_args: object) -> None:
            assert self.ainside
            self.ainside = False

        def __enter__(self) -> str:
            assert not self.inside
            self.inside = True
            return self.value

        def __exit__(self, *_args: object) -> None:
            assert self.inside
            self.inside = False

    @dataclass
    class HouseWrapper:
        """House wrapper."""

        house: House

    class Town(Bakery):
        """Town."""

        _value: str = Cake("value")
        _avalue: str = Cake("avalue")

        house1: House = Cake(House, value=_value, avalue=_avalue)
        house1_value = hand_made(
            Cake(house1)
            if hand_made_cake
            else House(value="value", avalue="avalue"),  # <<< Note: constant object
            cake_baking_method=BakingMethod.BAKE_FROM_CM,
        )
        house1_avalue = hand_made(
            Cake(house1) if hand_made_cake else House(value="value", avalue="avalue"),
            cake_baking_method=BakingMethod.BAKE_FROM_ACM,
        )
        house1_smth = hand_made(
            Cake(house1) if hand_made_cake else House(value="value", avalue="avalue"),
            cake_baking_method=BakingMethod.BAKE_FROM_CALL,
        )

        house2: House = Cake(House, value=_value, avalue=_avalue)
        house_wrap: HouseWrapper = Cake(HouseWrapper, house=house2)
        house2_value = hand_made(
            Cake(house_wrap.house) if hand_made_cake else house_wrap.house,
            cake_baking_method=BakingMethod.BAKE_FROM_CM,
        )
        house2_avalue = hand_made(
            Cake(house_wrap.house) if hand_made_cake else house_wrap.house,
            cake_baking_method=BakingMethod.BAKE_FROM_ACM,
        )
        house2_smth = hand_made(
            Cake(house_wrap.house) if hand_made_cake else house_wrap.house,
            cake_baking_method=BakingMethod.BAKE_FROM_CALL,
        )

    async with Town() as town:
        assert town.house1_value == town.house1.value == town.house2_value
        assert town.house1_avalue == town.house1.avalue == town.house2_avalue
        assert town.house1_smth == "something" == town.house2_smth
