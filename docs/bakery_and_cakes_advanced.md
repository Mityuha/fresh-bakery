# About Bakery and Cakes (Advanced)

Some advanced things about bakery and cakes could be useful to know.

## Cakes under the hood. Pastry
Strictly speaking, all type annotations you've seen above (and would see below) within bakery are the deception. `Cake` is just the function that returns a value. The reason why mypy is feeling good -- overloaded functions. But in runtime `Cake` function returns object, that wrapps the real value. Such an object called `Pastry`:
```python
from Bakery import Cake

val: int = Cake(1)
print(type(val))  # <<< <class 'bakery.cake.Pastry'>
```
`Pastry`s are always baked and unbaked under the bakery's hood on bakery open/close events.   

## Cakes under the hood. Piece of Cake
Now we know that all bakery's objects are `Pastry` objects. And any `Pastry`'s attribute is piece of pastry or `PieceOfCake`:
```python
from Bakery import Cake

val: int = Cake(1)
print(type(val.a))  # <<< <class 'bakery.piece_of_cake.PieceOfCake'>
print(type(val.a.b.c)) # <<< <class 'bakery.piece_of_cake.PieceOfCake'>
print(val.a["key"].c)  # <<< Cake '<anon>'.a[key].c
```
When you try to get `Pastry`'s attribute or item you always receive a `PieceOfCake` object. No matter what attributes/items you try receive. `PieceOfCake` object just "remember" the order of operations. And sometime in the future it will be an error if the real object has no attribute/item.

## Baking pastry and piece of cake
`Pastry` and `PieceOfCake` objects are both callable objects. `Pastry` object is either async context manager. But in context of baking it does not matter. The algorithm of baking such objects is the following:  

1. Check if object to bake is `Pastry` or `PieceOfCake`
2. If so
    - bake such an object
    - call such an object
    - replace object to bake with the result returned
3. Bake object.

Roughly equivalent to:
```python
from typing import Any
from bakery import Pastry, PieceOfCake

async def bake(recipe: Any) -> Any:
    if isinstance(recipe, (Pastry, PieceOfCake)):
        await bake(recipe)  # recursion here
        recipe = recipe()
    
    # bake recipe here
```

## The lifetime of anonymous cakes
Anonymous cake are just a cake without a name
```python
from bakery import Bakery, Cake

class MyBakery(Bakery):
    int_val: int = Cake(Cake(1))
```
In this example, the external cake is the named cake: its name is `int_val`. While the internal cake `Cake(1)` is anonymous.   
All anonymous cakes inside the named cake belong to the named cake. Maybe the only thing it means is that the named cake manages the lifetime of anonymous cakes that belong to it.    
Even if you bake anonymous cake before passing it to the named cake, the anonymous cake would be unbaked at the time when the named caked would.
```python
from bakery import Bakery, Cake, bake, is_baked

anon_cake: int = Cake(1)
await bake(anon_cake)
assert is_baked(anon_cake)

class MyBakery(Bakery):
    int_val: int = Cake(anon_cake)

async with MyBakery() as bakery:
    assert bakery.int_val == 1  d

# anon_cake is implicitly unbaked here
assert not is_baked(anon_cake)
```


