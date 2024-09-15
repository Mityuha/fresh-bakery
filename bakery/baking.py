"""All relative to baking."""


__all__ = [
    "bake",
    "check_baking_method",
    "determine_baking_method",
    "unbake",
]
from inspect import isawaitable, iscoroutinefunction
from typing import Any, AsyncContextManager, ContextManager, Optional, TypeVar

from .stuff import _LOGGER as logger
from .stuff import BUILTIN_TYPES, BakingMethod, Cakeable, is_cake_or_piece


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
    if method == BakingMethod.BAKE_FROM_CALL:
        return callable(recipe)

    if method == BakingMethod.BAKE_FROM_CM:
        return isinstance(recipe, ContextManager)

    if method == BakingMethod.BAKE_FROM_ACM:
        return isinstance(recipe, AsyncContextManager)

    if method == BakingMethod.BAKE_FROM_BUILTIN:
        return isinstance(recipe, BUILTIN_TYPES)

    if method == BakingMethod.BAKE_FROM_CORO_FUNC:
        return iscoroutinefunction(recipe)

    if method == BakingMethod.BAKE_FROM_AWAITABLE:
        return isawaitable(recipe)

    if method == BakingMethod.BAKE_NO_BAKE:
        return True

    raise ValueError(f"Cannot validate unknown baking method '{method}'.")


T = TypeVar("T")


async def bake(cake: Cakeable[T]) -> T:
    """Bake cake."""
    return await cake.__aenter__()


async def unbake(
    cake: Cakeable[Any],
    exc_type: Optional[type] = None,
    exc_value: Optional[Exception] = None,
    traceback: Optional[Any] = None,
) -> None:
    """Unbake."""
    return await cake.__aexit__(exc_type, exc_value, traceback)
