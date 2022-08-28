"""Some utils."""

import sys
from typing import Any


if sys.version_info < (3, 6):
    raise RuntimeError("Incompatible version")

if sys.version_info >= (3, 10):
    from contextlib import aclosing, asynccontextmanager
else:
    if sys.version_info >= (3, 7):
        from contextlib import asynccontextmanager
    else:
        from async_generator import asynccontextmanager

    @asynccontextmanager  # type: ignore
    async def aclosing(thing: Any) -> Any:
        """Python <3.10."""
        try:
            yield thing
        finally:
            await thing.aclose()
