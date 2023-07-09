from typing import Any, List

import pytest
from litestar import Router
from litestar.di import Provide
from litestar.status_codes import HTTP_200_OK
from litestar.testing import create_test_client
from test_app.__main__ import MyBakery, MyController

from bakery import Cake
from bakery.testbakery import BakeryMock


async def test_get_item(bakery_mock: BakeryMock) -> None:
    class Database:
        async def fetch_names(self) -> List[str]:
            return ["s1", "s2"]

    def almost_x2_multiplier(x: float) -> float:
        return x * 2 - 1

    def exception_handler(request, exception):
        raise exception

    # Cannot override local and controller dependencies
    # So let's do it using bakery!

    # controller_dependency -- list_fn
    bakery_mock.list_fn = Cake([5, 6, 7])

    # local_dependency -- int_fn
    bakery_mock.int_fn = Cake(55)

    # x2_multiplier == x2_multiplier
    bakery_mock.x2_multiplier = Cake(lambda: almost_x2_multiplier)

    with create_test_client(
        on_startup=[bakery_mock(MyBakery).__aenter__],
        on_shutdown=[bakery_mock.__aexit__],
        route_handlers=Router(
            path="/",
            route_handlers=[MyController],
        ),
        dependencies={
            "database": Provide(Database),
            "controller_dependency": Provide(lambda: [5, 6, 7]),
            "router_dependency": Provide(lambda: {"key1": 1, "key2": 2}),
        },
        exception_handlers={500: exception_handler},
    ) as client:
        response = client.get("/controller/handler")
        assert response.status_code == HTTP_200_OK
        assert response.json() == {
            "names": ["s1", "s2"],
            "router_dependency": {"key1": 1, "key2": 2},
            "controller_dependency": [5, 6, 7],
            "local_dependency": 55,
            "x2": almost_x2_multiplier(32),
        }
