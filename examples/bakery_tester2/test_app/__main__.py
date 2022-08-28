"""Entrypoint service file."""

import bakery
from fastapi import FastAPI
from loguru import logger

from .bakery import MainBakery
from .views.common import router as common_router


async def startup() -> None:
    """Global initialization."""

    logger.info("Init resources...")
    bakery.logger = logger
    await MainBakery.aopen()


async def shutdown() -> None:
    """Global shutdown."""

    logger.info("Shutdown resources...")
    await MainBakery.aclose()


APP: FastAPI = FastAPI(
    title="Bakery tester",
    description="Bakery tester service",
    on_startup=[startup],
    on_shutdown=[shutdown],
)


APP.include_router(common_router)
