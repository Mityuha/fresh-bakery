# isort: skip_file
from typing import Any, TypeVar

from .stuff import Cakeable

T = TypeVar("T", bound=Bakery)  # noqa: PYI001

class Bakery:
    __bakery_visitors__: int
    __bakery_items__: dict[str, Cakeable[Any]]
    async def __aenter__(self: T) -> T: ...
    async def __aexit__(self, *_args: object) -> None: ...
    @classmethod
    async def aopen(cls: type[T]) -> T: ...
    @classmethod
    async def aclose(
        cls,
        *_args: Any,
    ) -> None: ...
