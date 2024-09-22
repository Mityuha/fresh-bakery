"""Test bakery."""

from __future__ import annotations

import warnings
from inspect import Parameter, Signature
from typing import TYPE_CHECKING, Any, AsyncIterator, Type

import pytest

from . import Bakery as _Bakery
from . import (
    Cake,
    Cakeable,
    cake_baking_method,
    cake_recipe,
    cake_recipe_args,
    cake_recipe_kwargs,
    is_cake,
    unbake,
)

if TYPE_CHECKING:
    from pytest_mock import MockerFixture

Bakery = Type[_Bakery]


def fixture_factory(mocker_name: str) -> Any:
    """Create bakery mock fixtures by mocker name."""

    async def mocker(**kwargs: Any) -> AsyncIterator[BakeryMock]:
        if not all((len(kwargs) == 1, next(iter(kwargs.keys())).endswith("mocker"))):
            msg: str = "Please, pass mocker fixture."
            raise ValueError(msg)

        mock: BakeryMock = BakeryMock(next(iter(kwargs.values())))
        yield mock
        await mock.stopall()

    mocker.__signature__ = Signature(  # type: ignore[attr-defined]
        [
            Parameter(
                mocker_name,
                kind=Parameter.KEYWORD_ONLY,
            ),
        ],
    )
    return mocker


bakery_mock = pytest.fixture()(fixture_factory("mocker"))
class_bakery_mock = pytest.fixture(scope="class")(fixture_factory("class_mocker"))
module_bakery_mock = pytest.fixture(scope="module")(fixture_factory("module_mocker"))
package_bakery_mock = pytest.fixture(scope="package")(fixture_factory("package_mocker"))
session_bakery_mock = pytest.fixture(scope="session")(fixture_factory("session_mocker"))


class BakeryMock:
    """Toy bakery."""

    def __init__(self, mocker: MockerFixture) -> None:
        self._mocker_: MockerFixture = mocker
        self._cake_mocks_: dict[str, Cakeable[Any]] = {}
        self._bakery_: Bakery | None = None
        self._children_: list[BakeryMock] = []

    def __copy__(self) -> BakeryMock:
        """Copy bakery mock."""
        mock_copy: BakeryMock = BakeryMock(self._mocker_)
        self._children_.append(mock_copy)
        return mock_copy

    async def _patch_cake(
        self,
        *,
        bakery: Bakery,
        cake: Cakeable[Any],
        new_recipe: Cakeable[Any],
    ) -> None:
        """Patch cake recipe."""
        if not all((is_cake(cake), is_cake(new_recipe), issubclass(bakery, _Bakery))):
            raise ValueError

        new_cake: Cakeable[Any] = new_recipe
        self._mocker_.patch.multiple(
            cake,
            _Pastry__cake_recipe=cake_recipe(new_cake),
            _Pastry__cake_recipe_args=cake_recipe_args(new_cake),
            _Pastry__cake_recipe_kwargs=cake_recipe_kwargs(new_cake),
            _Pastry__cake_baking_method=cake_baking_method(new_cake),
            _Pastry__cake_result=await new_cake.__aenter__(),
        )

    async def _patch(self, bakery: Bakery) -> None:
        """Start bakery `bakery` patching."""
        if not issubclass(bakery, _Bakery):
            msg: str = f"{bakery} is not a Bakery."
            raise TypeError(msg)

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
            msg: str = f"Old bakery {self._bakery_} is still set. Close it first."
            raise ValueError(msg)
        return await self._patch(bakery)

    def __call__(self, bakery: Bakery) -> BakeryMock:
        if self._bakery_ is not None:
            msg: str = f"Old bakery {self._bakery_} is still set. Close it first."
            raise ValueError(msg)
        self._bakery_ = bakery
        return self

    async def __aenter__(self) -> None:
        if self._bakery_ is None:
            msg: str = "You should set bakery first."
            raise ValueError(msg)
        return await self._patch(self._bakery_)

    async def __aexit__(self, *_args: object) -> None:
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

        if not is_cake(value):
            warnings.warn(
                "Direct value assignment to bakery_mock is deprecated and will be removed soon. "
                "Please, use bakery_mock.attr = Cake(value) notation.",
                stacklevel=2,
            )
            value = Cake(value)
        self._cake_mocks_[attr] = value
        return None

    async def stopall(self) -> None:
        """Reset mocker and clear piece mocks."""
        await self.reset()
        for cake in self._cake_mocks_.values():
            await unbake(cake)

        for child in self._children_:
            await child.stopall()

        self._cake_mocks_.clear()
        self._children_.clear()
