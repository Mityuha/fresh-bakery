# isort: skip_file
from typing import Any, Dict, Type, TypeVar, Literal
from typing_extensions import dataclass_transform

from .stuff import Cakeable
from .cake import Shape

T = TypeVar('T', bound='Bakery')

def NoInitField(
    *,
    init: Literal[False] = False,
) -> Any: ...
@dataclass_transform(kw_only_default=True, field_specifiers=(NoInitField, Shape))
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
