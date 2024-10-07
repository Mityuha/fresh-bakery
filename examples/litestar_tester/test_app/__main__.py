"""Adaptive litestar DI's example.

https://docs.litestar.dev/latest/usage/dependency-injection.html
"""
from typing import Any, List, Protocol, runtime_checkable

from litestar import Controller, Litestar, Router, get
from litestar.di import Provide

from bakery import Bakery, Cake


class Database:
    async def fetch_names(self) -> list[str]:
        return ["name1", "name2", "name3"]


def dict_fn() -> dict:
    return {"a": 1, "b": 2}


def list_fn() -> list:
    return [1, 2, 3]


def int_fn() -> int:
    return 43


def x2_multiplier(x: float) -> float:
    return x * 2


class MyBakery(Bakery):
    database: Database = Cake(Database)
    int_fn: int = Cake(int_fn)
    dict_fn: dict = Cake(dict_fn)
    list_fn: list = Cake(list_fn)
    x2_multiplier: Any = Cake(lambda: x2_multiplier)


@runtime_checkable
class DatabaseProto(Protocol):
    async def fetch_names(self) -> List[str]:
        ...


class MyController(Controller):
    path = "/controller"
    # on the controller
    dependencies = {"controller_dependency": Provide(MyBakery.list_fn)}

    # on the route handler
    @get(
        path="/handler",
        dependencies={
            "local_dependency": Provide(MyBakery.int_fn),
            "x2_multiplier": Provide(MyBakery.x2_multiplier),
        },
    )
    async def my_route_handler(
        self,
        database: DatabaseProto,
        router_dependency: dict,
        controller_dependency: list,
        local_dependency: int,
        x2_multiplier: Any,
    ) -> dict:
        return {
            "names": await database.fetch_names(),
            "router_dependency": router_dependency,
            "controller_dependency": controller_dependency,
            "local_dependency": local_dependency,
            "x2": x2_multiplier(32),
        }


my_router = Router(
    path="/router",
    dependencies={"router_dependency": Provide(MyBakery.dict_fn)},
    route_handlers=[MyController],
)


async def on_startup() -> None:
    await MyBakery.aopen()


async def on_shutdown() -> None:
    await MyBakery.aclose()


# on the app
app = Litestar(
    route_handlers=[my_router],
    dependencies={"database": Provide(MyBakery.database)},
    on_startup=[on_startup],
    on_shutdown=[on_shutdown],
)
