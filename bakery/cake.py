"""Cake.

Book, recipes, etc.
"""

from __future__ import annotations

__all__ = ["Cake", "Pastry", "__Cake__", "hand_made"]

from contextlib import contextmanager
from copy import deepcopy
from typing import (
    TYPE_CHECKING,
    Any,
    AsyncContextManager,
    Awaitable,
    Callable,
    ContextManager,
    Final,
    Generic,
    Iterator,
    Literal,
    TypeVar,
    cast,
    overload,
)

from typing_extensions import ParamSpec, Self

from .baking import BakingMethod, bake_recipe, check_baking_method, determine_baking_method
from .piece_of_cake import PieceOfCake
from .stuff import _LOGGER as logger  # noqa: N811
from .stuff import (
    CakeRecipe,
    assert_baked,
    flatten,
    is_baked,
    is_cake,
    is_cake_or_piece,
    is_piece_of_cake,
    recipe_format,
)
from .stuff.types import UNDEFINED

if TYPE_CHECKING:
    from types import TracebackType


R = TypeVar("R")


class Pastry(CakeRecipe, Generic[R]):
    """Pastry is a public cake interface with almost zero name collision.

    Your item ingredients and cooking method stored here.
    """

    __CAKE_ATTRIBUTE_ERROR_NAMES__: Final[set[str]] = {
        "func",  # partial
        "__wrapped__",  # functools special attribute
    }

    def __init__(
        self,
        _cake_recipe: R,
        *_cake_recipe_args: Any,
        _cake_baking_method: BakingMethod = BakingMethod.BAKE_AUTO,
        _cake_name: str = "",
        **_cake_recipe_kwargs: Any,
    ) -> None:
        self.__cake_recipe: Final = _cake_recipe
        self.__cake_recipe_args: Final = _cake_recipe_args
        self.__cake_recipe_kwargs: Final = _cake_recipe_kwargs

        self.__cake_baking_method: BakingMethod = _cake_baking_method
        self.__cake_result: Any = None
        self.__cake_is_baked: bool = False
        self.__cake_name: str = _cake_name

        self.__cake_replaced: Pastry | None = None

        if not self.__cake_baking_method:
            self.__cake_baking_method = determine_baking_method(self.__cake_recipe)
        else:
            check_baking_method(self.__cake_recipe, _cake_baking_method)

        if self.__cake_baking_method == BakingMethod.BAKE_NO_BAKE:
            self.__cake_result = self.__cake_recipe
            self.__cake_is_baked = True

    def __set_name__(self, _: Any, name: str) -> None:
        self.__cake_name = name

    @property
    def __cake_name__(self) -> str:
        return self.__cake_name

    @property
    def __cake_anon__(self) -> bool:
        return not self.__cake_name

    @property
    def __cake_baked__(self) -> bool:
        return self.__cake_is_baked

    @property
    def __cake_baking_method__(self) -> BakingMethod:
        return self.__cake_baking_method

    @property
    def __cake_recipe__(self) -> R:
        return self.__cake_recipe

    @property
    def __cake_recipe_args__(self) -> tuple:
        return self.__cake_recipe_args

    @property
    def __cake_recipe_kwargs__(self) -> dict:
        return self.__cake_recipe_kwargs

    @property
    def __cake_undefined__(self) -> bool:
        return self.__cake_recipe is UNDEFINED

    @contextmanager
    def __cake_replace__(
        self,
        _cake_recipe: Any,
        *_cake_recipe_args: Any,
        _cake_baking_method: BakingMethod = BakingMethod.BAKE_AUTO,
        **_cake_recipe_kwargs: Any,
    ) -> Iterator[Self]:
        if self.__cake_replaced:
            msg = f"Cannot replace cake '{self}' that's already replaced"
            raise TypeError(msg)

        if self.__cake_is_baked and self.__cake_baking_method != BakingMethod.BAKE_NO_BAKE:
            msg = f"Cannot replace cake '{self}' that's already baked."
            raise TypeError(msg)

        is_replacement: bool = self.__cake_recipe is not UNDEFINED
        orig_recipe_fmt: str = recipe_format(self.__cake_recipe, self.__cake_baking_method)

        self.__cake_replaced = self.__copy__()
        self.__cake_recipe = _cake_recipe  # type: ignore[misc]
        self.__cake_recipe_args = _cake_recipe_args  # type: ignore[misc]
        self.__cake_recipe_kwargs = _cake_recipe_kwargs  # type: ignore[misc]
        self.__cake_baking_method = _cake_baking_method
        self.__cake_is_baked = False
        self.__cake_result = None

        new_recipe_fmt: str = recipe_format(self.__cake_recipe, self.__cake_baking_method)

        if is_replacement:
            logger.debug(f"{self} was replaced: {orig_recipe_fmt} ==> {new_recipe_fmt}")
        try:
            yield self
        finally:
            self.__cake_recipe = self.__cake_replaced.__cake_recipe__  # type: ignore[misc]
            self.__cake_recipe_args = self.__cake_replaced.__cake_recipe_args__  # type: ignore[misc]
            self.__cake_recipe_kwargs = self.__cake_replaced.__cake_recipe_kwargs__  # type: ignore[misc]
            self.__cake_baking_method = self.__cake_replaced.__cake_baking_method__
            self.__cake_replaced = None
            if is_replacement:
                logger.debug(f"{self} was restored: {orig_recipe_fmt} <== {new_recipe_fmt}")

        if self.__cake_is_baked:
            msg = (
                f"'{self}' replacement was rollbacked but cake is still baked. "
                "Unbake the cake first!"
            )
            raise TypeError(msg)

    def __repr__(self) -> str:
        name: str = self.__cake_name or "<anon>"
        return f"Cake '{name}'"

    def __copy__(self) -> Pastry[R]:
        """Copy itself with all ingredients and technologies.

        'Copy cake' just sounds like 'cupcake'. And I like cupcakes ;)
        """
        return Pastry(
            self.__cake_recipe,
            *list(self.__cake_recipe_args),
            _cake_baking_method=self.__cake_baking_method,
            _cake_name=self.__cake_name,
            **dict(self.__cake_recipe_kwargs),
        )

    def __deepcopy__(self, memo: Any) -> Pastry[R]:
        """Deep copy with all ingredients and technologies."""
        return Pastry(
            self.__cake_recipe,
            *deepcopy(self.__cake_recipe_args),
            _cake_baking_method=self.__cake_baking_method,
            _cake_name=self.__cake_name,
            **deepcopy(self.__cake_recipe_kwargs),
        )

    def __call__(self) -> Any:
        assert_baked(self)
        return self.__cake_result

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
        return PieceOfCake(self).__getitem__(piece_name)

    async def __aenter__(self) -> Any:
        if self.__cake_is_baked:
            return self.__cake_result

        for recipe in flatten(
            [self.__cake_recipe_args, self.__cake_recipe_kwargs, self.__cake_recipe]
        ):
            if is_cake(recipe):
                await recipe.__aenter__()

        recipe = self.__cake_recipe
        if is_cake_or_piece(recipe):
            recipe = recipe()

        if not self.__cake_baking_method:
            self.__cake_baking_method = determine_baking_method(recipe)

        self.__cake_result = await bake_recipe(
            recipe,
            recipe_args=self.__cake_recipe_args,
            recipe_kwargs=self.__cake_recipe_kwargs,
            baking_method=self.__cake_baking_method,
            cake_name=str(self),
        )

        logger.debug(f"{self} is baked [{self.__cake_baking_method.name}]")
        self.__cake_is_baked = True
        return self.__cake_result

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        """Unbake anonymous recipes even if not self.__cake_is_baked.

        Save recipe called value (recipe())
        because it will be impossible to do it after recipe unbaked.
        """
        recipe: Any = self.__cake_recipe

        is_cake_and_baked: bool = is_cake(recipe) and is_baked(recipe)
        is_poc_and_baked: bool = is_piece_of_cake(recipe) and is_baked(recipe.cake)

        if is_cake_and_baked or is_poc_and_baked:
            recipe = recipe()

        _recipe: Any
        for _recipe in flatten(
            [self.__cake_recipe, self.__cake_recipe_args, self.__cake_recipe_kwargs]
        ):
            if is_cake(_recipe) and _recipe.__cake_anon__:
                # unbake anonymous recipes only
                await _recipe.__aexit__(exc_type, exc_value, traceback)

        if not self.__cake_is_baked:
            return

        # All cakes and piece_of_cakes should already be unbaked
        # at this moment
        if not is_cake_or_piece(recipe):
            if self.__cake_baking_method == BakingMethod.BAKE_FROM_CM:
                recipe.__exit__(exc_type, exc_value, traceback)

            elif self.__cake_baking_method == BakingMethod.BAKE_FROM_ACM:
                await recipe.__aexit__(exc_type, exc_value, traceback)

        logger.debug(f"{self} is unbaked")

        self.__cake_is_baked = False


T = TypeVar("T")
P = ParamSpec("P")


def hand_made(cake: T, cake_baking_method: BakingMethod) -> T:
    """Hand made cake."""
    if not is_cake(cake):
        cake = Cake(cake)

    cake._Pastry__cake_baking_method = cake_baking_method  # type: ignore[attr-defined]
    return cake


@overload
def Cake(recipe: Awaitable[T]) -> T: ...


@overload
def Cake(recipe: AsyncContextManager[T]) -> T: ...


@overload
def Cake(recipe: ContextManager[T]) -> T: ...


@overload
def Cake(
    recipe: Callable[P, Awaitable[T]],
    *recipe_args: P.args,
    **recipe_kwargs: P.kwargs,
) -> T: ...


@overload
def Cake(
    recipe: Callable[P, T],
    *recipe_args: P.args,
    **recipe_kwargs: P.kwargs,
) -> T: ...


@overload
def Cake(recipe: T) -> T: ...


def Cake(  # waiting for issue to close  # noqa: N802
    # https://github.com/python/mypy/issues/11004
    recipe: T,
    *recipe_args: Any,
    **recipe_kwargs: Any,
) -> T:
    return cast(
        T,
        Pastry(recipe, *recipe_args, **recipe_kwargs),
    )


def __Cake__(*, init: Literal[True] = True) -> Any:  # noqa: N802, N807, ARG001
    return Cake(UNDEFINED)
