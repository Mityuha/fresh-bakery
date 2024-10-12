from typing import Any

from bakery import DefaultLogger


def test_default_logger(capsys: Any) -> None:
    logger = DefaultLogger()
    logger.debug("logging test")
    logger.info("logging test")
    logger.warning("logging test")
    logger.error("logging test")

    captured = capsys.readouterr()

    for exp in (
        "DEBUG | logging test",
        "INFO  | logging test",
        "WARN  | logging test",
        "ERROR | logging test",
    ):
        assert exp in captured.out
