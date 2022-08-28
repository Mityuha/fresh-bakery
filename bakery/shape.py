"""Empty cake shape.
For future purposes (maybe).

Goal: Pass arguments to dependent bakery.
case 1: # <-----
Main bakery defines settings. Only once, it's required.
Also main bakery has dependent bakery.
So, main bakery passes some settings to dependent bakery.
case2:  # <-----
Main bakery initializes dependent bakery 1 and dependent bakery 2.
So from dependent bakery 1 pass some cakes to dependent bakery 2.
Perfect impl:
    class MyBakery(Bakery):
        some_field: int
        ya_field: str
        my_class: Cake = Cake(MyClass, some_field, ya_field)
"""


# __all__ = ["Shape"]
#
# from typing import Any, Generic, Optional, Protocol, TypeVar, cast
#
# from .piece_of_cake import PieceOfCake
# from .stuff import CakeRecipe
#
#
# T = TypeVar("T")
#
#
# class CakeType(Protocol):
#    """cake protocol."""
#
#    def __call__(self):
#        ...
#
#    def __getattr__(self, piece_name: str) -> Any:
#        ...
#
#    def __getitem__(self, piece_name: Any) -> Any:
#        ...
#
#    async def __aenter__(self) -> Any:
#        ...
#
#    async def __aexit__(self, *_args: Any) -> None:
#        ...
#
#    async def bake(self) -> Any:
#        """bake."""
#
#    async def unbake(self, *_args: Any) -> None:
#        """unbake."""
#
#    def __set_name__(self, _, name: str) -> None:
#        ...
#
#
# class ShapeType(Protocol):
#    """shape protocol."""
#
#    _cake: Optional[CakeType]
#
#
# def assert_filled(shape: ShapeType) -> None:
#    """assert shape is filled."""
#    if shape._cake is None:
#        raise ValueError(f"{shape} is not filled. Just fill it with any cake!")
#
#
# def casted_cake(shape: ShapeType) -> CakeType:
#    """assert shape is filled and return shape cake."""
#    assert_filled(shape)
#    return cast(CakeType, shape._cake)
#
#
# class Shape(CakeRecipe, Generic[T]):
#    """Shape for baking."""
#
#    def __init__(self):
#        self._name: str = ""
#        self._cake: Optional[CakeType] = None
#
#    def __set_name__(self, _, name: str) -> None:
#        """shape name."""
#        self._name = name
#
#    def __repr__(self) -> str:
#        """repr."""
#        name: str = self._name or "<anon>"
#        return f"Shape '{name}'"
#
#    def __call__(self) -> T:
#        return casted_cake(self).__call__()
#
#    def __getattr__(self, piece_name: str) -> PieceOfCake:
#        return PieceOfCake(self).__getattr__(piece_name)
#
#    def __getitem__(self, piece_name: str) -> PieceOfCake:
#        return PieceOfCake(self).__getitem__(piece_name)
#
#    async def __aenter__(self) -> Any:
#        return await self.bake()
#
#    async def __aexit__(self, *args: Any) -> Any:
#        return await self.unbake(*args)
#
#    async def bake(self) -> Any:
#        """bake cake in shape."""
#        return await casted_cake(self).bake()
#
#    async def unbake(self, *args: Any) -> None:
#        """unbake cake in shape."""
#        return await casted_cake(self).unbake(*args)
#
#    def __cake(self, cake: CakeType) -> None:
#        """set cake."""
#        if self._cake is not None:
#            raise ValueError(f"{self} is already filled.")
#        if not isinstance(cake, CakeRecipe):
#            raise ValueError(f"You only can fill {self} with a cake, not {type(cake)}")
#        cake.__set_name__(self, self._name)
#        self._cake = cake
#
#    cake = property(fget=None, fset=__cake)
