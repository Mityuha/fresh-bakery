# ruff: noqa: ERA001, E501
"""Test partial bakery."""

# import os
# from dataclasses import dataclass
# from typing import Dict
#
# import pytest
#
# from bakery import BUILTIN_TYPES, Bakery, Cake, Shape
#
#
# @dataclass
# class CPU:
#    """cpu."""
#
#    core_num: int
#    manufacturer: str
#
#
# async def double_x(num: float) -> float:
#    """double num."""
#    return num * 2
#
#
# async def test_shape() -> None:
#    """test shape."""
#
#    with pytest.raises(ValueError):
#        # cannot bake empty shape
#        Shape()()
#
#    for value in BUILTIN_TYPES:
#        with pytest.raises(ValueError):
#            # can only fill with cake
#            Shape().cake = value
#
#        value = "123"
#        shape: Shape = Shape()
#        shape.cake = Cake(value)
#        with pytest.raises(ValueError):
#            # filled but not baked
#            shape()
#
#        async with shape:
#            assert shape() == value
#
#        await shape.bake()
#        assert shape() == value
#        await shape.unbake()
#
#        with pytest.raises(ValueError):
#            # can only fill once
#            shape.cake = Cake(value)
#
#
# async def test_piece_of_shape() -> None:
#    """test piece of shape."""
#
#    @dataclass
#    class Keys:
#        """keys."""
#
#        keys: Dict
#
#    shape: Shape = Shape()
#    value: str = "value"
#    dct = {"key1": {"key2": value}}
#    keys: Keys = Keys(keys=dct)
#    cake: Cake = Cake(keys)
#
#    shape.cake = cake
#    async with shape as val:
#        assert cake() == keys
#        assert val == keys
#        assert shape.keys["key1"]["key2"]() == value
#
#
# async def test_partial_bakery_error() -> None:
#    """fail on partial bakery."""
#
#    class MyPC(Bakery):
#        """my pc."""
#
#        core_num: Shape = Shape()
#        manufacturer: Shape[str] = Shape()
#        cpu1: Cake = Cake(
#            CPU,
#            core_num=core_num,
#            manufacturer=manufacturer,
#        )
#
#    with pytest.raises(ValueError):
#        async with MyPC() as my_pc:
#            pass
#
#
# async def test_partial_bakery_ok1() -> None:
#    """test ok."""
#
#    class MyPC(Bakery):
#        """my pc."""
#
#        core_num: Shape = Shape()
#        manufacturer: Shape[str] = Shape()
#        cpu1: Cake = Cake(
#            CPU,
#            core_num=core_num,
#            manufacturer=manufacturer,
#        )
#
#    class Settings:
#        """settings."""
#
#        def __init__(self):
#            self.core_num: int = int(os.environ["core_num"])
#            self.manufacturer: str = os.environ["manufacturer"]
#
#    class Workshop(Bakery):
#        """my workshop."""
#
#        settings: Cake = Cake(Settings)
#
#        cpu: Cake[CPU] = Cake(CPU, core_num=settings.core_num, manufacturer=settings.manufacturer)
#
#        my_pc: Cake[MyPC] = Cake(MyPC(core_num=cpu.core_num, manufacturer=cpu.manufacturer))
#
#    core_num: int = 4
#    manufacturer: str = "Intel"
#
#    os.environ["core_num"] = str(core_num)
#    os.environ["manufacturer"] = manufacturer
#
#    async with Workshop() as workshop:
#        print(workshop.my_pc)
#        assert workshop.my_pc.core_num == workshop.settings.core_num == core_num
#        assert workshop.my_pc.manufacturer == workshop.settings.manufacturer == manufacturer
#        assert workshop.my_pc.cpu1.core_num == workshop.settings.core_num == core_num
#        assert workshop.my_pc.cpu1.manufacturer == workshop.settings.manufacturer == manufacturer
#
#        assert Workshop.my_pc.core_num() == workshop.settings.core_num == core_num
#        assert Workshop.my_pc.manufacturer() == workshop.settings.manufacturer == manufacturer
#        assert Workshop.my_pc.cpu1.core_num() == workshop.settings.core_num == core_num
#        assert Workshop.my_pc.cpu1.manufacturer() == workshop.settings.manufacturer == manufacturer
#
#    core_num = 8
#    manufacturer = "Apple"
#
#    # test shape unbaking
#    async with Workshop() as workshop:
#        assert workshop.my_pc.core_num == workshop.settings.core_num == core_num
#        assert workshop.my_pc.manufacturer == workshop.settings.manufacturer == manufacturer
#        assert workshop.my_pc.cpu1.core_num == workshop.settings.core_num == core_num
#        assert workshop.my_pc.cpu1.manufacturer == workshop.settings.manufacturer == manufacturer
#
#        assert Workshop.my_pc.core_num() == workshop.settings.core_num == core_num
#        assert Workshop.my_pc().manufacturer == workshop.settings.manufacturer == manufacturer
#        assert Workshop.my_pc().cpu1.core_num == workshop.settings.core_num == core_num
#        assert Workshop().my_pc.cpu1.manufacturer == workshop.settings.manufacturer == manufacturer
