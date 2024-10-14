"""DI Bakery.

Opened around the clock.
"""

from __future__ import annotations

__all__ = ["Bakery"]

from typing import Any, AsyncContextManager, ContextManager, Protocol, TypeVar

from .baking import BakingMethod
from .cake import Cake
from .stuff import _LOGGER as logger  # noqa: N811
from .stuff import is_cake

T = TypeVar("T", bound="Bakery")


class Cakeable(Protocol, AsyncContextManager):
    def __set_name__(self, _: Any, name: str) -> None: ...
    @property
    def __cake_name__(self) -> str: ...
    @property
    def __cake_undefined__(self) -> bool: ...
    def __cake_replace__(
        self,
        _cake_recipe: Any,
        *_cake_recipe_args: Any,
        _cake_baking_method: BakingMethod,
        **_cake_recipe_kwargs: Any,
    ) -> ContextManager[Cakeable]: ...


def replace_cakes(cakes: dict[str, ContextManager]) -> None:
    for replacement in cakes.values():
        replacement.__enter__()


def unreplace_cakes(cakes: dict[str, ContextManager]) -> None:
    for replacement in reversed(cakes.values()):
        replacement.__exit__(None, None, None)

    cakes.clear()


class Bakery:
    """Your bakery."""

    __bakery_visitors__: int
    __bakery_items__: dict[str, Cakeable]
    __bakery_replaced_cakes__: dict[str, ContextManager]

    def __init__(self, **kwargs: Any) -> None:
        cls = type(self)
        if cls.__bakery_visitors__ and kwargs:
            msg = (
                f"{cls.__qualname__} initialized multiple times with keyword arguments. "
                "Such behaviour is discouraging and doesn't make sense. "
                f"Use '{cls.__qualname__}()' instead"
            )
            raise TypeError(msg)

        for item_name, item_value in kwargs.items():
            if item_name not in cls.__bakery_items__:
                msg = f"{cls.__qualname__} got an unexpected keyword argument '{item_name}'"
                raise TypeError(msg)

            if item_name in cls.__bakery_replaced_cakes__:
                msg = (
                    f"{cls.__qualname__} initialized multiple times with keyword argument: "
                    f"'{item_name}'"
                )
                raise TypeError(msg)

            cake_recipe: Any = item_value
            cake_baking_method = BakingMethod.BAKE_NO_BAKE
            recipe_args: tuple = ()
            recipe_kwargs: dict = {}
            if is_cake(item_value):
                cake_recipe = item_value.__cake_recipe__
                recipe_args = item_value.__cake_recipe_args__
                recipe_kwargs = item_value.__cake_recipe_kwargs__
                cake_baking_method = item_value.__cake_baking_method__

            cls.__bakery_replaced_cakes__[item_name] = cls.__bakery_items__[
                item_name
            ].__cake_replace__(
                cake_recipe,
                *recipe_args,
                **recipe_kwargs,
                _cake_baking_method=cake_baking_method,
            )

    async def __aenter__(self: T) -> T:
        return await type(self).aopen()

    async def __aexit__(self, *_args: object) -> None:
        return await type(self).aclose()

    def __getattribute__(self, attr: str) -> Any:
        """If getattr(cls, attr) is cake, call it and return."""
        value: Any = super().__getattribute__(attr)
        if is_cake(value):
            return value()
        return value

    def __init_subclass__(cls, **kwargs: Any) -> None:
        """Initialize bakery subclass."""
        bakery_items: dict[str, Cakeable] = {}
        # Do filter __dict__, because iterating
        # over __annotations__ forces to annotate
        # every cake
        cake_name: str
        _cake: Cakeable
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
        cls.__bakery_replaced_cakes__ = {}

    @classmethod
    async def aopen(cls: type[T]) -> T:
        if cls.__bakery_visitors__:
            cls.__bakery_visitors__ += 1
            # no concurrency yet (like aopen/aopen/aopen)
            # anyio lock required (on demand)
            return cls()

        replace_cakes(cls.__bakery_replaced_cakes__)

        missed_args: list[str] = [
            cake.__cake_name__ for cake in cls.__bakery_items__.values() if cake.__cake_undefined__
        ]
        if missed_args:
            msg = (
                f"{cls.__qualname__}.__init__() missing 1 required keyword-only argument: "
                f"'{missed_args[0]}'"
            )
            if len(missed_args) > 1:
                formatted_args: str = (
                    ", ".join(f"'{arg_name}'" for arg_name in missed_args[:-1])
                    + " and "
                    + f"'{missed_args[-1]}'"
                )
                msg = (
                    f"{cls.__qualname__}.__init__() missing {len(missed_args)} required "
                    f"keyword-only arguments: {formatted_args}"
                )

            logger.error(msg)
            unreplace_cakes(cls.__bakery_replaced_cakes__)
            raise TypeError(msg)

        cls.__bakery_visitors__ += 1
        # let's bake all your cakes
        cake: Cakeable | None = None
        try:
            for cake in cls.__bakery_items__.values():
                await cake.__aenter__()
        except (Exception, BaseException) as exc:
            logger.error(f"{cake} cannot be baked: {exc}")
            await cls.aclose()
            raise exc from None

        logger.debug(f"Bakery '{cls.__qualname__}' is opened. Welcome!")
        return cls()

    @classmethod
    async def aclose(
        cls,
        exc_type: type | None = None,
        exc_value: Exception | None = None,
        traceback: Any | None = None,
    ) -> None:
        cls.__bakery_visitors__ -= 1

        if cls.__bakery_visitors__ > 0:
            logger.debug(
                f"Bakery '{cls.__qualname__}' is working till the last visitor "
                f"({cls.__bakery_visitors__} left)!"
            )
            return

        exceptions: list[Exception | BaseException] = []
        cake: Cakeable
        for cake in reversed(  # it's important to unbake in reverse order
            # dict views are reversible since 3.8
            # https://docs.python.org/3/library/stdtypes.html#dictionary-view-objects
            cls.__bakery_items__.values(),
        ):
            try:
                await cake.__aexit__(exc_type, exc_value, traceback)
            except (Exception, BaseException) as exc:  # noqa: PERF203
                exceptions.append(exc)

        unreplace_cakes(cls.__bakery_replaced_cakes__)

        logger.debug(f"Bakery '{cls.__qualname__}' is closed. Goodbye!")

        if exceptions:
            # For now raise the first exception occurred.
            # Use trio MultiError (inception) on demand
            # https://github.com/python-trio/trio/blob/v0.21.0/trio/_core/_multierror.py#L154
            # or use exception groups (python 3.11)
            # https://peps.python.org/pep-0654/
            raise exceptions[0]
