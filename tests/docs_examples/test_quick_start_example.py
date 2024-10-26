from __future__ import annotations

from bakery import Bakery, Cake


def full_days_in(hours: int) -> float:
    return hours / 24


def average(total: int, num: int) -> float:
    return total / num


class WorkingBakery(Bakery):
    average_hours: int = Cake(8)
    week_hours: int = Cake(sum, [average_hours, average_hours, 7, 9, average_hours])
    full_days: float = Cake(full_days_in, week_hours)


async def test_hours_example() -> None:
    async with WorkingBakery() as bakery:
        assert bakery.week_hours == 40
        assert bakery.full_days - 0.00001 < full_days_in(40)
        assert int(bakery.average_hours) == 8
