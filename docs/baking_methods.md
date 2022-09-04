# Baking Methods

Bakery cakes are smart enough to determine what you do want to do. That's because cake automatically determines baking method using which the cake will be baked.

## Bake from built-in

If you will define cake with constant built-in type value, value will remain untouched:

```python
from bakery import Bakery, Cake

class MyBakery(Bakery):
    bytes_const: bytes = Cake(b"bytes")
    list_const: list[int] = Cake([1, 2, 3])

async with MyBakery() as bakery:
    assert bakery.bytes_const == b"bytes"
    assert bakery.list_const == [1, 2, 3]
```

## Bake from callable

If you will define cake with any callable object and provide all positional and keywords arguments to it, the value will be equal to return value of that callable object:

```python
from bakery import Bakery, Cake

def plus_one(value: int) -> int:
    return value + 1

class Splitter:
    def __init__(self, value: str, sep: str = "."):
        self.values: list[str] = value.split(sep)
    def __call__(self) -> list[str]:
        return self.values

class MyBakery(Bakery):
    two: int = Cake(plus_one, 1)
    three: int = Cake(plus_one, two)
    splitter: Splitter = Cake(Splitter, "one:two:three", sep=":")
    one_two_three: list[str] = Cake(splitter)

async with MyBakery() as bakery:
    assert bakery.two == 2
    assert bakery.three == 3
    assert bakery.splitter.values == ["one", "two", "three"]
    assert bakery.one_two_three == ["one", "two", "three"]
```

!!! note
    All callable objects' signatures are mypy compatible. In the example above if you will pass string to `plus_one` function or integer as separator to `Splitter` initializer you will get mypy error.

## Bake from (async) context manager

If you will define cake with (async) context manager object, the value will be equal to return value of `__enter__` (`__aenter__`) method:

```python
from contextlib import contextmanager
from dataclasses import dataclass
from typing import Iterator

from bakery import Bakery, Cake

@dataclass
class File:
    is_opened: bool

@contextmanager
def set_opened(file: File) -> Iterator[File]:
    file.is_opened = True
    yield file
    file.is_opened = False

FILE: File = File(is_opened=False)

class MyBakery(Bakery):
    opened_file: File = Cake(set_opened(FILE))

assert not FILE.is_opened

async with MyBakery() as bakery:
    assert bakery.opened_file.is_opened
    assert bakery.opened_file is FILE
    assert FILE.is_opened

assert not FILE.is_opened
```

In this example we defined variable `FILE` as global variable and then passed it to context manager `set_opened`. But what if we want to declare file within bakery and pass it to `set_opened` context manager. Let's try it out:

```python
# imports and statements
# from example above

class MyBakery(Bakery):
    file: File = Cake(File, is_opened=False)
    opened_file: File = Cake(    # <<< Bake from context manager
        Cake(set_opened, file),  # <<< Bake from callable
    )

async with MyBakery() as bakery:
    assert bakery.file.is_opened
    assert bakery.file is bakery.opened_file
    assert bakery.opened_file.is_opened
```

Take a look at the `opened_file` cake. First we baked anonymous cake from callable `set_opened`, passing `file` as argument. And then bake result (`GeneratorContextManager` object) as context manager. In the end we've got the same result as in the example above.

## Bake from coroutine function and any awaitable object

If you will define cake with coroutine object (or any awaitable object), the value will be equal to return value of this object:

```python
from bakery import Bakery, Cake

async def plus_one(value: int) -> int:
    return value + 1

class MyBakery(Bakery):
    two: int = Cake(plus_one(1))      # <<< Bake from awaitable (coroutine)
    three: int = Cake(plus_one, two)  # <<< Bake from coroutine function

async with MyBakery() as bakery:
    assert bakery.two == 2
    assert bakery.three == 3
```

!!! info
    What is difference between `awaitable`, `coroutine function` and `coroutine`?

    - [awaitable](https://docs.python.org/3/library/inspect.html#inspect.isawaitable) is an object that can be used in await expression.
    - [coroutine function](https://docs.python.org/3/library/inspect.html#inspect.iscoroutinefunction) is a function defined with an async def syntax.
    - [coroutine](https://docs.python.org/3/library/inspect.html#inspect.iscoroutine) is a object, created by an async def function (by calling it).

## Bake from ... Do not bake

If you will define cake with any custom object (like custom class), this object will remain untouched. Essentially it's the same case as for built-in constants:

```python
from bakery import Bakery, Cake

class OneKeeper:
    ONE = 1

class MyBakery(Bakery):
    keeper: OneKeeper = Cake(OneKeeper())

async with MyBakery() as bakery:
    assert bakery.keeper.ONE == 1
```

## Baking methods priority and customization

Sometimes you may need to specify custom baking method manually. When can this happen?
Let's suppose, that we have a class, that implement both sync and async context managers.   

From what context manager -- sync or async -- cake would be baked?

!!! info
    Baking methods priority (from checked first to checked last. `Coro Func` is checked first)
    ``` mermaid
    graph LR
    B[Coro Func] --> C[Awaitable] 
    --> D[Async CM] --> E[Sync CM] -->  F[Built-in] 
    --> G[Callable] --> H[No bake]
    ```

The answer is from async context manager, because it is checked first. But what if we need to bake from sync context manager? It could be made by hand ;)

```python
from typing import Any
from bakery import Bakery, BakingMethod, Cake, hand_made

class CmvsAcm:
    def __init__(self):
        self.is_acm: bool = False
        self.is_cm: bool = False

    def __enter__(self) -> "CmvsAcm":
        self.is_cm = True
        return self
    def __exit__(self, *_args: Any) -> None:
        self.is_cm = False
        return None

    async def __aenter__(self) -> "CmvsAcm":
        self.is_acm = True
        return self
    async def __aexit__(self, *_args: Any) -> None:
        self.is_acm = False
        return None

class MyBakery(Bakery):
    acm_wins: CmvsAcm = Cake(CmvsAcm())
    cm_wins: CmvsAcm = hand_made(
        Cake(CmvsAcm()), 
	cake_baking_method=BakingMethod.BAKE_FROM_CM,
    )

async with MyBakery() as bakery:
    assert bakery.acm_wins.is_acm
    assert not bakery.acm_wins.is_cm

    assert bakery.cm_wins.is_cm
    assert not bakery.cm_wins.is_acm
```

In case of `acm_wins` cake it's baked from async context manager, because async context manager has higher priority.   
In cake of `cm_wins` cake it's baked from sync context manager, because `BAKE_FROM_CM` method explicitly specified.

