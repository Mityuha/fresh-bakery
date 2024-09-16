"""DI Bakery.

Opened around the clock.
"""

from __future__ import annotations

__all__ = ["Bakery"]

from typing import Any, TypeVar

from .baking import bake, unbake
from .cake import Cake
from .stuff import _LOGGER as logger  # noqa: N811
from .stuff import Cakeable, is_cake

T = TypeVar("T", bound="Bakery")


class Bakery:
    """Your bakery."""

    __bakery_visitors__: int
    __bakery_items__: dict[str, Cakeable[Any]]

    async def __aenter__(self: T) -> T:
        """Open up your real bakery."""
        return await type(self).aopen()

    async def __aexit__(self, *_args: object) -> None:
        """Close up bakery.

        Unbake all cakes.
        """
        return await type(self).aclose()

    def __getattribute__(self, attr: str) -> Any:
        """If getattr(cls, attr) is cake, call it and return."""
        value: Any = super().__getattribute__(attr)
        if is_cake(value):
            return value()
        return value

    def __init_subclass__(cls, **kwargs: Any) -> None:
        """Initialize bakery subclass."""
        bakery_items: dict[str, Cakeable[Any]] = {}
        # Do filter __dict__, because iterating
        # over __annotations__ forces to annotate
        # every cake
        for cake_name, _cake in cls.__dict__.items():
            if cake_name.startswith("__") and cake_name.endswith("__"):
                continue
            cake = _cake
            if not is_cake(cake):
                # wrap value into cake
                cake = Cake(cake)
                setattr(cls, cake_name, cake)
                cake.__set_name__(cls, cake_name)
            bakery_items[cake_name] = cake

        cls.__bakery_items__ = bakery_items
        cls.__bakery_visitors__ = 0

    @classmethod
    async def aopen(cls: type[T]) -> T:
        """Open bakery."""
        if cls.__bakery_visitors__:
            cls.__bakery_visitors__ += 1
            # no concurrency yet (like aopen/aopen/aopen)
            # anyio lock required (on demand)
            return cls()

        cls.__bakery_visitors__ += 1

        # let's bake all your cakes
        cake: Cakeable | None = None
        try:
            for cake in cls.__bakery_items__.values():
                await bake(cake)
        except (Exception, BaseException) as exc:
            logger.error(f"{cake} cannot be baked: {exc}")
            await cls.aclose()
            raise exc from None

        logger.debug(f"Bakery '{cls}' is opened. Welcome!")
        return cls()

    @classmethod
    async def aclose(
        cls,
        exc_type: type | None = None,
        exc_value: Exception | None = None,
        traceback: Any | None = None,
    ) -> None:
        """Close bakery."""
        cls.__bakery_visitors__ -= 1

        if cls.__bakery_visitors__ > 0:
            logger.debug(f"Bakery '{cls}' is working till the last visitor!")
            return

        exceptions: list[Exception | BaseException] = []
        item: Cakeable[Any]
        for item in reversed(  # it's important to unbake in reverse order
            # dict views are reversible since 3.8
            # https://docs.python.org/3/library/stdtypes.html#dictionary-view-objects
            list(cls.__bakery_items__.values()),
        ):
            try:
                await unbake(item, exc_type, exc_value, traceback)
            except (Exception, BaseException) as exc:  # noqa: PERF203
                exceptions.append(exc)

        logger.debug(f"Bakery '{cls}' is closed.")

        if exceptions:
            # For now raise the first exception occurred.
            # Use trio MultiError (inception) on demand
            # https://github.com/python-trio/trio/blob/v0.21.0/trio/_core/_multierror.py#L154
            # or use exception groups (python 3.11)
            # https://peps.python.org/pep-0654/
            raise exceptions[0]
