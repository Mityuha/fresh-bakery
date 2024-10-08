from dataclasses import dataclass

from bakery import Bakery, Cake


@dataclass
class CPU:
    core_num: int
    manufacturer: str


async def test_di_with_cake() -> None:
    class MyPC(Bakery):
        cpu_1: CPU = Cake(CPU, core_num=1, manufacturer="AMD")
        cpu_2: CPU = Cake(CPU, core_num=cpu_1.core_num, manufacturer=cpu_1.manufacturer)

    async with MyPC(cpu_1=Cake(CPU, core_num=8, manufacturer="Intel")) as pc:
        assert pc.cpu_1.core_num == pc.cpu_2.core_num == 8
        assert pc.cpu_1.manufacturer == pc.cpu_2.manufacturer == "Intel"
