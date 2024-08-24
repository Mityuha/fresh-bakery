from time import sleep

from bakery import Bakery, Cake, is_cake
from bakery.testbakery import BakeryMock


async def test_bakery_mock_replace_recipe(bakery_mock: BakeryMock) -> None:
    """Test recipe replacement."""

    def sleeper(sleep_for: float) -> float:
        """Simply sleep."""
        sleep(sleep_for)
        return sleep_for

    class Comp(Bakery):
        """Comp."""

        sleeper1: float = Cake(sleeper, 100)
        sleeper2: float = Cake(sleeper, 200)
        some_list: list = Cake([1, 2, Cake(sleeper, 300)])
        total: float = Cake(sum, (sleeper1, sleeper2, some_list[2]))  # type: ignore

    class Comp2(Bakery):
        """Comp2."""

        comp: Comp = Cake(Comp())

    bakery_mock.sleeper1 = lambda *_args: 100
    bakery_mock.sleeper2 = lambda *_args: 200
    bakery_mock.some_list = [1, 2, 300]
    assert all(is_cake(v) for v in getattr(bakery_mock, "_cake_mocks_").values())

    async with bakery_mock(Comp):
        assert Comp().sleeper1 == 100
        assert Comp().sleeper2 == 200
        assert Comp().some_list[2] == 300
        assert Comp().total == 600

    async with bakery_mock(Comp), Comp2():
        assert Comp2().comp.sleeper1 == 100
        assert Comp2().comp.sleeper2 == 200
        assert Comp2().comp.some_list[2] == 300
        assert Comp2().comp.total == 600
