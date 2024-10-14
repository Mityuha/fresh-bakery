import pytest

from bakery import Bakery, Cake

from .misc import CPU


class CpuBakery(Bakery):
    cpu: CPU = Cake(CPU, core_num=4, manufacturer="Apple")


async def test_di_item_not_bakery_item() -> None:
    with pytest.raises(TypeError):
        async with CpuBakery(core_num=2):  # type: ignore[call-arg]
            ...
