import pytest

from bakery import Bakery, Cake, __Cake__

from .misc import CPU


class MyPC(Bakery):
    cpu_1: CPU = __Cake__()
    cpu_2: CPU = Cake(CPU, core_num=cpu_1.core_num, manufacturer=cpu_1.manufacturer)


async def test_multiple_openings() -> None:
    cpu = CPU(core_num=8, manufacturer="Intel")

    async with MyPC(cpu_1=cpu), MyPC(), MyPC(), MyPC() as pc:  # type: ignore[call-arg]
        assert pc.cpu_1.core_num == pc.cpu_2.core_num == 8
        assert pc.cpu_1.manufacturer == pc.cpu_2.manufacturer == "Intel"


async def test_multiple_openings_with_values() -> None:
    cpu = CPU(core_num=8, manufacturer="Intel")

    with pytest.raises(
        TypeError,
        match="(.*) initialized multiple times with keyword arguments. "
        "It doesn't make sense. (.*)",
    ):
        async with MyPC(cpu_1=cpu), MyPC(cpu_1=cpu):  # type: ignore[call-arg]
            ...
