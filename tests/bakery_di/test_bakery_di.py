from dataclasses import dataclass

import pytest

from bakery import Bakery, Cake, Shape


@dataclass
class CPU:
    core_num: int
    manufacturer: str


async def test_all_default_specified() -> None:
    class MyPC(Bakery):
        cpu_1: CPU = Cake(CPU, core_num=1, manufacturer="AMD")
        cpu_2: CPU = Cake(CPU, core_num=cpu_1.core_num, manufacturer=cpu_1.manufacturer)

    async with MyPC(cpu_1=CPU(core_num=8, manufacturer="Intel")) as pc:
        assert pc.cpu_1.core_num == pc.cpu_2.core_num == 8
        assert pc.cpu_1.manufacturer == pc.cpu_2.manufacturer == "Intel"


async def test_one_param_has_to_be_specified() -> None:
    class MyPC(Bakery):
        cpu_1: CPU = Shape()
        cpu_2: CPU = Cake(CPU, core_num=cpu_1.core_num, manufacturer=cpu_1.manufacturer)

    async with MyPC(cpu_1=CPU(core_num=8, manufacturer="Intel")) as pc:
        assert pc.cpu_1.core_num == pc.cpu_2.core_num == 8
        assert pc.cpu_1.manufacturer == pc.cpu_2.manufacturer == "Intel"


async def test_one_param_not_specified_in_runtime() -> None:
    class MyPC(Bakery):
        cpu_1: CPU = Shape()
        cpu_2: CPU = Cake(CPU, core_num=cpu_1.core_num, manufacturer=cpu_1.manufacturer)

    with pytest.raises(AttributeError):
        async with MyPC():  # type: ignore[call-arg]
            ...
