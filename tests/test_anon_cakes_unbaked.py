"""Test if all anon cakes are unbaked on errors."""
from typing import Any, Iterator, List, no_type_check

import pytest

from bakery import Bakery, Cake, cake_ingredients, cake_name, flatten, is_baked, is_cake


def search_for_all_anon_cakes(cakes: List) -> Iterator[Any]:
    """Search for all anon cakes."""
    for cake in cakes:
        ingredients = cake_ingredients(cake)
        for ingr in flatten(
            [
                ingredients.recipe_args,
                ingredients.recipe_kwargs,
            ]
        ):
            if is_cake(ingr):
                yield from search_for_all_anon_cakes([ingr])
                if not cake_name(ingr):
                    yield ingr
        if is_cake(ingredients.recipe):
            yield from search_for_all_anon_cakes([ingredients.recipe])

        if not cake_name(cake):
            yield cake


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


# otherwise mypy hangs forever ;'(
@no_type_check
async def test_nested_anon_cakes_unbaked() -> None:
    """Test nested anon cakes unbaked."""

    def sum_with_error(*args: float) -> float:
        """Sum with error."""
        return sum(args)

    anon_cakes: List[float] = [
        Cake(Cake(Cake(Cake(Cake(1.0))))),
        Cake(Cake(Cake(Cake(Cake(Cake(Cake(2.0))))))),
        Cake(Cake(Cake(Cake(Cake(Cake(3.0)))))),
        Cake(Cake(Cake(Cake(4.0)))),
        Cake(Cake(Cake(Cake(Cake(Cake(5.0)))))),
    ]

    class MathBakery(Bakery):
        """Math bakery."""

        value: float = Cake(sum_with_error, *anon_cakes)

    async with MathBakery():
        assert MathBakery().value == 15

    all_anon_cakes = list(search_for_all_anon_cakes(anon_cakes))
    assert len(all_anon_cakes) == 28

    assert all(not is_baked(cake) for cake in all_anon_cakes)
