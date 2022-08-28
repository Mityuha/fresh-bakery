"""Piece of any cake."""

__all__ = [
    "PieceAttr",
    "PieceOfCake",
    "PieceSubs",
    "PieceType",
]

from typing import Any, List

from typing_extensions import Final

from .stuff import Cakeable, FictionalPiece, is_cake


class PieceType:
    """Piece type."""

    def __init__(self, mark: Any):
        self.mark: Any = mark


class PieceAttr(PieceType):
    """Piece attribute."""


class PieceSubs(PieceType):
    """Piece subscription."""


def copy_piece_of_cake(to_copy: "PieceOfCake", mark: PieceType) -> "PieceOfCake":
    """Copy piece_of_cake with mark."""
    piece_copy: PieceOfCake = PieceOfCake(to_copy.cake)
    piece_copy.pieces.extend([*to_copy.pieces, mark])
    return piece_copy


class PieceOfCake(FictionalPiece):
    """Any piece of your any cake."""

    def __init__(self, cake: Cakeable[Any]):
        self.cake: Final[Cakeable[Any]] = cake
        self.pieces: Final[List[PieceType]] = []

    def __repr__(self) -> str:
        res: str = str(self.cake)
        for piece in self.pieces:
            piece_repr: str = f".{piece.mark}"
            if isinstance(piece, PieceSubs):
                piece_repr = f"[{piece.mark}]"
            res += piece_repr

        return res

    def __iter__(self) -> None:
        raise ValueError("Piece of cake is not iterable")

    def __getattr__(self, mark: Any) -> "PieceOfCake":
        """Remember all marks were done."""
        return copy_piece_of_cake(self, PieceAttr(mark))

    def __getitem__(self, mark: Any) -> "PieceOfCake":
        """Remember all subscriptions."""
        return copy_piece_of_cake(self, PieceSubs(mark))

    def __call__(self, *_args: Any, **_kwargs: Any) -> Any:
        """It's time to cut a piece from cake.
        Get dummy *args and **kwargs to highlight
        `Cake is not baked` errors.
        Example:
        ```code
            database: Cake
            await database.write_values([1,2,3,4,5], table="some_table")
            # Without dummy args some strange error occured:
            # `PieceOfCake.__call__() takes 1 positional argument but ... were given`.
        ```
        """

        cake: Cakeable[Any] = self.cake
        if is_cake(cake):
            cake = cake()

        for piece in self.pieces:
            mark: Any = piece.mark
            if mark.__class__ is self.__class__:
                mark = mark()

            if isinstance(piece, PieceAttr):
                cake = getattr(cake, mark)
            elif isinstance(piece, PieceSubs):
                cake = cake[mark]  # type: ignore
            else:
                raise ValueError(f"Unknown piece '{piece}' of cake '{self.cake}'")

        if is_cake(cake):
            cake = cake()
        return cake
