"""Test cake special attributes.

For inspect module only.
"""

from functools import lru_cache, partial
from inspect import unwrap
from typing import Any, Callable, cast

from bakery import Bakery, Cake


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
