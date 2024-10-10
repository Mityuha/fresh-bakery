from __future__ import annotations

__all__ = [
    "BakeryLogger",
    "CakeRecipe",
    "DefaultLogger",
    "_LOGGER",
]

from datetime import datetime
from functools import partial
from typing import Any, Callable, Final, Protocol

import bakery

from .types import CakeRecipe


class BakeryLogger(Protocol):
    """Bakery logger."""

    def debug(self, __message: str, *args: Any, **kwargs: Any) -> None:
        """Debug."""

    def info(self, __message: str, *args: Any, **kwargs: Any) -> None:
        """Info."""

    def warning(self, __message: str, *args: Any, **kwargs: Any) -> None:
        """Warning."""

    def error(self, __message: str, *args: Any, **kwargs: Any) -> None:
        """Error."""


class DummyLogger:
    """Dummy logger."""

    def debug(self, __message: str, *args: Any, **kwargs: Any) -> None:
        """Debug."""

    def info(self, __message: str, *args: Any, **kwargs: Any) -> None:
        """Info."""

    def warning(self, __message: str, *args: Any, **kwargs: Any) -> None:
        """Warning."""

    def error(self, __message: str, *args: Any, **kwargs: Any) -> None:
        """Error."""


class DefaultLogger:
    """Just instead of print function."""

    FUNC_2_LEVEL: Final[dict[str, str]] = {
        "debug": "DEBUG",
        "info": "INFO ",
        "warning": "WARN ",
        "error": "ERROR",
    }

    @staticmethod
    def _log(level: str, message: str) -> None:
        """Log it."""
        print(  # noqa: T201
            f"{datetime.now().isoformat(sep=' ', timespec='milliseconds')} | {level} | {message}"  # noqa: DTZ005
        )

    def __getattr__(self, attr: str) -> Callable[..., Any]:
        """Check and get default logger attribute."""
        if attr not in self.FUNC_2_LEVEL:
            msg = f"Logger has no attribute {attr}. Possible values: {list(self.FUNC_2_LEVEL)}"
            raise AttributeError(
                msg,
            )

        return partial(self._log, self.FUNC_2_LEVEL[attr])


DUMMY_LOGGER: Final[DummyLogger] = DummyLogger()


class LoggerWrapper:
    """Logger wrapper."""

    def __getattr__(self, attr: str) -> Any:
        """Return actual logger method."""
        cur_logger: BakeryLogger = bakery.logger or DUMMY_LOGGER
        return getattr(cur_logger, attr)


_LOGGER: Final[LoggerWrapper] = LoggerWrapper()
