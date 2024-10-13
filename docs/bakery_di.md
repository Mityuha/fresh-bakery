# Bakery DI

!!! note
    New in version 0.4.2


Fresh bakery provides a DI mechanism. And sometimes it's very convenient to structure your application so that different modules have their own bakeries.     
Even more: sometimes it's really convenient to initiate modules over their bakeries. 
If so, why don't pass arguments to such bakeries?     
Let's suppose we have Resource Owner Password Authentication Flow: we have to receive token by (username, password) tuple. 

```python
from typing import Final, Iterator

import httpx
from httpx import Auth, Request


class IntranetAuth(Auth):
    def __init__(self, url: str, *, login: str, password: str) -> None:
        self._url: Final = url
        self._auth: Final = (login, password)

    def sync_auth_flow(self, request: Request) -> Iterator[Request]:
        resp = httpx.get(self._url, auth=self._auth)
        token: str = resp.json()["token"]
        request.headers["Authorization"] = f"Bearer {token}"
        yield request

```
And we have `AuthBakery` bakery for such an authentication:
```python
from bakery import Bakery, Cake, __Cake__


class AuthBakery(Bakery):
    auth_url: str = __Cake__()
    username: str = __Cake__()
    password: str = __Cake__()

    auth: IntranetAuth = Cake(IntranetAuth, auth_url, login=username, password=password)
```
Also we have a client to receive user info
```python
from typing import Final

from httpx import Client


class UserClient:
    def __init__(self, client: Client) -> None:
        self.client: Final = client

    def user_info(self, user_id: int) -> dict:
        resp = self.client.get(f"/api/v1/users/{user_id}")
        return resp.json()
```
and bakery for this client
```python
from httpx import Auth, Client

from bakery import Bakery, Cake, __Cake__


class UserClientBakery(Bakery):
    base_url: str = __Cake__()
    auth: Auth = __Cake__()
    http_client: Client = Cake(Cake(Client, base_url=base_url, auth=auth))
    client: UserClient = Cake(UserClient, http_client)
```
We can see to initiate `AuthBakery` we need
- Authentication url `auth_url`
- `username`
- `password`

To initiate `UserClientBakery` we need:
- Url to go: `base_url`
- authentication `auth`

All right, let's glue all this over 3rd `ApplicationBakery` bakery:
```python
from bakery import Bakery, Cake


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
```
We defined all urls and credentials just right in `ApplicationBakery`, but of course, we can redefine it over arguments passing:
```python
async def main() -> None:
    async with ApplicationBakery(auth_url="https://google.com") as bakery:
        ...
```
The complete example can look like this
```python
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
```
You can inspect this example for more details in [examples folder](https://github.com/Mityuha/fresh-bakery/tree/main/examples/docs_bakery_di_example). But I hope the idea is clear: you can use the power of Dependency Injection for bakeries as simple as for plain classes and functions.
