from __future__ import annotations

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

from typing import (
    TYPE_CHECKING,
    Any,
)

from .types import Cakeable, CakeRecipe, FictionalPiece

if TYPE_CHECKING:
    from enum import IntEnum


def is_cake(value: Any) -> bool:
    return isinstance(value, CakeRecipe)


def is_piece_of_cake(value: Any) -> bool:
    return isinstance(value, FictionalPiece)


def is_cake_or_piece(value: Any) -> bool:
    return is_cake(value) or is_piece_of_cake(value)


def cake_name(cake: Cakeable) -> str:
    return cake.__cake_name__


def anon_cake(cake: Cakeable) -> bool:
    return cake.__cake_anon__


def is_baked(cake: Cakeable) -> bool:
    return cake.__cake_baked__


def assert_baked(cake: Cakeable[Any]) -> None:
    if not is_baked(cake):
        msg = f"{cake} is not baked. Just bake it!"
        raise ValueError(msg)


def cake_recipe(cake: Cakeable) -> Any:
    return cake.__cake_recipe__


def cake_recipe_args(cake: Cakeable) -> tuple:
    return cake.__cake_recipe_args__


def cake_recipe_kwargs(cake: Cakeable) -> dict:
    return cake.__cake_recipe_kwargs__


def cake_baking_method(cake: Cakeable) -> IntEnum:
    return cake.__cake_baking_method__
