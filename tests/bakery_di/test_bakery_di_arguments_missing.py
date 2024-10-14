import pytest

from bakery import Bakery, __Cake__


class MyBakery(Bakery):
    arg_1: int = __Cake__()
    arg_2: int = __Cake__()
    arg_3: int = __Cake__()
    arg_4: int = __Cake__()


async def test_one_argument_not_specified() -> None:
    with pytest.raises(TypeError, match="missing 1 required keyword-only argument: 'arg_4'"):
        async with MyBakery(arg_1=1, arg_2=2, arg_3=3):  # type: ignore[call-arg]
            ...


@pytest.mark.parametrize("missed_arg_num", [4, 3, 2])
async def test_more_than_one_arguments_not_specified(missed_arg_num: int) -> None:
    values: dict = {}
    formatted_args: str = "'arg_1', 'arg_2', 'arg_3' and 'arg_4'"
    if missed_arg_num == 3:
        values = {"arg_1": 1}
        formatted_args = "'arg_2', 'arg_3' and 'arg_4'"
    if missed_arg_num == 2:
        values = {"arg_1": 1, "arg_2": 2}
        formatted_args = "'arg_3' and 'arg_4'"

    with pytest.raises(
        TypeError,
        match=f"missing {missed_arg_num} required keyword-only arguments: {formatted_args}",
    ):
        async with MyBakery(**values):  # type: ignore[call-arg]
            ...
