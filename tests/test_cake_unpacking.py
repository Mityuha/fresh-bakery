from collections import ChainMap
from itertools import chain

from bakery import Bakery, Cake


# All type: ignore macros are only for old (<1.8.0) mypy versions


class MyBakery1(Bakery):
    some_dict_1: dict = Cake({"key1": 1, "key2": 2})
    some_list_1: list = Cake([1, 2, 3, 4])


class MyBakery2(Bakery):
    some_dict_2: dict = Cake(dict, key3=3, key4=4)  # type: ignore
    some_tuple_2: tuple = Cake((5, 6, 7, 8))


class BigBakery(Bakery):
    my_bakery1: MyBakery1 = Cake(Cake(MyBakery1))
    my_bakery2: MyBakery2 = Cake(Cake(MyBakery2))

    common_mapper: dict = Cake(  # type: ignore
        dict,  # type: ignore
        Cake(ChainMap, my_bakery1.some_dict_1, my_bakery2.some_dict_2),
    )
    common_seq: list = Cake(  # type: ignore
        list,  # type: ignore
        Cake(
            chain,
            my_bakery1.some_list_1,
            my_bakery2.some_tuple_2,
        ),
    )


async def test_it() -> None:
    async with BigBakery() as bakery:
        assert bakery.common_mapper == {"key1": 1, "key2": 2, "key3": 3, "key4": 4}
        assert bakery.common_seq == [1, 2, 3, 4, 5, 6, 7, 8]
