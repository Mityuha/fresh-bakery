# Test Bakery
Let's suppose we have class `Settings` and bakery `MyBakery`:
```python
# file example.py
from dataclasses import dataclass
from bakery import Bakery, Cake


@dataclass
class Settings:
    dsn: str


class MyBakery(Bakery):
    dsn: str = Cake("real dsn")
    settings: Settings = Cake(Settings, dsn=dsn)
```
Let's consider two approaches for bakery testing: framework agnostic and pytest related approaches.

## Framework agnostic approach
Use can override any bakery member by passing argument for it to bakery:
```python
from .example import MyBakery


async def test_example_1_no_mocks() -> None:
    async with MyBakery(dsn="fake dsn"):  # <<< pass new dsn value
        assert MyBakery().dsn == "fake dsn"
        assert MyBakery().settings.dsn == "fake dsn"
```
No particular framework required for it. It just works as expected and out-of-the-box.    
The only downside of this approach is that you can't pass new arguments if bakery's been already opened:
```python
import pytest

from .example import MyBakery


async def test_example_1_cant_pass_after_open() -> None:
    await MyBakery.aopen()

    with pytest.raises(TypeError):
        async with MyBakery(dsn="fake dsn"):  # <<< passing new arguments after open is prohibited
            ...

    await MyBakery.aclose()
```
If for some reason you need to override bakery's member **after** opening, please use pytest related approach.

## Pytest related approach
Fresh Bakery appreciate the usage of pytest framework: you can use `bakery_mock` fixture out-of-the-box.

!!! note
    To use `bakery_mock` fixture you have to also install pytest-mock library (besides pytest itself):
    ```bash
    $ pip install pytest-mock
    ```

!!! info
    `bakery_mock` is a function-scoped fixture. There are also other fixtures with different fixture scopes:   

    - `class_bakery_mock` is a class-scoped fixture
    - `module_bakery_mock` is a module-scoped fixture
    - `package_bakery_mock` is a package-scoped fixture
    - `session_bakery_mock` is a session-scoped fixture

### Patch before bakery opened
Let's see how to use `bakery_mock` fixture to test your bakery.
```python
# file test_example.py
from bakery import Cake
from bakery.testbakery import BakeryMock

from .example import MyBakery


async def test_example_1(bakery_mock: BakeryMock) -> None:
    bakery_mock.dsn = Cake("fake dsn")  # <<< patch dsn
    async with bakery_mock(MyBakery):  # <<< mock against MyBakery
        assert MyBakery().dsn == "fake dsn"
        assert MyBakery().settings.dsn == "fake dsn"
```
In this example we patch `dsn` attribute (of any bakery) and then bind `bakery_mock` with the real bakery `MyBakery`.

!!! note
    Note that bacause of we patch `dsn` attribute **BEFORE** bakery opened, all depending cakes are also becoming patched. In the example above `settings` cake are also patched with fake dsn.

### Patch after bakery opened
You could also patch attributes **after** bakery was opened. But you should realize that the cake patched is the only thing that will be patched.

```python
# file test_example.py
from bakery import Cake
from bakery.testbakery import BakeryMock

from .example import MyBakery


async def test_example_2(bakery_mock: BakeryMock) -> None:
    await MyBakery.aopen()  # open bakery anywhere

    bakery_mock.dsn = Cake("fake dsn")
    async with bakery_mock(MyBakery):
        assert MyBakery().dsn == "fake dsn"  # patched
        assert MyBakery().settings.dsn == "real dsn"  # not patched

    await MyBakery.aclose()  # close anywhere
```
Note that unlike the `test_example_1` example, in the `test_example_2` we patch `MyBakery` bakery **after** the bakery is opened. It means the cake `settings` is already baked and its `.dsn` value is `"real dsn"`.

### Patch hand made cakes
Hand made cakes are also supported:
```python
# file test_example.py
from bakery import Bakery, BakingMethod, Cake, hand_made
from bakery.testbakery import BakeryMock

from .example import MyBakery


async def test_example_3(bakery_mock: BakeryMock) -> None:
    bakery_mock.settings = hand_made(
        Cake(list),
        cake_baking_method=BakingMethod.BAKE_NO_BAKE,
    )
    async with bakery_mock(MyBakery):
        assert MyBakery().settings is list
```
