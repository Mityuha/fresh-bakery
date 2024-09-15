"""Cake.

Book, recipes, etc.
"""

from __future__ import annotations
from copy import deepcopy
from typing import (
    Any,
    AsyncContextManager,
    Awaitable,
    Callable,
    ContextManager,
    Optional,
    Set,
    TypeVar,
    cast,
    overload,
)

from typing_extensions import Final, ParamSpec

from .baking import check_baking_method, determine_baking_method
from .piece_of_cake import PieceOfCake
from .stuff import _LOGGER as logger
from .stuff import (
    BakingMethod,
    Cakeable,
    CakeRecipe,
    IngredientsProto,
    assert_baked,
    cake_ingredients,
    cake_name,
    flatten,
    is_baked,
    is_cake,
    is_cake_or_piece,
    is_piece_of_cake,
    replace_cakes,
)


__all__ = ["Cake", "Pastry", "Shape", "hand_made"]


class Pastry(CakeRecipe):
    """Pastry is a public cake interface with almost zero name collision.

    Your item ingredients and cooking method stored here.
    """

    __CAKE_ATTRIBUTE_ERROR_NAMES__: Final[Set[str]] = {
        "func",  # partial
        "__wrapped__",  # functools special attribute
    }

    def __init__(
        self,
        recipe: Any,
        *recipe_args: Any,
        cake_baking_method: BakingMethod = BakingMethod.BAKE_AUTO,
        **recipe_kwargs: Any,
    ):
        # self.__ingredients: Final[Ingredients] = ingredients
        # self.__name__: Final = ingredients.__name__
        # self.__code__: Final = ingredients.__code__
        # self.__defaults__: Final = ingredients.__defaults__
        # self.__kwdefaults__: Final = ingredients.__kwdefaults__
        # self.__annotations__: Final = ingredients.__annotations__
        # self._is_coroutine: Final = ingredients._is_coroutine
        self.recipe: Final[Any] = recipe
        self.recipe_args: Final[Any] = recipe_args
        self.recipe_kwargs: Final[Any] = recipe_kwargs

        self.cake_baking_method: BakingMethod = cake_baking_method

        self.result: Any = None

        self.is_baked: bool = False

        if not self.cake_baking_method:
            self.cake_baking_method = determine_baking_method(self.recipe)
        else:
            check_baking_method(self.recipe, cake_baking_method)

        if self.cake_baking_method == BakingMethod.BAKE_NO_BAKE:
            self.result = self.recipe
            self.is_baked = True

        # self.__name__: Final = getattr(self.recipe, "__name__", None) or self.__call__.__name__
        # self.__code__: Final = getattr(self.recipe, "__code__", None) or self.__call__.__code__
        # self.__defaults__: Final = (
        #     getattr(self.recipe, "__defaults__", None) or self.__call__.__defaults__
        # )
        # self.__kwdefaults__: Final = (
        #     getattr(self.recipe, "__kwdefaults__", None) or self.__call__.__kwdefaults__
        # )
        # self.__annotations__: Final = (
        #     getattr(self.recipe, "__annotations__", None) or self.__call__.__annotations__
        # )
        # self._is_coroutine: Final = getattr(self.recipe, "_is_coroutine", False)
        self.__name = ""

    def __set_name__(self, _: Any, name: str) -> None:
        self.__name = name
        # self.__ingredients.name = name

    def __repr__(self) -> str:
        """Repr."""
        # return self.__ingredients.__repr__()
        name: str = self.__name or "<anon>"
        return f"Cake '{name}'"

    def __copy__(self) -> "Cakeable[Any]":
        """Copy itself with all ingredients and technologies.

        If cake is not baked then such a cake's copy is cake itself.

        'Copy cake' just sounds like 'cupcake'. And I like cupcakes ;)
        """
        if not is_baked(self):
            return self

        # ingr_copy: Ingredients = self.__ingredients.__copy__()
        # return cast(Cakeable[Any], Pastry(ingr_copy))
        ingr_copy = Pastry(
            self.recipe,
            *list(self.recipe_args),
            cake_baking_method=self.cake_baking_method,
            **dict(self.recipe_kwargs),
        )
        ingr_copy._Pastry__name = self.__name
        return ingr_copy

    def __deepcopy__(self, memo: Any) -> "Cakeable[Any]":
        """Deep copy with all ingredients and technologies.

        If cake is not baked then such a cake's deep copy is cake itself.
        """
        if not is_baked(self):
            return self

        # ingr_copy: Ingredients = self.__ingredients.__deepcopy__(memo)
        # return cast(Cakeable[Any], Pastry(ingr_copy))
        ingr_copy = Pastry(
            self.recipe,
            *deepcopy(self.recipe_args),
            cake_baking_method=self.cake_baking_method,
            **deepcopy(self.recipe_kwargs),
        )
        ingr_copy._Pastry__name = self.__name
        return ingr_copy

    def __call__(self) -> Any:
        """Just return whole cake."""
        assert_baked(cast(Cakeable[Any], self))
        return self.result
        # return self.__ingredients()

    def __getattr__(self, piece_name: str) -> PieceOfCake:
        """Cut a piece of cake.

        With __CAKE_ATTRIBUTE_ERROR_NAMES__ you can no longer write
        the things like:
        class MyBakery(Bakery):
            ctrl: Any = Cake(Controller)
            controller_func: Any = Cake(some_func, ctrl.func)  # or __wrapped__

        There is the place where AttribureError exception will occured.
        You can make a simple refactoring:
        class MyBakery(Bakery):
            ctrl: Any = Cake(Controller)
            controller_func: Any = Cake(some_func, Cake(getattr, ctrl, "func"))
        """
        if piece_name in self.__CAKE_ATTRIBUTE_ERROR_NAMES__:
            raise AttributeError(piece_name)
        # explicit __getattr__ call to avoid collisions
        return PieceOfCake(self).__getattr__(piece_name)

    def __getitem__(self, piece_name: Any) -> PieceOfCake:
        """Cut a piece of cake."""
        return PieceOfCake(self).__getitem__(piece_name)

    async def __aenter__(self) -> Any:
        return await self.bake()

    async def __aexit__(
        self,
        exc_type: Optional[type],
        exc_value: Optional[Exception],
        traceback: Optional[Any],
    ) -> None:
        return await self.unbake(exc_type, exc_value, traceback)

    async def bake(self) -> Any:
        """Bake it all."""

        if self.is_baked:
            return self.result

        for recipe in flatten([self.recipe_args, self.recipe_kwargs, self.recipe]):
            if is_cake(recipe):
                await recipe.bake()

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
                await _recipe.unbake(exc_type, exc_value, traceback)

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


T = TypeVar("T")
P = ParamSpec("P")


def hand_made(cake: T, cake_baking_method: BakingMethod) -> T:
    """Hand made cake."""

    if not is_cake(cake):
        cake = Cake(cake)

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
    recipe: Callable[P, Awaitable[T]],
    *recipe_args: P.args,
    **recipe_kwargs: P.kwargs,
) -> T:
    ...


@overload
def Cake(
    recipe: Callable[P, T],
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
        Pastry(recipe, *recipe_args, **recipe_kwargs),
    )


def Shape(*, init: bool = True) -> Any:  # pylint: disable=unused-argument
    return Cake(...)
