# isort: skip_file
from typing import Any, TypeVar, Literal
from typing_extensions import dataclass_transform, Self

from .stuff import Cakeable
from .cake import __Cake__

T = TypeVar("T", bound=Bakery)  # noqa: PYI001

def no_init_field(
    *,
    init: Literal[False] = False,
) -> Any: ...

@dataclass_transform(kw_only_default=True, field_specifiers=(no_init_field, __Cake__))
class Bakery:
    __bakery_visitors__: int
    __bakery_items__: dict[str, Cakeable[Any]]
    async def __aenter__(self) -> Self: ...
    async def __aexit__(self, *_args: object) -> None: ...
    @classmethod
    async def aopen(cls) -> Self: ...
    @classmethod
    async def aclose(
        cls,
        *_args: Any,
    ) -> None: ...
