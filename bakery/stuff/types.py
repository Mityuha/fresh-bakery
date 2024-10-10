from __future__ import annotations

__all__ = [
    "CakeRecipe",
    "Cakeable",
    "FictionalPiece",
    "is_undefined",
    "recipe_format",
]

from inspect import Signature
from typing import (
    TYPE_CHECKING,
    Any,
    Final,
    Protocol,
    TypeVar,
    final,
)

if TYPE_CHECKING:
    import types
    from enum import IntEnum


class CakeRecipe:
    # for fastapi Depends
    __signature__ = Signature()

    def __call__(self) -> Any:
        raise NotImplementedError


class FictionalPiece:
    # for fastapi Depends
    __signature__ = Signature()

    def __call__(self) -> Any:
        raise NotImplementedError


T_co = TypeVar("T_co", covariant=True)


class PieceProto(Protocol):
    def __getattr__(self, mark: Any) -> PieceProto:
        """some_cake.attribute."""

    def __getitem__(self, mark: Any) -> PieceProto:
        """some_cake["key"]."""

    def __call__(self) -> Any:
        """some_cake()."""


class Cakeable(Protocol[T_co]):
    def __set_name__(self, _: Any, name: str) -> None: ...

    def __call__(self) -> T_co: ...

    def __getattr__(self, piece_name: str) -> PieceProto: ...

    def __getitem__(self, piece_name: Any) -> PieceProto: ...

    @property
    def __cake_name__(self) -> str: ...

    @property
    def __cake_anon__(self) -> bool: ...

    @property
    def __cake_baked__(self) -> bool: ...

    @property
    def __cake_baking_method__(self) -> IntEnum: ...

    @property
    def __cake_recipe__(self) -> Any: ...

    @property
    def __cake_recipe_args__(self) -> tuple: ...

    @property
    def __cake_recipe_kwargs__(self) -> dict: ...

    async def __aenter__(self) -> T_co: ...

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: types.TracebackType | None,
    ) -> None: ...


@final
class _Undefined: ...


UNDEFINED: Final = _Undefined()


def is_undefined(obj: Any) -> bool:
    return obj is UNDEFINED


def recipe_format(recipe: Any, method: IntEnum) -> str:
    fmt: str
    if recipe is UNDEFINED:
        fmt = "__cake__"
    elif hasattr(recipe, "__qualname__"):
        fmt = recipe.__qualname__
    elif hasattr(recipe, "__name__"):
        fmt = recipe.__name__
    elif hasattr(recipe, "__class__"):
        fmt = recipe.__class__.__qualname__
    else:
        fmt = str(recipe)

    return f"{fmt}[{method.name}]"
