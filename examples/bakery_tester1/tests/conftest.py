"""Conftest."""
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Optional

import pytest
from fastapi import APIRouter, FastAPI
from httpx import AsyncClient


pytest_plugins = ["bakery.testbakery"]


@pytest.fixture
def test_client():
    """Test fastapi client."""

    @asynccontextmanager
    async def client(
        routers: list[APIRouter], dependencies: Optional[dict] = None
    ) -> AsyncGenerator:
        app = FastAPI()
        for router in routers:
            app.include_router(router)
        client = AsyncClient(base_url="https://asd.ru", app=app)
        dependencies = dependencies or {}
        for key, value in dependencies.items():
            app.dependency_overrides[key] = value
        yield client
        await client.aclose()

    return client
