"""Test get person."""

from typing import Callable
from unittest.mock import AsyncMock

import pytest
from bakery.testbakery import BakeryMock

from test_app.bakery import BackgroundTask, MainBakery
from test_app.views.common import router


@pytest.fixture(autouse=True)
async def _patch_background_tasks(bakery_mock: BakeryMock) -> None:
    """Patch background tasks."""
    bakery_mock.background_task = lambda: None


async def test_get_person_1(
    test_client: Callable,
    bakery_mock: BakeryMock,
):
    """Test person 1."""

    _common: dict = {
        "first_name": "name",
        "second_name": "sname",
        "age": 12,
    }

    person: dict = {
        **_common,
        "id": 2,
    }

    # pylint: disable=protected-access
    bakery_mock._connection = lambda *_args, **_kwargs: AsyncMock(
        **{"fetch_one.return_value": person}
    )

    async with test_client([router]) as client, bakery_mock(MainBakery):
        resp = await client.get("/person/2")

    assert resp.status_code == 200
    assert resp.json() == {**_common, "person_id": person["id"]}
    assert not BackgroundTask.CALL_COUNT


async def test_get_person_2(
    test_client: Callable,
    bakery_mock: BakeryMock,
):
    """Test person 2."""

    # pylint: disable=protected-access
    bakery_mock._connection = lambda *_args, **_kwargs: AsyncMock(
        **{"fetch_one.return_value": None}
    )

    async with test_client([router]) as client, bakery_mock(MainBakery):
        resp = await client.get("/person/2")

    assert resp.status_code == 404
    assert resp.json() == {}
    assert not BackgroundTask.CALL_COUNT
