"""Bakery."""


from bakery import Bakery, Cake
from pydantic import BaseSettings

from .cron.bakery import CapacityBakery, CronBakery


class Settings(BaseSettings):
    """Cron settings."""

    info_fetch_outputs: str = "* * * * * 25"


class MainBakery(Bakery):
    """Main bakery."""

    _config: Settings = Cake(Settings)

    projects: CapacityBakery = Cake(CapacityBakery())

    _capacity_p_cron: CronBakery = Cake(CronBakery())


def tests() -> None:
    """Just for test."""
    settings: Settings = MainBakery._config()
