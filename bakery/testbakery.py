"""Test bakery."""
from inspect import Parameter, Signature
from typing import Any, AsyncIterator, Dict, List, Optional, Type

import pytest
from pytest_mock import MockerFixture

from . import Bakery as _Bakery
from . import (
    Cakeable,
    IngredientsProto,
    bake,
    cake_baking_method,
    cake_ingredients,
    is_cake,
    unbake,
)


Bakery = Type[_Bakery]


def fixture_factory(mocker_name: str) -> Any:
    """Create bakery mock fixtures by mocker name."""

    async def mocker(**kwargs: Any) -> AsyncIterator["BakeryMock"]:
        assert len(kwargs) == 1
        assert list(kwargs.keys())[0].endswith("mocker"), "please, pass mocker fixture."

        mock: BakeryMock = BakeryMock(list(kwargs.values())[0])
        yield mock
        await mock.stopall()

    mocker.__signature__ = Signature(  # type: ignore
        [
            Parameter(
                mocker_name,
                kind=Parameter.KEYWORD_ONLY,
            )
        ]
    )
    return mocker


bakery_mock = pytest.fixture()(fixture_factory("mocker"))
class_bakery_mock = pytest.fixture(scope="class")(fixture_factory("class_mocker"))
module_bakery_mock = pytest.fixture(scope="module")(fixture_factory("module_mocker"))
package_bakery_mock = pytest.fixture(scope="package")(fixture_factory("package_mocker"))
session_bakery_mock = pytest.fixture(scope="session")(fixture_factory("session_mocker"))


class BakeryMock:
    """Toy bakery."""

    def __init__(self, mocker: MockerFixture):
        self._mocker_: MockerFixture = mocker
        self._cake_mocks_: Dict[str, Any] = {}
        self._bakery_: Optional[Bakery] = None
        self._children_: List["BakeryMock"] = []

    def __copy__(self) -> "BakeryMock":
        """Copy bakery mock."""
        mock_copy: BakeryMock = BakeryMock(self._mocker_)
        self._children_.append(mock_copy)
        return mock_copy

    async def _patch_cake(self, *, bakery: Bakery, cake: Cakeable[Any], new_recipe: Any) -> None:
        """Patch cake recipe."""
        assert is_cake(cake)
        assert issubclass(bakery, _Bakery)

        ingredients: IngredientsProto = cake_ingredients(cake)
        if is_cake(new_recipe):
            new_cake: Cakeable[Any] = new_recipe
            self._mocker_.patch.multiple(
                ingredients,
                recipe=cake_ingredients(new_cake).recipe,
                recipe_args=cake_ingredients(new_cake).recipe_args,
                recipe_kwargs=cake_ingredients(new_cake).recipe_kwargs,
                cake_baking_method=cake_baking_method(new_cake),
                result=await bake(new_cake),
            )
        else:
            self._mocker_.patch.multiple(
                ingredients,
                recipe=new_recipe,
                result=new_recipe,
            )

    async def _patch(self, bakery: Bakery) -> None:
        """Start bakery `bakery` patching."""

        if not issubclass(bakery, _Bakery):
            raise ValueError(f"{bakery} is not a Bakery.")

        cake_name: str
        new_recipe: Any

        for cake_name, new_recipe in self._cake_mocks_.items():
            # patch bakery itself
            await self._patch_cake(
                bakery=bakery,
                cake=getattr(bakery, cake_name),
                new_recipe=new_recipe,
            )

        await bakery.aopen()
        self._bakery_ = bakery

    async def patch(self, bakery: Bakery) -> None:
        """Check if bakery set and start patching."""
        if self._bakery_ is not None:
            raise ValueError(f"Old bakery {self._bakery_} is still set. Close it first.")
        return await self._patch(bakery)

    def __call__(self, bakery: Bakery) -> "BakeryMock":
        if self._bakery_ is not None:
            raise ValueError(f"Old bakery {self._bakery_} is still set. Close it first.")
        self._bakery_ = bakery
        return self

    async def __aenter__(self) -> None:
        assert self._bakery_ is not None, "You should set bakery first."
        return await self._patch(self._bakery_)

    async def __aexit__(self, *_args: Any) -> None:
        return await self.reset()

    async def reset(self) -> None:
        """Stop patching."""
        if self._bakery_:
            await self._bakery_.aclose()
            self._bakery_ = None

        self._mocker_.stopall()

    def __setattr__(self, attr: str, value: Any) -> None:
        if attr in (
            "_mocker_",
            "_cake_mocks_",
            "_bakery_",
            "_children_",
        ):
            return super().__setattr__(attr, value)

        self._cake_mocks_[attr] = value
        return None

    async def stopall(self) -> None:
        """Reset mocker and clear piece mocks."""
        await self.reset()
        for cake in self._cake_mocks_.values():
            if is_cake(cake):
                await unbake(cake)

        for child in self._children_:
            await child.stopall()

        self._cake_mocks_.clear()
        self._children_.clear()
