"""Baking stuff."""

__all__ = [
    "BUILTIN_TYPES",
    "BakeryLogger",
    "BakingMethod",
    "CakeRecipe",
    "Cakeable",
    "DefaultLogger",
    "IngredientsProto",
    "cake_baking_method",
    "cake_ingredients",
    "cake_name",
    "flatten",
    "is_baked",
    "is_cake",
    "is_iterable",
    "is_mapping",
    "is_piece_of_cake",
]

import types
from copy import copy
from datetime import datetime
from enum import IntEnum, auto
from functools import partial
from inspect import Signature
from typing import (
    Any,
    Callable,
    Dict,
    Iterable,
    Iterator,
    Mapping,
    Optional,
    Tuple,
    Type,
    TypeVar,
    Union,
    cast,
)

from typing_extensions import Final, Protocol, TypeGuard

import bakery


class BakingMethod(IntEnum):
    """Baking method."""

    BAKE_AUTO = 0
    BAKE_FROM_CORO_FUNC = auto()
    BAKE_FROM_AWAITABLE = auto()
    BAKE_FROM_ACM = auto()
    BAKE_FROM_CM = auto()
    BAKE_FROM_BUILTIN = auto()
    BAKE_FROM_CALL = auto()
    BAKE_NO_BAKE = auto()


class IngredientsProto(Protocol):
    """Ingredients protocol."""

    recipe: Any
    recipe_args: Any
    recipe_kwargs: Any
    cake_baking_method: BakingMethod
    is_baked: bool
    name: str


class CakeRecipe:
    """Any recipe you want."""

    # for fastapi Depends
    __signature__ = Signature()

    def __call__(self) -> Any:
        """Do something."""
        raise NotImplementedError


class FictionalPiece:
    """Fictional piece of cake."""

    # for fastapi Depends
    __signature__ = Signature()

    def __call__(self) -> Any:
        """Do something."""
        raise NotImplementedError


T_co = TypeVar("T_co", covariant=True)


class PieceProto(Protocol):
    """Piece of cake protocol."""

    def __getattr__(self, mark: Any) -> "PieceProto":
        """Getattr."""

    def __getitem__(self, mark: Any) -> "PieceProto":
        """Subscription."""

    def __call__(self) -> Any:
        """Get cake."""


class Cakeable(Protocol[T_co]):
    """Cakeable protocol."""

    def __set_name__(self, _: Any, name: str) -> None:
        """Set cakeable name."""

    def __repr__(self) -> str:
        """Repr."""

    def __copy__(self) -> "Cakeable[T_co]":
        """Copy cake."""

    def __call__(self) -> T_co:
        """Call cake."""

    def __getattr__(self, piece_name: str) -> PieceProto:
        """Getattr."""

    def __getitem__(self, piece_name: Any) -> PieceProto:
        """Subscription."""

    async def __aenter__(self) -> T_co:
        """Bake cakeable."""

    async def __aexit__(
        self,
        exc_type: Optional[type],
        exc_value: Optional[Exception],
        traceback: Optional[Any],
    ) -> None:
        """Unbake cakeable."""


def is_iterable(
    value: Any,
    ignore_types: Tuple[Type[Any], ...] = (
        str,
        bytes,
        memoryview,
        types.GeneratorType,
        types.AsyncGeneratorType,
        map,
        range,
        zip,
        CakeRecipe,
        FictionalPiece,
    ),
) -> bool:
    """Check if iterable, ignore generator-like by default."""
    return isinstance(value, Iterable) and not isinstance(value, ignore_types)


def is_mapping(value: Any) -> TypeGuard[Mapping[Any, Any]]:
    """Is mapping check."""
    return isinstance(value, Mapping)


def is_cake(value: Any) -> bool:
    """Is cake."""
    return isinstance(value, CakeRecipe)


def is_piece_of_cake(value: Any) -> bool:
    """Is piece of cake."""
    return isinstance(value, FictionalPiece)


def is_cake_or_piece(value: Any) -> bool:
    """Is cake or piece of cake."""
    return is_cake(value) or is_piece_of_cake(value)


def cake_ingredients(cake: Cakeable[Any]) -> IngredientsProto:
    """Cake ingredients."""
    if not is_cake(cake):
        raise ValueError(f"Only cakes are baking in the bakery, not {cake}")
    return cast(IngredientsProto, getattr(cake, "_Pastry__ingredients"))


def cake_name(cake: Cakeable[Any]) -> str:
    """Is cake with name."""
    return cake_ingredients(cake).name


def is_baked(cake: Cakeable[Any]) -> bool:
    """Check if recipe is baked."""
    return cake_ingredients(cake).is_baked


def assert_baked(cake: Cakeable[Any]) -> None:
    """Check if recipe is baked."""
    if not is_baked(cake):
        raise ValueError(f"{cake} is not baked. Just bake it!")


def cake_baking_method(cake: Cakeable[Any]) -> IntEnum:
    """Cake baking method."""
    return cake_ingredients(cake).cake_baking_method


def flatten(
    items: Union[Iterable[Any], Mapping[Any, Any]],
    ignore_types: Tuple[Type[Any], ...] = (
        str,
        bytes,
        memoryview,
        types.GeneratorType,
        types.AsyncGeneratorType,
        map,
        range,
        zip,
        CakeRecipe,
        FictionalPiece,
    ),
) -> Iterator[Any]:
    """Flatten items, except ignored (generator-like)."""
    items = items.items() if is_mapping(items) else items
    for _item in items:
        if is_iterable(_item, ignore_types) or is_mapping(_item):
            yield from flatten(_item)
        else:
            yield _item


def replace_cakes(obj: Any) -> Any:
    """Replace all objects."""

    res: Any

    if is_mapping(obj):
        res = copy(obj)
        for key, value in obj.items():
            _key = replace_cakes(key)
            _value = replace_cakes(value)
            res[_key] = _value

    elif is_iterable(obj):
        res = type(obj)(replace_cakes(item) for item in obj)

    elif is_cake_or_piece(obj):
        res = obj()

    else:
        res = obj

    return res


BUILTIN_TYPES: Final[Tuple[Any, ...]] = (
    bool,
    bytearray,
    bytes,
    classmethod,
    complex,
    dict,
    float,
    frozenset,
    int,
    list,
    map,
    memoryview,
    property,
    range,
    set,
    slice,
    staticmethod,
    str,
    super,
    tuple,
    zip,
    type(None),
    type(Ellipsis),
    types.AsyncGeneratorType,
    types.GeneratorType,
    types.ModuleType,
    types.SimpleNamespace,
)


class BakeryLogger(Protocol):
    """Bakery logger."""

    def debug(self, __message: str, *args: Any, **kwargs: Any) -> None:
        """Debug."""

    def info(self, __message: str, *args: Any, **kwargs: Any) -> None:
        """Info."""

    def warning(self, __message: str, *args: Any, **kwargs: Any) -> None:
        """Warning."""

    def error(self, __message: str, *args: Any, **kwargs: Any) -> None:
        """Error."""


class DummyLogger:
    """Dummy logger."""

    def debug(self, __message: str, *args: Any, **kwargs: Any) -> None:
        """Debug."""

    def info(self, __message: str, *args: Any, **kwargs: Any) -> None:
        """Info."""

    def warning(self, __message: str, *args: Any, **kwargs: Any) -> None:
        """Warning."""

    def error(self, __message: str, *args: Any, **kwargs: Any) -> None:
        """Error."""


class DefaultLogger:
    """Just instead of print function."""

    FUNC_2_LEVEL: Final[Dict[str, str]] = {
        "debug": "DEBUG",
        "info": "INFO ",
        "warning": "WARN ",
        "error": "ERROR",
    }

    @staticmethod
    def _log(level: str, message: str) -> None:
        """Log it."""
        print(
            f"{datetime.now().isoformat(sep=' ', timespec='milliseconds')} | {level} | {message}"
        )

    def __getattr__(self, attr: str) -> Callable[..., Any]:
        if attr not in self.FUNC_2_LEVEL:
            raise AttributeError(
                f"Logger has no attribute {attr}. Possible values: {list(self.FUNC_2_LEVEL)}"
            )

        return partial(self._log, self.FUNC_2_LEVEL[attr])


DUMMY_LOGGER: Final[DummyLogger] = DummyLogger()


class LoggerWrapper:
    """Logger wrapper."""

    def __getattr__(self, attr: str) -> Any:
        """Return actual logger method."""
        cur_logger: BakeryLogger = bakery.logger or DUMMY_LOGGER
        return getattr(cur_logger, attr)


_LOGGER: Final[LoggerWrapper] = LoggerWrapper()
