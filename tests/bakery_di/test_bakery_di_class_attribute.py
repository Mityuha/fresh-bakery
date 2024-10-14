from bakery import Bakery, Cake, __Cake__

from .misc import Auth, HttpClient


class Client1Bakery(Bakery):
    username: str = __Cake__()
    password: str = __Cake__()
    base_url: str = __Cake__()

    auth: Auth = Cake(Auth, username=username, password=password)
    client: HttpClient = Cake(Cake(HttpClient, base_url, auth=auth))


class Client2Bakery(Bakery):
    base_url: str = __Cake__()
    auth: Auth = __Cake__()

    client: HttpClient = Cake(Cake(HttpClient, base_url, auth=auth))


class AppBakery(Bakery):
    username: str = __Cake__()
    password: str = __Cake__()
    base_url: str = __Cake__()

    client1_bakery: Client1Bakery = Cake(
        Cake(Client1Bakery, username=username, password=password, base_url=base_url)
    )

    client2_bakery: Client2Bakery = Cake(
        Cake(
            Client2Bakery, base_url=client1_bakery.client.base_url, auth=client1_bakery.client.auth
        )
    )


async def test_bakery_di_class_attribute() -> None:
    username: str = "[masked_username_2]"
    password: str = "[masked_password_2]"
    base_url: str = "[masked_url_2]"

    async with AppBakery(username=username, password=password, base_url=base_url) as bakery:
        assert bakery.client1_bakery.auth is bakery.client2_bakery.auth
