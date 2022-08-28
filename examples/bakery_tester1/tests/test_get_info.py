"""Test get info."""

from copy import copy
from typing import Callable
from unittest.mock import Mock
from uuid import uuid4

from bakery import BakingMethod, Cake
from bakery.testbakery import BakeryMock

from test_app.bakery import MainBakery
from test_app.cron.bakery import CapacityBakery
from test_app.routes import get_info


async def test_info_1(
    test_client: Callable,
    bakery_mock: BakeryMock,
):
    """Test info 1."""

    projects: list[str] = [str(uuid4()), str(uuid4())]

    bakery_mock.capacity = lambda **_kwargs: Mock(**{"keys.return_value": projects})

    async with test_client([get_info.router]) as client, bakery_mock(CapacityBakery), MainBakery():
        resp = await client.get("/")

    assert resp.json() == dict(projects=projects, networks=[])


async def test_mock_crons(
    test_client: Callable,
    bakery_mock: BakeryMock,
) -> None:
    """Test info 2."""

    projects: list[str] = [str(uuid4()), str(uuid4())]

    bakery_mock._capacity_p_cron = Cake(0)  # pylint: disable=protected-access

    bakery_mock_cap: BakeryMock = copy(bakery_mock)

    bakery_mock_cap.capacity = Cake(
        Mock(**{"keys.return_value": projects}),
        cake_baking_method=BakingMethod.BAKE_NO_BAKE,
    )

    await bakery_mock_cap.patch(CapacityBakery)
    await bakery_mock.patch(MainBakery)

    async with test_client([get_info.router]) as client:
        resp = await client.get("/")

    assert resp.json() == dict(projects=projects, networks=[])
