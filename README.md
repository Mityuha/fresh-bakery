
<p align="center">
  <a href="https://fresh-bakery.readthedocs.io/en/latest/"><img width="300px" src="https://github.com/Mityuha/fresh-bakery/assets/17745407/9ad83683-03dc-43af-b66f-f8a010bde264" alt='fresh-bakery'></a>
</p>
<p align="center">
    <em>🍰 The little DI framework that tastes like a cake. 🍰</em>
</p>

---

**Documentation**: [https://fresh-bakery.readthedocs.io/en/latest/](https://fresh-bakery.readthedocs.io/en/latest/)

---

# Fresh Bakery

Fresh bakery is a lightweight [Dependency Injection][DI] framework/toolkit,
which is ideal for building object dependencies in Python.

It is [nearly] production-ready, and gives you the following:

* A lightweight, stupidly simple DI framework.
* Fully asynchronous, no synchronous mode.
* Any async backends compatible (`asyncio`, `trio`).
* Zero dependencies.
* `Mypy` compatible (no probably need for `# type: ignore`).
* `FastAPI` fully compatible.
* `Litestar` compatible.
* `Pytest` fully compatible (Fresh Bakery encourages the use of `pytest`).
* Ease of testing.
* Easily extended (contribution is welcome).

## Requirements

Python 3.8+

## Installation

```shell
$ pip3 install fresh-bakery
```

## Examples

### Quickstart
This example is intended to show the nature of Dependency Injection and the ease of use the library. Many of us work 8 hours per day on average, 5 days a week, i.e. ~ 40 hours per week. Let's describe it using DI and bakery:
```python
from bakery import Bakery, Cake


def full_days_in(hours: int) -> float:
    return hours / 24


def average(total: int, num: int) -> float:
    return total / num


class WorkingBakery(Bakery):
    average_hours: int = Cake(8)
    week_hours: int = Cake(sum, [average_hours, average_hours, 7, 9, average_hours])
    full_days: float = Cake(full_days_in, week_hours)


async def main() -> None:
    async with WorkingBakery() as bakery:
        assert bakery.week_hours == 40
        assert bakery.full_days - 0.00001 < full_days_in(40)
        assert int(bakery.average_hours) == 8
```
You can see it's simple as it can be.

### One more example
Let's suppose we have a thin wrapper around file object.
```python
from typing import ClassVar, Final

from typing_extensions import Self


class FileWrapper:
    file_opened: bool = False
    write_lines: ClassVar[list[str]] = []

    def __init__(self, filename: str) -> None:
        self.filename: Final = filename

    def write(self, line: str) -> int:
        type(self).write_lines.append(line)
        return len(line)

    def __enter__(self) -> Self:
        type(self).file_opened = True
        return self

    def __exit__(self, *_args: object) -> None:
        type(self).file_opened = False
        type(self).write_lines.clear()
```
This wrapper acts exactly like a file object: it can be opened, closed, and can write line to file.
Let's open file `hello.txt`, write 2 lines into it and close it. Let's do all this with the bakery syntax:
```python
from bakery import Bakery, Cake


class FileBakery(Bakery):
    _file_obj: FileWrapper = Cake(FileWrapper, "hello.txt")
    file_obj: FileWrapper = Cake(_file_obj)
    write_1_bytes: int = Cake(file_obj.write, "hello, ")
    write_2_bytes: int = Cake(file_obj.write, "world")


async def main() -> None:
    assert FileWrapper.file_opened is False
    assert FileWrapper.write_lines == []
    async with FileBakery() as bakery:
        assert bakery.file_obj.filename == "hello.txt"
        assert FileWrapper.file_opened is True
        assert FileWrapper.write_lines == ["hello, ", "world"]

    assert FileWrapper.file_opened is False
    assert FileWrapper.write_lines == []
```
Maybe you noticed some strange things concerning `FileBakery` bakery:
1. `_file_obj` and `file_obj` objects. Do we need them both?
2. Unused `write_1_bytes` and `write_2_bytes` objects. Do we need them?

Let's try to fix both cases. First, why do we need `_file_obj` and `file_obj` objects?
- The first `Cake` initiates `FileWrapper` object, i.e. calls `__init__` method;
- the second `Cake` calls context-manager, i.e. `__enter__` method.

Actually, we can merge these two statements into single one:
```python
# class FileBakery(Bakery):
    file_obj: FileWrapper = Cake(Cake(FileWrapper, "hello.txt"))
```
What about unused arguments? OK, let's re-write this gist a little bit. First, let's declare the list of strings we want to write:
```python
# class FileBakery(Bakery):
    strs_to_write: list[str] = Cake(["hello, ", "world"])
```
How to apply function to every string in this list? There are several ways to do it and one of these is built-in [`map`](https://docs.python.org/3/library/functions.html#map) function.
```python
map_cake = Cake(map, file_obj.write, strs_to_write)
```
But `map` function returns iterator and we need to yield from it. Let's apply `list` function to do it.
```python
list_cake = Cake(list, map_cake)
```
In the same manner as we did with `file_obj` let's merge these two statements into one. The final `FileBakery` will be look like this:
```python
class FileBakeryMap(Bakery):
    file_obj: FileWrapper = Cake(Cake(FileWrapper, "hello.txt"))
    strs_to_write: list[str] = Cake(["hello, ", "world"])
    _: list[int] = Cake(list, Cake(map, file_obj.write, strs_to_write))
```
The last thing nobody likes is hard-coded strings! In this case such strings are:
- the name of the file `hello.txt`
- list of strings to write: `hello, ` and `world`

What if we've got another filename or other strings to write? Let's define filename and list of strings to write as `FileBakery` parameters:
```python
from bakery import Bakery, Cake, __Cake__


class FileBakery(Bakery):
    filename: str = __Cake__()
    strs_to_write: list[str] = __Cake__()
    file_obj: FileWrapper = Cake(Cake(FileWrapper, filename))
    _: list[int] = Cake(list, Cake(map, file_obj.write, strs_to_write))
```
To define parameters one can use dunder-cake construction: `__Cake__()`.   
To pass arguments into `FileBakery` one can you native python syntax:
```python
async def main() -> None:
    ...
    async with FileBakeryMapWithParams(
        filename="hello.txt", strs_to_write=["hello, ", "world"]
    ) as bakery:
        ...
```
and the whole example will look like this:
```python
from bakery import Bakery, Cake, __Cake__


class FileBakery(Bakery):
    filename: str = __Cake__()
    strs_to_write: list[str] = __Cake__()
    file_obj: FileWrapper = Cake(Cake(FileWrapper, filename))
    _: list[int] = Cake(list, Cake(map, file_obj.write, strs_to_write))


async def main() -> None:
    assert FileWrapper.file_opened is False
    assert FileWrapper.write_lines == []
    async with FileBakeryMapWithParams(
        filename="hello.txt", strs_to_write=["hello, ", "world"]
    ) as bakery:
        assert bakery.file_obj.filename == "hello.txt"
        assert FileWrapper.file_opened is True
        assert FileWrapper.write_lines == ["hello, ", "world"]

    assert FileWrapper.file_opened is False
    assert FileWrapper.write_lines == []
```

## Dependencies

No dependencies ;)

## Changelog
You can see the release history here: https://github.com/Mityuha/fresh-bakery/releases/

---

<p align="center"><i>Fresh Bakery is <a href="https://github.com/Mityuha/fresh-bakery/blob/main/LICENSE">MIT licensed</a> code.</p>
