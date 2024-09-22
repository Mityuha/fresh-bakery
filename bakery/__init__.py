"""Bakery house."""

from __future__ import annotations

from .stuff import BakeryLogger, DefaultLogger

logger: BakeryLogger | None = DefaultLogger()

# ruff: noqa: E402
from .bakery import *
from .baking import *
from .cake import *
from .piece_of_cake import *
from .stuff import *

# ruff: noqa: F405, PLE0604
__all__ = [
    *bakery.__all__,  # type: ignore[name-defined]
    *baking.__all__,  # type: ignore[name-defined]
    *cake.__all__,  # type: ignore[name-defined]
    *piece_of_cake.__all__,  # type: ignore[name-defined]
    *stuff.__all__,  # type: ignore[name-defined]
]
