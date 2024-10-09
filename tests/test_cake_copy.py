"""Test cake copy methods."""

from copy import copy, deepcopy
from dataclasses import dataclass

import pytest

from bakery import (
    Bakery,
    Cake,
    bake,
    cake_baking_method,
    cake_name,
    cake_recipe,
    cake_recipe_args,
    cake_recipe_kwargs,
    is_baked,
    unbake,
)


@dataclass
class CPU:
    """Settings."""

    core_num: int
    manufacturer: str


class MyPC(Bakery):
    """My bakery."""

    core_num: int = Cake(4)
    manufacturer: str = Cake("Intel")
    cpu: CPU = Cake(CPU, core_num=core_num, manufacturer=manufacturer)


def test_copy_cake_not_baked_is_not_cake_itself() -> None:
    """Test cake not baked copy is not cake itself."""
    assert MyPC.cpu is not copy(MyPC.cpu)
    assert MyPC.cpu is not deepcopy(MyPC.cpu)


async def test_copy_cake() -> None:
    """Test new recipe."""
    async with MyPC():
        cpu_cake = MyPC.cpu
        cpu_new_cake = copy(MyPC.cpu)

        assert id(cpu_cake) != id(cpu_new_cake)
        assert cake_name(cpu_cake) == cake_name(cpu_new_cake)
        assert cake_baking_method(cpu_cake) == cake_baking_method(cpu_new_cake)
        assert True is is_baked(cpu_cake) != is_baked(cpu_new_cake)
        assert cake_recipe(cpu_cake) is cake_recipe(cpu_new_cake)
        assert cake_recipe_args(cpu_cake) == cake_recipe_args(cpu_new_cake)
        assert cake_recipe_kwargs(cpu_cake) == cake_recipe_kwargs(cpu_new_cake)

        cpu: CPU = cpu_cake()
        with pytest.raises(ValueError, match="Cake 'cpu' is not baked. Just bake it!"):
            # Cake copy is not baked yet
            _ = cpu_new_cake.core_num()

        new_cpu: CPU
        async with cpu_new_cake as new_cpu:
            assert id(cpu) != id(new_cpu)
            assert cpu.core_num == new_cpu.core_num
            assert cpu.manufacturer == new_cpu.manufacturer

        new_cpu = await bake(cpu_new_cake)
        assert id(cpu) != id(new_cpu)
        assert cpu.core_num == new_cpu.core_num
        assert cpu.manufacturer == new_cpu.manufacturer

        await unbake(cpu_new_cake)


async def test_deepcopy_cake() -> None:
    """Test recipe deepcopy.

    Improve this test as well as Ingredients' __deepcopy__ method.
    """
    async with MyPC():
        cpu_cake = MyPC.cpu
        cpu_new_cake = deepcopy(MyPC.cpu)

        assert id(cpu_cake) != id(cpu_new_cake)
        assert cake_name(cpu_cake) == cake_name(cpu_new_cake)
        assert cake_baking_method(cpu_cake) == cake_baking_method(cpu_new_cake)
        assert True is is_baked(cpu_cake) != is_baked(cpu_new_cake)
        assert cake_recipe(cpu_cake) is cake_recipe(cpu_new_cake)
        assert cake_recipe_args(cpu_cake) == cake_recipe_args(cpu_new_cake)

        cpu: CPU = cpu_cake()
        with pytest.raises(ValueError, match="Cake 'cpu' is not baked. Just bake it!"):
            # Cake copy is not baked yet
            _ = cpu_new_cake.core_num()

        new_cpu: CPU
        async with cpu_new_cake as new_cpu:
            assert id(cpu) != id(new_cpu)
            assert cpu.core_num == new_cpu.core_num
            assert cpu.manufacturer == new_cpu.manufacturer

        new_cpu = await bake(cpu_new_cake)
        assert id(cpu) != id(new_cpu)
        assert cpu.core_num == new_cpu.core_num
        assert cpu.manufacturer == new_cpu.manufacturer

        await unbake(cpu_new_cake)
