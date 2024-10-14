from bakery import Bakery, Cake, __Cake__

from .misc import Adapter, Auth, HttpClient


class AuthBakery(Bakery):
    username: str = __Cake__()
    password: str = __Cake__()
    auth: Auth = Cake(Auth, username=username, password=password)


class ClientBakery(Bakery):
    base_url: str = __Cake__()
    auth: Auth = __Cake__()
    client: HttpClient = Cake(Cake(HttpClient, base_url, auth=auth))


class AdapterBakery(Bakery):
    client: HttpClient = __Cake__()
    adapter: Adapter = Cake(Adapter, client)


class AppBakery(Bakery):
    username: str = __Cake__()
    password: str = __Cake__()
    http_base_url: str = __Cake__()

    auth_bakery: AuthBakery = Cake(
        Cake(
            AuthBakery,
            username=username,
            password=password,
        )
    )
    client_bakery: ClientBakery = Cake(
        Cake(
            ClientBakery,
            base_url=http_base_url,
            auth=auth_bakery.auth,
        )
    )

    adapter_bakery: AdapterBakery = Cake(Cake(AdapterBakery, client=client_bakery.client))

    adapter: Adapter = Cake(adapter_bakery.adapter)


async def test_di_http_client() -> None:
    username: str = "[masked_username]"
    password: str = "[masked_password]"
    base_url: str = "[masked_url]"

    auth: Auth
    client: HttpClient

    async with AppBakery(username=username, password=password, http_base_url=base_url) as bakery:
        adapter = bakery.adapter
        await adapter.user_info()

        assert bakery.auth_bakery.username == bakery.auth_bakery.auth.username == username
        assert bakery.auth_bakery.password == bakery.auth_bakery.auth.password == password
        assert (
            bakery.client_bakery.auth
            is bakery.adapter_bakery.client.auth
            is bakery.auth_bakery.auth
        )
        assert bakery.client_bakery.base_url == bakery.client_bakery.client.base_url == base_url
        assert bakery.adapter_bakery.client is bakery.client_bakery.client

        auth = bakery.auth_bakery.auth
        client = bakery.adapter_bakery.client

    assert auth.token_got
    assert not client.connected
