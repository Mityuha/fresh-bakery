"""Cake.

Book, recipes, etc.
"""

__all__ = ["Cake", "Pastry", "hand_made"]

from typing import (
    Any,
    AsyncContextManager,
    Awaitable,
    Callable,
    ContextManager,
    Optional,
    TypeVar,
    cast,
    overload,
)

from typing_extensions import Final, ParamSpec

from .baking import Ingredients
from .piece_of_cake import PieceOfCake
from .stuff import (
    BakingMethod,
    Cakeable,
    CakeRecipe,
    IngredientsProto,
    assert_baked,
    cake_ingredients,
)


class Pastry(CakeRecipe):
    """Pastry for your cake.

    Your item ingredients and cooking method stored here.
    """

    def __init__(
        self,
        ingredients: Ingredients,
    ):
        self.__ingredients: Final[Ingredients] = ingredients

    def __set_name__(self, _: Any, name: str) -> None:
        self.__ingredients.name = name

    def __repr__(self) -> str:
        """Repr."""
        return self.__ingredients.__repr__()

    def __copy__(self) -> "Cakeable[Any]":
        """Copy itself with all ingredients and technologies.

        'Copy cake' just sounds like 'cupcake'. And I like cupcakes ;)
        """
        assert_baked(cast(Cakeable[Any], self))  # we only copy proven recipes!
        ingr_copy: Ingredients = self.__ingredients.__copy__()
        return cast(Cakeable[Any], Pastry(ingr_copy))

    def __call__(self) -> Any:
        """Just return whole cake."""
        assert_baked(cast(Cakeable[Any], self))
        return self.__ingredients()

    def __getattr__(self, piece_name: str) -> PieceOfCake:
        """Cut a piece of cake."""
        # explicit __getattr__ call to avoid collisions
        return PieceOfCake(self).__getattr__(piece_name)

    def __getitem__(self, piece_name: Any) -> PieceOfCake:
        """Cut a piece of cake."""
        return PieceOfCake(self).__getitem__(piece_name)

    async def __aenter__(self) -> Any:
        return await self.__ingredients.bake()

    async def __aexit__(
        self,
        exc_type: Optional[type],
        exc_value: Optional[Exception],
        traceback: Optional[Any],
    ) -> None:
        return await self.__ingredients.unbake(exc_type, exc_value, traceback)


T = TypeVar("T")
P = ParamSpec("P")


def hand_made(cake: T, cake_baking_method: BakingMethod) -> T:
    """Hand made cake."""

    ingredients: IngredientsProto = cake_ingredients(cast(Cakeable[Any], cake))
    ingredients.cake_baking_method = cake_baking_method
    return cake


# pylint: disable=invalid-name


@overload
def Cake(recipe: Awaitable[T]) -> T:
    ...


@overload
def Cake(recipe: AsyncContextManager[T]) -> T:
    ...


@overload
def Cake(recipe: ContextManager[T]) -> T:
    ...


@overload
def Cake(
    recipe: Callable[P, T],
    *recipe_args: P.args,
    **recipe_kwargs: P.kwargs,
) -> T:
    ...


@overload
def Cake(
    recipe: Callable[P, Awaitable[T]],
    *recipe_args: P.args,
    **recipe_kwargs: P.kwargs,
) -> T:
    ...


@overload
def Cake(recipe: T) -> T:
    ...


def Cake(  # waiting for issue to close
    # https://github.com/python/mypy/issues/11004
    recipe: T,
    *recipe_args: Any,
    **recipe_kwargs: Any,
) -> T:
    """Cake as Cake =)."""
    return cast(
        T,
        Pastry(Ingredients(recipe, *recipe_args, **recipe_kwargs)),
    )
