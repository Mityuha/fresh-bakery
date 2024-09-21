from __future__ import annotations

from typing import (
    TYPE_CHECKING,
    Any,
)

from .types import Cakeable, CakeRecipe, FictionalPiece

if TYPE_CHECKING:
    from enum import IntEnum

__all__ = [
    "anon_cake",
    "assert_baked",
    "cake_baking_method",
    "cake_name",
    "cake_recipe",
    "cake_recipe_args",
    "cake_recipe_kwargs",
    "is_baked",
    "is_cake",
    "is_cake_or_piece",
    "is_piece_of_cake",
]


def is_cake(value: Any) -> bool:
    """Is cake."""
    return isinstance(value, CakeRecipe)


def is_piece_of_cake(value: Any) -> bool:
    """Is piece of cake."""
    return isinstance(value, FictionalPiece)


def is_cake_or_piece(value: Any) -> bool:
    """Is cake or piece of cake."""
    return is_cake(value) or is_piece_of_cake(value)


def cake_name(cake: Cakeable[Any]) -> str:
    """Is cake with name."""
    return cake.__cake_name__


def anon_cake(cake: Cakeable) -> bool:
    """Check if anonymous cake."""
    return cake.__cake_anon__


def is_baked(cake: Cakeable[Any]) -> bool:
    """Check if recipe is baked."""
    return cake.__cake_baked__


def assert_baked(cake: Cakeable[Any]) -> None:
    """Check if recipe is baked."""
    if not is_baked(cake):
        msg = f"{cake} is not baked. Just bake it!"
        raise ValueError(msg)


def cake_recipe(cake: Cakeable) -> Any:
    return cake.__cake_recipe__


def cake_recipe_args(cake: Cakeable) -> Any:
    return cake.__cake_recipe_args__


def cake_recipe_kwargs(cake: Cakeable) -> Any:
    return cake.__cake_recipe_kwargs__


def cake_baking_method(cake: Cakeable[Any]) -> IntEnum:
    """Cake baking method."""
    return cake.__cake_baking_method__
