from __future__ import annotations

from typing import Any, ClassVar, Final

import pytest
from typing_extensions import Self

from bakery import Bakery, Cake, __Cake__


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


class FileBakerySeq(Bakery):
    _file_obj: FileWrapper = Cake(FileWrapper, "hello.txt")
    file_obj: FileWrapper = Cake(_file_obj)
    write_1_bytes: int = Cake(file_obj.write, "hello, ")
    write_2_bytes: int = Cake(file_obj.write, "world")


class FileBakery(Bakery):
    file_obj: FileWrapper = Cake(Cake(FileWrapper, "hello.txt"))
    write_1_bytes: int = Cake(file_obj.write, "hello, ")
    write_2_bytes: int = Cake(file_obj.write, "world")


class FileBakeryMap(Bakery):
    file_obj: FileWrapper = Cake(Cake(FileWrapper, "hello.txt"))
    strs_to_write: list[str] = Cake(["hello, ", "world"])
    _: list[int] = Cake(list, Cake(map, file_obj.write, strs_to_write))


class FileBakeryMapWithParams(Bakery):
    filename: str = __Cake__()
    strs_to_write: list[str] = __Cake__()
    file_obj: FileWrapper = Cake(Cake(FileWrapper, filename))
    _: list[int] = Cake(list, Cake(map, file_obj.write, strs_to_write))


@pytest.mark.parametrize(
    ("bakery_cls", "kwargs"),
    [
        (FileBakerySeq, {}),
        (FileBakery, {}),
        (FileBakeryMap, {}),
        (
            FileBakeryMapWithParams,
            {"filename": "hello.txt", "strs_to_write": ["hello, ", "world"]},
        ),
    ],
)
async def test_file_example_1(bakery_cls: Any, kwargs: dict) -> None:
    assert FileWrapper.file_opened is False
    assert FileWrapper.write_lines == []
    async with FileBakeryMapWithParams(
        filename="hello.txt", strs_to_write=["hello, ", "world"]
    ) as bakery:
        ...
    async with bakery_cls(**kwargs) as bakery:
        assert bakery.file_obj.filename == "hello.txt"
        assert FileWrapper.file_opened is True
        assert FileWrapper.write_lines == ["hello, ", "world"]

    assert FileWrapper.file_opened is False
    assert FileWrapper.write_lines == []
