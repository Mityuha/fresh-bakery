"""Test if all anon cakes are unbaked on errors."""
from typing import List

import pytest

from bakery import Bakery, Cake, is_baked


async def test_anon_cakes_unbaked() -> None:
    """Test anon cakes unbaked."""

    def sum_with_error(*args: float) -> float:
        """Sum with error."""
        return sum(args)

    anon_cakes: List[float] = [
        Cake(1.0),
        Cake(2.0),
        Cake(3.0),
        Cake(4.0),
        Cake("5.0"),  # type: ignore
    ]

    class MathBakery(Bakery):
        """Math bakery."""

        value: float = Cake(sum_with_error, *anon_cakes)

    with pytest.raises(TypeError):
        async with MathBakery():
            pass

    assert all(not is_baked(cake) for cake in anon_cakes)  # type: ignore
