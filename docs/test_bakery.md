# Test Bakery
It is recommended to use pytest framework to test your bakeries. Fresh Bakery appreciate the usage of pytest framework: you can use `bakery_mock` fixture out of the box.

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

## Patch before bakery opened
Let's see hot to use `bakery_mock` fixture to test your bakery.
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


# file test_example.py
from bakery import Cake
from bakery.testbakery import BakeryMock
from example import MyBakery


async def test_example_1(bakery_mock: BakeryMock) -> None:
    bakery_mock.dsn = Cake("fake dsn")  # <<< patch dsn
    async with bakery_mock(MyBakery):  # <<< mock against MyBakery
        assert MyBakery().dsn == "fake dsn"
        assert MyBakery().settings.dsn == "fake dsn"
```
In this example we patch `dsn` attribute (of any bakery) and then bind `bakery_mock` with the real bakery `MyBakery`.

!!! note
    Note that bacause of we patch `dsn` attribute **BEFORE** bakery opened, all depending cakes are also becoming patched. In the example above `settings` cake are also patched with fake dsn.

## Patch after bakery opened
You could also patch attributes **after** bakery was opened. But you should realize that the cake patched is the only thing that will be patched.

```python
# file test_example.py


async def test_example_2(bakery_mock: BakeryMock) -> None:
    await MyBakery.aopen()  # open bakery anywhere

    bakery_mock.dsn = Cake("fake dsn")
    async with bakery_mock(MyBakery):
        assert MyBakery().dsn == "fake dsn"  # patched
        assert MyBakery().settings.dsn == "real dsn"  # not patched

    await MyBakery.aclose()  # close anywhere
```
Note that unlike the `test_example_1` example, in the `test_example_2` we patch `MyBakery` bakery after the bakery is opened. It means, that cake `settings` is already baked and its `.dsn` value is `"real dsn"`.

## Patch hand made cakes
Hand made cakes are also supported:
```python
# file test_example.py
from bakery import hand_made, BakingMethod


async def test_example_3(bakery_mock: BakeryMock) -> None:
    bakery_mock.settings = hand_made(
        Cake(list),
        cake_baking_method=BakingMethod.BAKE_NO_BAKE,
    )
    async with bakery_mock(MyBakery):
        assert MyBakery().settings is list
```

## Unittest
You surely could patch the whole cakes with the unittest. All cake's dependencies patching may be a little bit tricky. But don't give up and continue experimenting.   
Or just move to pytest ;)
