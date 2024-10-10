from enum import IntEnum

from bakery import recipe_format


class Foo:
    def bar(self) -> None: ...


class SEnum(IntEnum):
    A = 1


def test_recipe_format() -> None:
    assert recipe_format(Foo(), SEnum.A) == "Foo[A]"

    assert recipe_format(Foo, SEnum.A) == "Foo[A]"
    assert recipe_format(Foo.bar, SEnum.A) == "Foo.bar[A]"
    assert recipe_format(Foo().bar, SEnum.A) == "Foo.bar[A]"
    assert recipe_format(42, SEnum.A) == "int[A]"
