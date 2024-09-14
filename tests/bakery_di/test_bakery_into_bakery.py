from typing import Any

from bakery import Bakery, Cake, Shape


class HttpClient:
    def __init__(self):
        self.connected: bool = False

    async def get(self, _url: str) -> Any:
        assert self.connected
        return None

    async def __aenter__(self) -> "HttpClient":
        assert not self.connected
        self.connected = True
        return self

    async def __aexit__(self, *_args: Any) -> None:
        assert self.connected
        self.connected = False


class Adapter:
    def __init__(self, client: HttpClient) -> None:
        self.client = client

    async def user_info(self) -> Any:
        return await self.client.get("/some/url")


async def test_di_http_client() -> None:
    class Bakery1(Bakery):
        external_client: HttpClient = Shape()
        adapter: Adapter = Cake(Adapter, external_client)

    class Bakery2(Bakery):
        client: HttpClient = Cake(Cake(HttpClient))
        bakery1: Bakery1 = Cake(Cake(Bakery1, external_client=client))

        http_adapter: Adapter = Cake(bakery1.adapter)

    async with Bakery2() as cont:
        adapter = cont.http_adapter
        await adapter.user_info()
