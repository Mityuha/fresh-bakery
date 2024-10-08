from typing import Final

import pytest

from bakery import Bakery, Cake


class CoresBakery(Bakery):
    core_num: int = Cake(4)


class MyCPU:
    def __init__(self, core_num: int) -> None:
        self.core_num: Final = core_num


class CPUBakery(Bakery):
    core_num: int = Cake(8)
    cpu: MyCPU = Cake(MyCPU, core_num)


async def test_di_piece_of_cake_should_not_work() -> None:
    """Honestly speaking, I don't know why and when it can happen, but now it shouldn't work.

    Please, don't use this in production code.
    """
    # CPUBakery.cpu.core_num -- is a PieceOfCake class
    # It means cores.core_num will be PieceOfCake as well
    async with CPUBakery() as cpu, CoresBakery(core_num=CPUBakery.cpu.core_num) as cores:  # type: ignore[arg-type]
        assert cpu.core_num == 8
        with pytest.raises(AssertionError):
            assert cores.core_num == 8
