import pytest

from bakery import Bakery, Cake

from .misc import CPU


class MyPC(Bakery):
    cpu_1: CPU = Cake(CPU, core_num=1, manufacturer="AMD")
    cpu_2: CPU = Cake(CPU, core_num=cpu_1.core_num, manufacturer=cpu_1.manufacturer)


@pytest.mark.parametrize("with_value", [True, False])
async def test_di_with_value(with_value: int) -> None:
    cpu_1: CPU = CPU(core_num=8, manufacturer="Intel")
    if not with_value:
        cpu_1 = Cake(CPU, core_num=8, manufacturer="Intel")

    async with MyPC(cpu_1=cpu_1) as pc:
        assert pc.cpu_1.core_num == pc.cpu_2.core_num == 8
        assert pc.cpu_1.manufacturer == pc.cpu_2.manufacturer == "Intel"

    async with MyPC() as pc:
        assert pc.cpu_1.core_num == pc.cpu_2.core_num == 1
        assert pc.cpu_1.manufacturer == pc.cpu_2.manufacturer == "AMD"
