from __future__ import annotations

import asyncio
from typing import Final, Iterator

import httpx
from httpx import Auth, Client, Request
from loguru import logger

from bakery import Bakery, Cake, __Cake__


class IntranetAuth(Auth):
    def __init__(self, url: str, *, login: str, password: str) -> None:
        self._url: Final = url
        self._auth: Final = (login, password)

    def sync_auth_flow(self, request: Request) -> Iterator[Request]:
        resp = httpx.get(self._url, auth=self._auth)
        token: str = resp.json()["token"]
        request.headers["Authorization"] = f"Bearer {token}"
        yield request


class UserClient:
    def __init__(self, client: Client) -> None:
        self.client: Final = client

    def user_info(self, user_id: int) -> dict:
        resp = self.client.get(f"/api/v1/users/{user_id}")
        return resp.json()


class AuthBakery(Bakery):
    auth_url: str = __Cake__()
    username: str = __Cake__()
    password: str = __Cake__()

    auth: IntranetAuth = Cake(IntranetAuth, auth_url, login=username, password=password)


class UserClientBakery(Bakery):
    base_url: str = __Cake__()
    auth: Auth = __Cake__()
    http_client: Client = Cake(Cake(Client, base_url=base_url, auth=auth))
    client: UserClient = Cake(UserClient, http_client)


class ApplicationBakery(Bakery):
    auth_url: str = Cake("https://your.auth.url")
    intranet_url: str = Cake("https://your.intranet.url")
    username: str = Cake("[masked]")
    password: str = Cake("[masked]")

    auth_bakery: AuthBakery = Cake(
        Cake(AuthBakery, auth_url=auth_url, username=username, password=password)
    )

    client_bakery: UserClientBakery = Cake(
        Cake(UserClientBakery, base_url=intranet_url, auth=auth_bakery.auth)
    )


async def main() -> None:
    user_id: int = 123
    async with ApplicationBakery(auth_url="https://google.com") as bakery:
        client = bakery.client_bakery.client
        user_info = client.user_info(user_id)

        logger.debug(f"User '{user_id}' info: {user_info}")


if __name__ == "__main__":
    asyncio.run(main())
