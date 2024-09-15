"""Test cakes baking."""

from __future__ import annotations

from contextlib import contextmanager
from typing import TYPE_CHECKING, Any, AsyncIterator, ClassVar, Iterator

import pytest
from typing_extensions import Self

from bakery import Bakery, Cake

from . import asynccontextmanager

if TYPE_CHECKING:
    from types import TracebackType


@pytest.mark.parametrize("car_limit", range(5))
async def test_callable_cake(car_limit: int) -> None:
    """Test callable cake."""

    class Car:
        """Car."""

        def __init__(self, brand: str) -> None:
            self.brand: str = brand

    def garage_review(limit: Any = None) -> list[Car]:
        """My garage review."""
        return [Car("BMW"), Car("Mercedes"), Car("2107"), Car("2109")][:limit]

    class MyCar(Bakery):
        """My car."""

        brand: str = Cake("BMW")
        car: Car = Cake(Car, brand)
        car_list: list[Car] = Cake(garage_review, car_limit)

    async with MyCar() as car:
        assert car.car.brand == "BMW"
        assert [car.brand for car in car.car_list] == [
            car.brand for car in garage_review(car_limit)
        ]


async def test_context_cake() -> None:
    """Test context cake."""

    class Car:
        """Car."""

        def __init__(self, brand: str) -> None:
            self.brand: str = brand
            self.is_turned_on: bool = False

        def turn_on(self) -> None:
            """Turn engine on."""
            self.is_turned_on = True

        def turn_off(self) -> None:
            """Turn engine off."""
            self.is_turned_on = False

    @contextmanager
    def open_garage(brand: str) -> Iterator[Car]:
        """Opens garage with car turned on."""
        car = Car(brand)
        car.turn_on()
        yield car
        car.turn_off()

    class ReadyCar(Bakery):
        """My car ready to go."""

        brand: str = "VAZ"
        car: Car = Cake(open_garage(brand))

    car_copy = None
    async with ReadyCar() as car:
        assert car.car.is_turned_on
        car_copy = car.car

    assert not car_copy.is_turned_on


async def test_async_context_cake() -> None:
    """Test async context cake."""

    class Car:
        """Car."""

        def __init__(self, brand: str) -> None:
            self.brand: str = brand
            self.is_turned_on: bool = False

        async def turn_on(self) -> None:
            """Turn engine on."""
            self.is_turned_on = True

        async def turn_off(self) -> None:
            """Turn engine off."""
            self.is_turned_on = False

    @asynccontextmanager
    async def open_garage(brand: str) -> AsyncIterator[Car]:
        """Opens garage with car turned on."""
        car = Car(brand)
        await car.turn_on()
        yield car
        await car.turn_off()

    class ReadyCar(Bakery):
        """My car ready to go."""

        brand: str = "VAZ"
        car: Car = Cake(open_garage(brand))

    car_copy = None
    async with ReadyCar() as car:
        assert car.car.is_turned_on
        car_copy = car.car

    assert not car_copy.is_turned_on


@pytest.mark.parametrize("broken_index", range(3))
async def test_all_cakes_unbaked(broken_index: int) -> None:
    """Test cakes unbaked."""

    class Car:
        """Car."""

        def __init__(self, brand: str) -> None:
            self.brand: str = brand
            self.is_turned_on: bool = False

        def __enter__(self) -> Self:
            """Turn engine on."""
            self.is_turned_on = True
            return self

        def __exit__(
            self,
            exc_type: type[BaseException] | None,
            exc: BaseException | None,
            traceback: TracebackType | None,
        ) -> None:
            """Turn engine off."""
            self.is_turned_on = False

    class BrokenCar(Car):
        """Broken sensor car."""

        def __exit__(
            self,
            exc_type: type[BaseException] | None,
            exc: BaseException | None,
            traceback: TracebackType | None,
        ) -> None:
            msg = "Bad sensor value."
            raise ValueError(msg)

    class Garage(Bakery):
        """Garage."""

        car1: Car = Cake((BrokenCar if broken_index == 0 else Car)("VAZ"))
        car2: Car = Cake((BrokenCar if broken_index == 1 else Car)("BMW"))
        car3: Car = Cake((BrokenCar if broken_index == 2 else Car)("VW"))

    cars: list[Car] = []
    try:
        async with Garage() as garage:
            assert garage.car1.is_turned_on
            assert garage.car2.is_turned_on
            assert garage.car3.is_turned_on
            cars = [garage.car1, garage.car2, garage.car3]
    except ValueError:
        ...
    else:
        raise AssertionError

    is_broken: dict = {index: index == broken_index for index in range(3)}

    for index, broken in is_broken.items():
        assert cars[index].is_turned_on is broken


@pytest.mark.parametrize("broken_index", range(3))
async def test_all_cakes_unbaked_async(broken_index: int) -> None:
    """Test cakes unbaked."""

    class Car:
        """Car."""

        def __init__(self, brand: str) -> None:
            self.brand: str = brand
            self.is_turned_on: bool = False

        async def __aenter__(self) -> Self:
            """Turn engine on."""
            self.is_turned_on = True
            return self

        async def __aexit__(
            self,
            exc_type: type[BaseException] | None,
            exc: BaseException | None,
            traceback: TracebackType | None,
        ) -> None:
            """Turn engine off."""
            self.is_turned_on = False

    class BrokenCar(Car):
        """Broken sensor car."""

        async def __aexit__(
            self,
            exc_type: type[BaseException] | None,
            exc: BaseException | None,
            traceback: TracebackType | None,
        ) -> None:
            msg = "Bad sensor value."
            raise ValueError(msg)

    class Garage(Bakery):
        """Garage."""

        car1: Car = Cake((BrokenCar if broken_index == 0 else Car)("VAZ"))
        car2: Car = Cake((BrokenCar if broken_index == 1 else Car)("BMW"))
        car3: Car = Cake((BrokenCar if broken_index == 2 else Car)("VW"))

    cars: list[Car] = []
    try:
        async with Garage() as garage:
            assert garage.car1.is_turned_on
            assert garage.car2.is_turned_on
            assert garage.car3.is_turned_on
            cars = [garage.car1, garage.car2, garage.car3]
    except ValueError:
        ...
    else:
        raise AssertionError

    is_broken: dict = {index: index == broken_index for index in range(3)}

    for index, broken in is_broken.items():
        assert cars[index].is_turned_on is broken


@pytest.mark.parametrize("broken_index", range(3))
async def test_all_cakes_unbaked_on_startup(broken_index: int) -> None:
    """Test on startup exception."""
    cars_turned_on: set[str] = set()

    class Car:
        """Car."""

        def __init__(self, brand: str) -> None:
            self.brand: str = brand
            self.is_turned_on: bool = False

        async def __aenter__(self) -> Self:
            """Turn engine on."""
            self.is_turned_on = True
            cars_turned_on.add(self.brand)
            return self

        async def __aexit__(
            self,
            exc_type: type[BaseException] | None,
            exc: BaseException | None,
            traceback: TracebackType | None,
        ) -> None:
            """Turn engine off."""
            cars_turned_on.discard(self.brand)
            self.is_turned_on = False

    class Garage(Bakery):
        """Garage."""

        car1: Car = Cake(Car) if broken_index == 0 else Cake(Car, "VAZ")  # type: ignore[assignment]
        car2: Car = Cake(Car) if broken_index == 1 else Cake(Car, "BMW")  # type: ignore[assignment]
        car3: Car = Cake(Car) if broken_index == 2 else Cake(Car, "VAZ")  # type: ignore[assignment]

    try:
        async with Garage():
            ...
    except TypeError:
        ...
    else:
        raise AssertionError

    assert not cars_turned_on


async def test_cakes_from_bakery_are_equal() -> None:
    """Test cake from bakery and cake passed as argument are equal."""

    class Car:
        """Car."""

        def __init__(self, brand: str) -> None:
            self.brand: str = brand

    class Garage:
        """Garage."""

        def __init__(self, cars: list[Car]) -> None:
            self.cars: list[Car] = cars

    class House(Bakery):
        """My house."""

        car1: Car = Cake(Car, "VAZ")
        car2: Car = Cake(Car, "BMW")
        car3: Car = Cake(Car, "VW")
        garage: Garage = Cake(Garage, [car1, car2, car3])

    async with House() as house:
        assert [car.brand for car in house.garage.cars] == [
            car.brand for car in (house.car1, house.car2, house.car3)
        ]
        assert [id(car) for car in house.garage.cars] == [
            id(car) for car in (house.car1, house.car2, house.car3)
        ]


async def test_complex_bakery() -> None:
    """Test complex bakery."""

    class Car:
        """Car."""

        def __init__(self, brand: str) -> None:
            self.brand: str = brand

        def __repr__(self) -> str:
            return f"{self.brand}"

    class House(Bakery):
        """My house."""

        garage1: ClassVar[list] = [
            Cake(Car, "VAZ"),
            Cake(Car, "BMW"),
            Cake(Car, "VW"),
        ]
        garage2: ClassVar[dict] = {
            "garage1": garage1,
            "garage22": {
                "garage": [
                    Cake(Car("Lambo")),
                ],
            },
        }
        floor1: ClassVar[dict] = {
            "garage1": garage1,
            "garage2": garage2,
            "near": [Cake(Car, "LADA")],
        }

    async with House() as house:
        assert [car.brand for car in house.garage1] == [
            car.brand for car in house.garage2["garage1"]
        ]
        assert [id(car) for car in house.garage1] == [id(car) for car in house.garage2["garage1"]]
        assert house.garage2["garage22"]["garage"][0].brand == "Lambo"
        assert house.garage1 == house.floor1["garage1"]
        assert house.garage2 == house.floor1["garage2"]
        assert house.floor1["near"][0].brand == "LADA"
