"""All relative to baking."""


__all__ = [
    "Ingredients",
    "bake",
    "check_baking_method",
    "determine_baking_method",
    "unbake",
]
from copy import deepcopy
from inspect import isawaitable, iscoroutinefunction
from typing import Any, AsyncContextManager, ContextManager, Optional, TypeVar

from typing_extensions import Final

from .stuff import _LOGGER as logger
from .stuff import (
    BUILTIN_TYPES,
    BakingMethod,
    Cakeable,
    cake_name,
    flatten,
    is_baked,
    is_cake,
    is_cake_or_piece,
    is_piece_of_cake,
    replace_cakes,
)


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


class Ingredients:
    """Cake ingredients.

    Cake internal state.
    """

    # pylint: disable=too-many-instance-attributes

    def __init__(
        self,
        recipe: Any,
        *recipe_args: Any,
        cake_baking_method: BakingMethod = BakingMethod.BAKE_AUTO,
        **recipe_kwargs: Any,
    ):

        self.recipe: Final[Any] = recipe
        self.recipe_args: Final[Any] = recipe_args
        self.recipe_kwargs: Final[Any] = recipe_kwargs

        self.cake_baking_method: BakingMethod = cake_baking_method

        self.result: Any = None

        self.is_baked: bool = False

        self.name: str = ""

        if not self.cake_baking_method:
            self.cake_baking_method = determine_baking_method(self.recipe)
        else:
            check_baking_method(self.recipe, cake_baking_method)

        if self.cake_baking_method == BakingMethod.BAKE_NO_BAKE:
            self.result = self.recipe
            self.is_baked = True

        self.__name__: Final = getattr(self.recipe, "__name__", None) or self.__call__.__name__
        self.__code__: Final = getattr(self.recipe, "__code__", None) or self.__call__.__code__
        self.__defaults__: Final = (
            getattr(self.recipe, "__defaults__", None) or self.__call__.__defaults__
        )
        self.__kwdefaults__: Final = (
            getattr(self.recipe, "__kwdefaults__", None) or self.__call__.__kwdefaults__
        )
        self.__annotations__: Final = (
            getattr(self.recipe, "__annotations__", None) or self.__call__.__annotations__
        )
        self._is_coroutine: Final = getattr(self.recipe, "_is_coroutine", False)

    def __repr__(self) -> str:
        """Repr."""
        name: str = self.name or "<anon>"
        return f"Cake '{name}'"

    def __copy__(self) -> "Ingredients":
        """Copy all ingredients and technologies."""
        ingr_copy: Ingredients = Ingredients(
            self.recipe,
            *list(self.recipe_args),
            cake_baking_method=self.cake_baking_method,
            **dict(self.recipe_kwargs),
        )
        ingr_copy.name = self.name
        return ingr_copy

    def __deepcopy__(self, memo: Any) -> "Ingredients":
        """Deep copy all ingredients and technologies."""
        ingr_copy: Ingredients = Ingredients(
            self.recipe,
            *deepcopy(self.recipe_args),
            cake_baking_method=self.cake_baking_method,
            **deepcopy(self.recipe_kwargs),
        )
        ingr_copy.name = self.name
        return ingr_copy

    def __call__(self) -> Any:
        """Just return result."""
        return self.result

    async def bake(self) -> Any:
        """Bake it all."""

        if self.is_baked:
            return self.result

        for recipe in flatten([self.recipe_args, self.recipe_kwargs, self.recipe]):
            if is_cake(recipe):
                await bake(recipe)

        recipe = self.recipe
        if is_cake_or_piece(recipe):
            recipe = self.recipe()

        if not self.cake_baking_method:
            self.cake_baking_method = determine_baking_method(recipe)

        if self.cake_baking_method == BakingMethod.BAKE_FROM_BUILTIN:
            self.result = replace_cakes(self.recipe)

        elif self.cake_baking_method == BakingMethod.BAKE_FROM_CALL:
            self.result = recipe(
                *replace_cakes(self.recipe_args),
                **replace_cakes(self.recipe_kwargs),
            )

        elif self.cake_baking_method == BakingMethod.BAKE_FROM_CM:
            self.result = recipe.__enter__()

        elif self.cake_baking_method == BakingMethod.BAKE_FROM_ACM:
            self.result = await recipe.__aenter__()

        elif self.cake_baking_method == BakingMethod.BAKE_FROM_CORO_FUNC:
            self.result = await recipe(
                *replace_cakes(self.recipe_args),
                **replace_cakes(self.recipe_kwargs),
            )

        elif self.cake_baking_method == BakingMethod.BAKE_FROM_AWAITABLE:
            self.result = await recipe

        elif self.cake_baking_method == BakingMethod.BAKE_NO_BAKE:
            self.result = recipe

        else:
            raise ValueError(
                f"{self}: Unknown baking method '{self.cake_baking_method}' "
                f"for recipe {self.recipe}"
            )

        logger.debug(f"{self} is baked [{self.cake_baking_method.name}]")
        self.is_baked = True
        return self.result

    async def unbake(
        self,
        exc_type: Optional[type] = None,
        exc_value: Optional[Exception] = None,
        traceback: Optional[Any] = None,
    ) -> None:
        """Unbake cake."""

        # Unbake anonymous recipes even if not self.is_baked
        # Save recipe called value (recipe())
        # because it will be impossible to do it
        # after recipe unbaked
        recipe: Any = self.recipe

        is_cake_and_baked: bool = is_cake(recipe) and is_baked(recipe)
        is_poc_and_baked: bool = is_piece_of_cake(recipe) and is_baked(recipe.cake)

        if is_cake_and_baked or is_poc_and_baked:
            recipe = recipe()

        _recipe: Any
        for _recipe in flatten([self.recipe, self.recipe_args, self.recipe_kwargs]):
            if is_cake(_recipe) and not cake_name(_recipe):
                # unbake anonymous recipes only
                await unbake(_recipe, exc_type, exc_value, traceback)

        if not self.is_baked:
            return

        # All cakes and piece_of_cakes should already be unbaked
        # at this moment
        if not is_cake_or_piece(recipe):
            if self.cake_baking_method == BakingMethod.BAKE_FROM_CM:
                recipe.__exit__(exc_type, exc_value, traceback)

            elif self.cake_baking_method == BakingMethod.BAKE_FROM_ACM:
                await recipe.__aexit__(exc_type, exc_value, traceback)

        logger.debug(f"{self} is unbaked")

        self.is_baked = False
