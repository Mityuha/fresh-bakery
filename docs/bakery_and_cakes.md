# About Bakery and Cakes

!!! note
    If you want to run examples directly from the console, you may want to use `ipython` here.
    ```shell
    $ pip install ipython
    ```

There are some thing you should know about bakery and cakes.

* Any class inherited from `Bakery` is becoming bakery ;)

## Bakery is monostate

Though such a class is not singleton, but its instances share the same state. It is the Borg/Monostate (anti)pattern just because in Python class variables are shared by all instances. 
```python
from bakery import Bakery, Cake

class MyBakery(Bakery):
    my_list: list[int] = Cake([1,2,3])

async with MyBakery():
    bakery1: MyBakery = MyBakery()
    bakery2: MyBakery = MyBakery()
    assert bakery1 is not bakery2
    assert bakery1.my_list == bakery2.my_list == MyBakery.my_list()
```

## Cakes are singletons

All cakes within bakery are singletons. Cakes are baked once on bakery open and unbaked once on bakery close. But you can easily copy cake once bakery is opened.
!!! info
    After cake is copied you could do anything with it. Just remember, that after cake copy you'll receive a raw cake (pastry). And you need to bake it. See example below.

!!! warning
    Note, that copy is an experimental feature yet. Cake copy is a shallow cake copy (it's going to be changed). Use it with care.

```python
from copy import copy
from dataclasses import dataclass
from bakery import Bakery, Cake, Pastry, bake, unbake

@dataclass
class JsonKeeper:
    json: dict

class MyBakery(Bakery):
    json_keeper: JsonKeeper = Cake(JsonKeeper, json={"value": 42})

async with MyBakery() as bakery:
    keeper_copy: Pastry = copy(MyBakery.json_keeper)  # <<< Note: it's pastry, not cake ;)
    async with keeper_copy:  # <<< bake pastry
        assert keeper_copy().json == bakery.json_keeper.json

    await bake(keeper_copy)  # <<< bake pastry manually
    assert keeper_copy().json == bakery.json_keeper.json
    await unbake(keeper_copy)  # <<< unbake pastry

    keeper_copy()  # <<< raises ValueError. Pastry's not baked
```

## Round brackets anywhere

No matter where you will decide to put parentheses while getting cake/attribute value, the result whould be the same in the end.
```python
from dataclasses import dataclass
from typing import Optional
from bakery import Bakery, Cake

@dataclass
class NestedSettings:
    settings: Optional["NestedSettings"]
    json: dict

class MyBakery(Bakery):
    settings1: NestedSettings = Cake(NestedSettings, settings=None, json={"value": 42})
    settings2: NestedSettings = Cake(NestedSettings, settings=settings1, json={})

async with MyBakery() as bakery:
    assert (
        MyBakery.settings2.settings.json["value"]()
        == MyBakery.settings2.settings.json()["value"]
        == MyBakery.settings2.settings().json["value"]
        == MyBakery.settings2().settings.json["value"]
        == MyBakery().settings2.settings.json["value"]
        == bakery.settings2.settings.json["value"]
        == 42
    )
```
