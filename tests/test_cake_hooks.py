"""test cake hooks."""

# from bakery import Bakery, Cake
#
#
# async def test_bakery_cake_hooks() -> None:
#    """test hooks."""
#
#    class Car:
#        """Car."""
#
#        def __init__(self):
#            self.turned_on: bool = False
#
#        def turn_on(self) -> None:
#            """turn engine on."""
#            assert not self.turned_on
#            self.turned_on = True
#
#        def turn_off(self) -> None:
#            """turn engine off."""
#            assert self.turned_on
#            self.turned_on = False
#
#        async def aturn_on(self) -> None:
#            """turn engine on."""
#            return self.turn_on()
#
#        def aturn_off(self) -> None:
#            """turn engine off."""
#            return self.turn_off()
#
#    class Garage(Bakery):
#        """garage."""
#
#        ready_car1: Cake[Car] = Cake(
#            Car,
#            context_methods=("turn_on", "turn_off"),
#            cake_from_sync_context=False,
#            cake_from_async_context=False,
#        )
#        ready_car2: Cake[Car] = Cake(
#            Car,
#            context_methods=("aturn_on", "aturn_off"),
#            cake_from_sync_context=False,
#            cake_from_async_context=False,
#        )
#
#    garage = await Garage.aopen()
#
#    assert garage.ready_car1.turned_on
#    assert garage.ready_car2.turned_on
#
#    await Garage.aclose()
#
#    assert not garage.ready_car1.turned_on
#    assert not garage.ready_car2.turned_on
#
#
## async def test_cake_from_hook() -> None:
##    """test cake from hook."""
##
##    class Box:
##        """box."""
##
##        def __init__(self, close_expected: bool = True):
##            self.close_expected: bool = close_expected
##
##        def open(self) -> str:
##            """return something."""
##            return "money"
##
##        def close(self) -> None:
##            """close."""
##            assert self.close_expected
##
##        async def aopen(self) -> str:
##            """return something different."""
##            return "car"
##
##        async def aclose(self) -> None:
##            """aclose."""
##            assert self.close_expected
##
##    class Boxer(Bakery):
##        """boxer."""
##
##        box_open_close: Cake[str] = Cake(Box)
##        box_open_aclose: Cake[str] = Cake(Box)
##        box_open_not_closed: Cake[str] = Cake(Box, close_expected=False)
##
##        box_aopen_aclose: Cake[str] = Cake(Box)
##        box_aopen_close: Cake[str] = Cake(Box)
##        box_aopen_not_closed: Cake[str] = Cake(Box, close_expected=False)
##
##    async with Boxer() as boxer:
##        for box in [
##            boxer.box_open_close,
##            boxer.box_open_aclose,
##            boxer.box_open_not_closed,
##        ]:
##            assert box == "money"
##
##        for box in [boxer.box_aopen_aclose, boxer.box_aopen_close, boxer.aopen_not_closed]:
##            assert box == "car"
