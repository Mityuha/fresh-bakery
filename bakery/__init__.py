"""Bakery house."""

from typing import Optional

from .stuff import BakeryLogger, DefaultLogger


logger: Optional[BakeryLogger] = DefaultLogger()

from .bakery import *
from .baking import *
from .cake import *
from .piece_of_cake import *
from .stuff import *


__all__ = [
    *bakery.__all__,  # type: ignore # pylint: disable=undefined-variable
    *baking.__all__,  # type: ignore # pylint: disable=undefined-variable
    *cake.__all__,  # type: ignore # pylint: disable=undefined-variable
    *piece_of_cake.__all__,  # type: ignore # pylint: disable=undefined-variable
    *stuff.__all__,  # type: ignore # pylint: disable=undefined-variable
]
