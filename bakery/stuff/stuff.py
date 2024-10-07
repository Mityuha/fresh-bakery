from __future__ import annotations

__all__ = [
    "BUILTIN_TYPES",
    "flatten",
    "is_iterable",
    "is_mapping",
    "replace_cakes",
]

import types
from copy import copy
from typing import (
    Any,
    Final,
    Iterable,
    Iterator,
    Mapping,
)

from typing_extensions import TypeGuard

from .cake_stuff import is_cake_or_piece
from .types import CakeRecipe, FictionalPiece


def is_iterable(
    value: Any,
    ignore_types: tuple[type[Any], ...] = (
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


def flatten(
    items: Iterable[Any] | Mapping[Any, Any],
    ignore_types: tuple[type[Any], ...] = (
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


BUILTIN_TYPES: Final[tuple[Any, ...]] = (
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
