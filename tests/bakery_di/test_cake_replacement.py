import contextlib

import pytest

from bakery import Pastry


async def test_cake_replacement_before_bake() -> None:
    value = 1
    replace_with = 2
    cake = Pastry(value)
    async with cake:
        assert cake() == value

    with cake.__cake_replace__(replace_with):
        async with cake:
            assert cake() == replace_with


async def test_cake_replacement_after_bake_is_prohibited() -> None:
    """Such a behaviour is prohibited here's why.

    - Suppose the cake was baked
    - We want to replace it with another cake
    - Should we rebake the cake at the time of replacement?
    - What if a new cake cannot be baked?
    - and so on.
    """
    value = 1
    replace_with = 2
    cake = Pastry(value)

    async with cake:
        with pytest.raises(TypeError, match="Cannot replace cake (.*) that's already baked"):
            cake.__cake_replace__(replace_with).__enter__()
        assert cake() == value


async def test_multiple_replacements_are_prohibited() -> None:
    value = 1
    replace_with = 2
    cake = Pastry(value)

    with cake.__cake_replace__(replace_with):
        with pytest.raises(
            TypeError, match="Cannot replace cake (.*) that's already replaced"
        ), cake.__cake_replace__(replace_with):
            ...

        async with cake:
            assert cake() == replace_with


async def test_cake_replacement_rollback_after_exception() -> None:
    value = 1
    replace_with = 2
    cake = Pastry(value)

    with contextlib.suppress(AttributeError), cake.__cake_replace__(replace_with):
        async with cake:
            assert cake() == replace_with
            msg = "Some attribute error occured"
            raise AttributeError(msg)

    async with cake:
        assert cake() == value
