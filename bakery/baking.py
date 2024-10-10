"""All relative to baking."""

from __future__ import annotations

__all__ = [
    "BakingMethod",
    "bake",
    "bake_recipe",
    "check_baking_method",
    "determine_baking_method",
    "unbake",
]
from enum import IntEnum, auto
from inspect import isawaitable, iscoroutinefunction
from typing import Any, AsyncContextManager, ContextManager, Final, TypeVar

from .stuff import _LOGGER as logger  # noqa: N811
from .stuff import (
    BUILTIN_TYPES,
    is_cake_or_piece,
    is_undefined,
    replace_cakes,
)


class BakingMethod(IntEnum):
    BAKE_AUTO = 0
    BAKE_FROM_CORO_FUNC = auto()
    BAKE_FROM_AWAITABLE = auto()
    BAKE_FROM_ACM = auto()
    BAKE_FROM_CM = auto()
    BAKE_FROM_BUILTIN = auto()
    BAKE_FROM_CALL = auto()
    BAKE_NO_BAKE = auto()


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
    if is_undefined(recipe):
        return BakingMethod.BAKE_NO_BAKE
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


async def bake_from_builtin(recipe: Any, _args: Any, _kwargs: Any) -> Any:
    return replace_cakes(recipe)


async def bake_from_call(recipe: Any, args: Any, kwargs: Any) -> Any:
    return recipe(*replace_cakes(args), **replace_cakes(kwargs))


async def bake_from_cm(recipe: Any, _args: Any, _kwargs: Any) -> Any:
    return recipe.__enter__()


async def bake_from_acm(recipe: Any, _args: Any, _kwargs: Any) -> Any:
    return await recipe.__aenter__()


async def bake_from_coro_func(recipe: Any, args: Any, kwargs: Any) -> Any:
    return await recipe(*replace_cakes(args), **replace_cakes(kwargs))


async def bake_from_awaitable(recipe: Any, _args: Any, _kwargs: Any) -> Any:
    return await recipe


async def bake_no_bake(recipe: Any, _args: Any, _kwargs: Any) -> Any:
    return recipe


METHOD_2_HOW_TO_BAKE: Final = {
    BakingMethod.BAKE_FROM_BUILTIN: bake_from_builtin,
    BakingMethod.BAKE_FROM_CALL: bake_from_call,
    BakingMethod.BAKE_FROM_CM: bake_from_cm,
    BakingMethod.BAKE_FROM_ACM: bake_from_acm,
    BakingMethod.BAKE_FROM_CORO_FUNC: bake_from_coro_func,
    BakingMethod.BAKE_FROM_AWAITABLE: bake_from_awaitable,
    BakingMethod.BAKE_NO_BAKE: bake_no_bake,
}


async def bake_recipe(
    recipe: Any,
    *,
    recipe_args: Any,
    recipe_kwargs: Any,
    baking_method: BakingMethod,
    cake_name: str,
) -> Any:
    if baking_method not in METHOD_2_HOW_TO_BAKE:
        msg = f"{cake_name}: Unknown baking method '{baking_method}' " f"for recipe {recipe}"
        raise ValueError(msg)

    return await METHOD_2_HOW_TO_BAKE[baking_method](
        recipe,
        recipe_args,
        recipe_kwargs,
    )


T = TypeVar("T")


async def bake(cake: AsyncContextManager[T]) -> T:
    return await cake.__aenter__()


async def unbake(
    cake: AsyncContextManager[T],
    exc_type: type | None = None,
    exc_value: BaseException | None = None,
    traceback: Any | None = None,
) -> None:
    await cake.__aexit__(exc_type, exc_value, traceback)
