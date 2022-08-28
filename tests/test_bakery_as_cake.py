"""Test bakery as cake."""
from dataclasses import dataclass

from bakery import Bakery, Cake


async def test_bakery_as_cake() -> None:
    """Test bakery as cake."""

    @dataclass
    class Car:
        """Car."""

        name: str

    class Garage(Bakery):
        """Garage."""

        car: Car = Cake(Car, "BMW")
        bmw_logo = car.name

    class House(Bakery):
        """House."""

        garage = Cake(Garage())
        bmw_car = garage.car
        bmw_logo = garage.bmw_logo

    async with House() as house:
        assert house.bmw_car.name == house.garage.bmw_logo
        assert house.bmw_logo == "BMW"
