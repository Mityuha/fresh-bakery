"""Test get person."""

import asyncio
from copy import copy
from typing import Callable

import pytest
from bakery import Cake, Cakeable
from bakery.testbakery import BakeryMock

from test_app.bakery import BackgroundTask, MainBakery
from test_app.views.common import router


@pytest.fixture(scope="module")
def event_loop():
    """Redefine event loop.

    Super UGLY!
    """

    return asyncio.get_event_loop()


@pytest.fixture(scope="module", autouse=True)
async def _truncate_table(module_bakery_mock: BakeryMock) -> None:
    """
    - Open bakery.

    - Truncate table
    - Patch background tasks
    Speed up tests ~x10 times.
    """

    module_bakery_mock.background_task = lambda: None
    await module_bakery_mock.patch(MainBakery)

    conn_cake: Cakeable = copy(MainBakery._connection)
    async with Cake(conn_cake) as connection:  # bake as AsyncContextManager (ACM)
        await connection.execute("TRUNCATE person;")


@pytest.mark.parametrize("number", range(100))
async def test_integration(
    test_client: Callable,
    number: int,
):
    """Test integration."""

    person: dict = {
        "first_name": "fname",
        "second_name": "sname",
        "age": number,
    }

    async with test_client([router]) as client:
        resp = await client.post("/person", json=person)

    assert resp.status_code == 201
    person_id: int = resp.json()["person_id"]

    async with test_client([router]) as client:
        resp = await client.get(f"/person/{person_id}")

    assert resp.status_code == 200
    assert resp.json() == {**person, "person_id": person_id}
    assert not BackgroundTask.CALL_COUNT
