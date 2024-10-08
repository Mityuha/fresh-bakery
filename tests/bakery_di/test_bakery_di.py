from bakery import Bakery, Cake, __Cake__

from .misc import CPU


async def test_all_default_specified() -> None:
    class MyPC(Bakery):
        cpu_1: CPU = Cake(CPU, core_num=1, manufacturer="AMD")
        cpu_2: CPU = Cake(CPU, core_num=cpu_1.core_num, manufacturer=cpu_1.manufacturer)

    async with MyPC(cpu_1=CPU(core_num=8, manufacturer="Intel")) as pc:
        assert pc.cpu_1.core_num == pc.cpu_2.core_num == 8
        assert pc.cpu_1.manufacturer == pc.cpu_2.manufacturer == "Intel"


async def test_one_param_has_to_be_specified() -> None:
    class MyPC(Bakery):
        cpu_1: CPU = __Cake__()
        cpu_2: CPU = Cake(CPU, core_num=cpu_1.core_num, manufacturer=cpu_1.manufacturer)

    async with MyPC(cpu_1=CPU(core_num=8, manufacturer="Intel")) as pc:
        assert pc.cpu_1.core_num == pc.cpu_2.core_num == 8
        assert pc.cpu_1.manufacturer == pc.cpu_2.manufacturer == "Intel"
