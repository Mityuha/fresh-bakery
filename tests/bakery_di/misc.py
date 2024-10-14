from dataclasses import dataclass
from typing import Any, Final


@dataclass
class CPU:
    core_num: int
    manufacturer: str


class Auth:
    def __init__(self, *, username: str, password: str) -> None:
        self.username: Final = username
        self.password: Final = password
        self.token_got: bool = False

    async def get_token(self) -> str:
        assert not self.token_got
        self.token_got = True
        return "[masked]"


class HttpClient:
    def __init__(self, base_url: str, *, auth: Auth) -> None:
        self.base_url: Final = base_url
        self.auth: Final = auth
        self.connected: bool = False

    async def get(self, _url: str) -> Any:
        assert self.connected
        await self.auth.get_token()
        return None

    async def __aenter__(self) -> "HttpClient":
        assert not self.connected
        self.connected = True
        return self

    async def __aexit__(self, *_args: object) -> None:
        assert self.connected
        self.connected = False


class Adapter:
    def __init__(self, client: HttpClient) -> None:
        self.client = client

    async def user_info(self) -> Any:
        return await self.client.get("/some/url")
