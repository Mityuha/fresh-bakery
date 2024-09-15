"""
Test piece of cake as cake.

https://github.com/Mityuha/fresh-bakery/issues/13.
"""

from contextlib import contextmanager
from dataclasses import dataclass
from typing import Any, AsyncIterator, Iterator

from bakery import Bakery, BakingMethod, Cake, hand_made, unbake

from . import asynccontextmanager


class SomeClass:
    """Foo class with coro function bar."""

    @staticmethod
    async def get_const() -> int:
        """Just your answer."""
        return 42


async def wrapper(coro: Any, result: Any) -> bool:
    """Wrapper."""
    res_got = await coro
    return res_got == result


async def test_piece_of_cake_as_cake() -> None:
    """Test piece of cake as cake."""

    class POCTester:
        """Piece of cake tester."""

        CONST: int = 42

        def __init__(self) -> None:
            self.acm_baked: bool = False
            self.cm_baked: bool = False

        @staticmethod
        async def coro_sum(num1: float, num2: float) -> float:
            """Just async sum."""
            return num1 + num2

        @asynccontextmanager
        async def acm_sum(self, num1: float, num2: float) -> AsyncIterator[float]:
            """Acm multiplication."""
            self.acm_baked = True
            yield num1 + num2
            self.acm_baked = False

        @contextmanager
        def cm_sum(self, num1: float, num2: float) -> Iterator[float]:
            """Cm substraction."""
            self.cm_baked = True
            yield num1 + num2
            self.cm_baked = False

        @staticmethod
        def call_sum(num1: float, num2: float) -> float:
            """Plus one function."""
            return num1 + num2

    class MyBakery(Bakery):
        """MyBakery."""

        poc: POCTester = Cake(POCTester)
        coro_poc: float = Cake(poc.coro_sum, num1=5, num2=6)
        acm_poc: float = Cake(
            Cake(poc.acm_sum, num1=8, num2=9),
        )
        cm_poc: float = Cake(
            Cake(poc.cm_sum, num1=10, num2=13),
        )
        call_poc: float = Cake(poc.call_sum, num1=4, num2=18)
        const_poc: float = Cake(poc.CONST)

    async with MyBakery() as bakery:
        poc: POCTester = bakery.poc
        assert bakery.coro_poc == 5 + 6
        assert bakery.acm_poc == 8 + 9
        assert bakery.cm_poc == 10 + 13
        assert bakery.call_poc == 4 + 18
        assert bakery.const_poc == bakery.poc.CONST

        assert poc.cm_baked
        assert poc.acm_baked

    assert not poc.cm_baked
    assert not poc.acm_baked


async def test_piece_of_cake_with_hand_made() -> None:
    """Test piece of cake is not cake (old style)."""

    class MyBakery(Bakery):
        """My bakery."""

        some_class: SomeClass = Cake(SomeClass)
        check: bool = Cake(
            wrapper,
            coro=hand_made(
                Cake(some_class.get_const),  # <<< piece of cake
                cake_baking_method=BakingMethod.BAKE_FROM_CALL,
            ),
            result=42,
        )

    async with MyBakery() as bakery:
        assert bakery.check


async def test_awkward_unbaking() -> None:
    """Test awkward piece of cake unbaking."""

    class CMTester:
        """(A)CM tester."""

        async def __aenter__(self) -> str:
            return "avalue"

        async def __aexit__(self, *_args: object) -> None:
            return None

        def __enter__(self) -> str:
            return "value"

        def __exit__(self, *_args: object) -> None:
            return None

    @dataclass
    class Wrapper:
        """CMTester wrapper."""

        obj: CMTester

    class AwkBakery(Bakery):
        """Awkward bakery."""

        wrapper: Wrapper = Cake(Wrapper, obj=Cake(CMTester))
        acm_obj = hand_made(
            wrapper.obj,
            cake_baking_method=BakingMethod.BAKE_FROM_ACM,
        )
        cm_obj = hand_made(
            wrapper.obj,
            cake_baking_method=BakingMethod.BAKE_FROM_CM,
        )

    async with AwkBakery() as bakery:
        assert bakery.acm_obj == "avalue"
        assert bakery.cm_obj == "value"
        # awkward thing goes here
        await unbake(AwkBakery.wrapper)
