# isort: skip_file
from typing import Any, Dict, Type, TypeVar

from .stuff import Cakeable

T = TypeVar('T', bound='Bakery')

class Bakery:
    __bakery_visitors__: int
    __bakery_items__: Dict[str, Cakeable[Any]]
    async def __aenter__(self: T) -> T: ...
    async def __aexit__(self, *_args: Any) -> None: ...
    @classmethod
    async def aopen(cls: Type[T]) -> T: ...
    @classmethod
    async def aclose(
        cls,
        *_args: Any,
    ) -> None: ...
