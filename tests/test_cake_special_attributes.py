"""
Test cake special attributes.

For inspect module only.
"""

from functools import lru_cache, partial
from inspect import unwrap
from typing import Any, Callable, cast

from bakery import Bakery, Cake, cake_ingredients


def test_callable_cake_attributes() -> None:
    """Test callable cake attributes."""

    async def some_coro(
        param1: int,
        param2: str = "default",
        param3: float = 0.5,
    ) -> None:
        """Just for test."""
        print(param1, param2, param3)  # noqa: T201

    class MyBakery(Bakery):
        """Bakery."""

        callable_cake = Cake(some_coro)

    assert MyBakery.callable_cake.__name__ == some_coro.__name__
    assert MyBakery.callable_cake.__code__ == some_coro.__code__
    assert MyBakery.callable_cake.__defaults__ == some_coro.__defaults__
    assert MyBakery.callable_cake.__kwdefaults__ == some_coro.__kwdefaults__
    assert MyBakery.callable_cake.__annotations__ == some_coro.__annotations__
    assert MyBakery.callable_cake._is_coroutine is False


def test_not_callable_cake_attributes() -> None:
    """Test not callable cake attributes."""

    class MyBakery(Bakery):
        """Bakery."""

        const: int = Cake(1)

    assert MyBakery.const.__name__ == cake_ingredients(MyBakery.const).__call__.__name__
    assert MyBakery.const.__code__ == cake_ingredients(MyBakery.const).__call__.__code__
    assert MyBakery.const.__defaults__ == cake_ingredients(MyBakery.const).__call__.__defaults__
    assert (
        MyBakery.const.__kwdefaults__ == cake_ingredients(MyBakery.const).__call__.__kwdefaults__
    )
    assert (
        MyBakery.const.__annotations__ == cake_ingredients(MyBakery.const).__call__.__annotations__
    )
    assert MyBakery.const._is_coroutine is False


async def test_cake_partial_func_attribute() -> None:
    """Test cake partial."""

    def multiplier(x: float, y: float, z: float) -> float:
        """Multiple it."""
        return x * y * z

    class MyBakery(Bakery):
        """Bakery."""

        x2_multiplier: Callable = Cake(partial, cast(Callable, multiplier), y=2)
        x6_multiplier: Callable = Cake(partial, x2_multiplier, z=3)

    def unwrap_partial(value: Any) -> Any:
        output: Any = value.func if hasattr(value, "func") else value
        while hasattr(output, "func"):
            output = output.func

        return output

    assert unwrap_partial(MyBakery.x2_multiplier) is MyBakery.x2_multiplier

    async with MyBakery():
        assert unwrap_partial(MyBakery.x2_multiplier) is MyBakery.x2_multiplier
        assert unwrap_partial(MyBakery.x6_multiplier) is MyBakery.x6_multiplier
        assert unwrap_partial(MyBakery.x2_multiplier()) is multiplier
        assert unwrap_partial(MyBakery.x6_multiplier()) is multiplier

        assert MyBakery.x6_multiplier()(6) == 36


async def test_cake_wrapped_func_attribute() -> None:
    """Test cake partial."""

    def id_func(entity: str) -> str:
        """Identity function."""
        return entity

    class MyBakery(Bakery):
        """Bakery."""

        id_func1: Callable = Cake(lru_cache(None), id_func)
        id_func2: Callable = Cake(lru_cache(None), id_func1)

    assert unwrap(MyBakery.id_func1) is MyBakery.id_func1

    async with MyBakery():
        assert unwrap(MyBakery.id_func1) is MyBakery.id_func1
        assert unwrap(MyBakery.id_func2) is MyBakery.id_func2
        assert unwrap(MyBakery.id_func1()) is id_func
        assert unwrap(MyBakery.id_func2()) is id_func

        assert MyBakery.id_func2()("str") == "str"
        # cache hit
        assert MyBakery.id_func2()("str") == "str"
        assert MyBakery.id_func2().cache_info().hits == 1  # type: ignore[attr-defined]

        # source function call without cache
        assert unwrap(MyBakery.id_func2())("str") == "str"

        # cache hits are still the same
        assert MyBakery.id_func2().cache_info().hits == 1  # type: ignore[attr-defined]


async def test_special_attributes_refactoring() -> None:
    """Code refactoring for special attributes."""

    class Controller:
        """Controller."""

        def __init__(self) -> None:
            self.func = lambda x: x * 2

    def mapper(func: Callable) -> Callable:
        """Mapper."""
        return func

    class MyBakery(Bakery):
        """Bakery."""

        ctrl: Controller = Cake(Controller)
        ctrl_func: Callable = Cake(
            mapper,
            Cake(getattr, ctrl, "func"),
        )

    async with MyBakery():
        assert MyBakery().ctrl_func(10) == 20
