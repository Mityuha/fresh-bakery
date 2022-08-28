"""Main."""

from fastapi import FastAPI

from .bakery import MainBakery
from .routes.get_info import router as info_router


async def on_startup() -> None:
    """Startup."""

    await MainBakery.aopen()


async def on_shutdown() -> None:
    """Shutdown."""
    await MainBakery.aclose()


APP: FastAPI = FastAPI(on_startup=[on_startup], on_shutdown=[on_shutdown])

APP.include_router(info_router)
