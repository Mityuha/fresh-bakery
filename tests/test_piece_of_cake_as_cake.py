"""Test piece of cake as cake.

https://github.com/Mityuha/fresh-bakery/issues/13.
"""

from typing import Any

from bakery import Bakery, BakingMethod, Cake, hand_made


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


async def test_piece_of_cake_is_not_cake() -> None:
    """Test piece of cake is not cake (old style)."""

    class MyBakery(Bakery):
        """My bakery."""

        some_class: SomeClass = Cake(SomeClass)
        check: bool = Cake(  # type: ignore
            wrapper,
            coro=hand_made(
                Cake(Cake(some_class.get_const)),  # <<< piece of cake
                cake_baking_method=BakingMethod.BAKE_FROM_CALL,
            ),
            result=42,
        )

    async with MyBakery() as bakery:
        assert bakery.check
