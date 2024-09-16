"""Some utils."""

import sys
from typing import Any

if sys.version_info >= (3, 10):
    from contextlib import aclosing, asynccontextmanager
else:
    from contextlib import asynccontextmanager

    @asynccontextmanager
    async def aclosing(thing: Any) -> Any:
        """Python <3.10."""
        try:
            yield thing
        finally:
            await thing.aclose()
