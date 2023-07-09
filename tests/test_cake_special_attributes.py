"""Test cake special attributes.

For inspect module only.
"""
from functools import partial
from typing import Any, Callable

from bakery import Bakery, Cake, cake_ingredients


def test_callable_cake_attributes() -> None:
    """Test callable cake attributes."""

    async def some_coro(
        param1: int,
        param2: str = "default",
        param3: float = 0.5,
    ) -> None:
        """Just for test."""
        print(param1, param2, param3)
        return None

    class MyBakery(Bakery):
        """Bakery."""

        callable_cake = Cake(some_coro)

    assert MyBakery.callable_cake.__name__ == some_coro.__name__
    assert MyBakery.callable_cake.__code__ == some_coro.__code__
    assert MyBakery.callable_cake.__defaults__ == some_coro.__defaults__
    assert MyBakery.callable_cake.__kwdefaults__ == some_coro.__kwdefaults__
    assert MyBakery.callable_cake.__annotations__ == some_coro.__annotations__
    assert MyBakery.callable_cake._is_coroutine is False  # pylint: disable=protected-access


def test_not_callable_cake_attributes() -> None:
    """Test not callable cake attributes."""

    class MyBakery(Bakery):
        """Bakery."""

        const: int = Cake(1)

    assert MyBakery.const.__name__ == cake_ingredients(MyBakery.const).__call__.__name__  # type: ignore
    assert MyBakery.const.__code__ == cake_ingredients(MyBakery.const).__call__.__code__  # type: ignore
    assert MyBakery.const.__defaults__ == cake_ingredients(MyBakery.const).__call__.__defaults__  # type: ignore
    assert (
        MyBakery.const.__kwdefaults__ == cake_ingredients(MyBakery.const).__call__.__kwdefaults__  # type: ignore
    )
    assert (
        MyBakery.const.__annotations__ == cake_ingredients(MyBakery.const).__call__.__annotations__  # type: ignore
    )
    assert MyBakery.const._is_coroutine is False  # pylint: disable=protected-access


async def test_cake_partial_func_attribute() -> None:
    """Test cake partial."""

    def multiplier(x: float, y: float, z: float) -> float:  # pylint: disable=invalid-name
        """Multiple it."""
        return x * y * z

    class MyBakery(Bakery):
        """Bakery."""

        x2_multiplier: Callable = Cake(partial, multiplier, y=2)  # type: ignore
        x6_multiplier: Callable = Cake(partial, x2_multiplier, z=3)

    def unwrap_partial(value: Any) -> Any:
        output: Any = value.func if hasattr(value, "func") else value
        while hasattr(output, "func"):
            output = output.func
            print(output, type(output))

        return output

    assert unwrap_partial(MyBakery.x2_multiplier) is MyBakery.x2_multiplier

    async with MyBakery():
        assert unwrap_partial(MyBakery.x2_multiplier()) is multiplier
        assert unwrap_partial(MyBakery.x6_multiplier()) is multiplier

        assert MyBakery.x6_multiplier()(6) == 36
