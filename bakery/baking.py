"""All relative to baking."""

from __future__ import annotations

__all__ = [
    "bake",
    "check_baking_method",
    "determine_baking_method",
    "unbake",
]
from inspect import isawaitable, iscoroutinefunction
from typing import Any, AsyncContextManager, ContextManager, Final, TypeVar

from .stuff import _LOGGER as logger  # noqa: N811
from .stuff import (
    BUILTIN_TYPES,
    BakingMethod,
    Cakeable,
    is_cake_or_piece,
)

BAKING_METHODS: Final = {
    BakingMethod.BAKE_FROM_CALL: lambda _recipe: callable(_recipe),
    BakingMethod.BAKE_FROM_CM: lambda _recipe: isinstance(_recipe, ContextManager),
    BakingMethod.BAKE_FROM_ACM: lambda _recipe: isinstance(_recipe, AsyncContextManager),
    BakingMethod.BAKE_FROM_BUILTIN: lambda _recipe: isinstance(_recipe, BUILTIN_TYPES),
    BakingMethod.BAKE_FROM_CORO_FUNC: lambda _recipe: iscoroutinefunction(_recipe),
    BakingMethod.BAKE_FROM_AWAITABLE: lambda _recipe: isawaitable(_recipe),
    BakingMethod.BAKE_NO_BAKE: lambda _recipe: True,
}


def determine_baking_method(recipe: Any) -> BakingMethod:
    """Determine the first available baking method for recipe."""
    if is_cake_or_piece(recipe):
        # Baking method depends on what object
        # really is inside cake/piece_of_cake
        return BakingMethod.BAKE_AUTO

    for method in [
        BakingMethod.BAKE_FROM_CORO_FUNC,
        BakingMethod.BAKE_FROM_AWAITABLE,
        BakingMethod.BAKE_FROM_ACM,
        BakingMethod.BAKE_FROM_CM,
        BakingMethod.BAKE_FROM_BUILTIN,
        BakingMethod.BAKE_FROM_CALL,
    ]:
        if check_baking_method(recipe, method):
            return method

    logger.info(f"Cannot determine baking method for recipe {recipe}")
    return BakingMethod.BAKE_NO_BAKE


def check_baking_method(recipe: Any, method: BakingMethod) -> bool:
    """Check baking method.

    return true if OK.
    """
    try:
        return BAKING_METHODS[method](recipe)
    except KeyError:
        msg = f"Cannot validate unknown baking method '{method}'."
        raise ValueError(msg) from None


T = TypeVar("T")


async def bake(cake: Cakeable[T]) -> T:
    """Bake cake."""
    return await cake.__aenter__()


async def unbake(
    cake: Cakeable[Any],
    exc_type: type | None = None,
    exc_value: BaseException | None = None,
    traceback: Any | None = None,
) -> None:
    """Unbake."""
    return await cake.__aexit__(exc_type, exc_value, traceback)
