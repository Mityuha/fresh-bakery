from __future__ import annotations

__all__ = [
    "CakeRecipe",
    "Cakeable",
    "FictionalPiece",
]

from inspect import Signature
from typing import (
    TYPE_CHECKING,
    Any,
    Protocol,
    TypeVar,
)

if TYPE_CHECKING:
    import types


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
    """Piece of cake protocol."""

    def __getattr__(self, mark: Any) -> PieceProto:
        """Getattr."""

    def __getitem__(self, mark: Any) -> PieceProto:
        """Subscription."""

    def __call__(self) -> Any:
        """Get cake."""


class Cakeable(Protocol[T_co]):
    """Cakeable protocol."""

    def __set_name__(self, _: Any, name: str) -> None:
        """Set cakeable name."""

    def __repr__(self) -> str:
        """Repr."""

    def __copy__(self) -> Cakeable[T_co]:
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
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: types.TracebackType | None,
    ) -> None:
        """Unbake cakeable."""
