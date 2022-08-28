"""Bakery mypy plugin.

Make cakeable all bakery items.
"""

from pathlib import Path
from typing import Callable, Optional, Tuple, Type

# pylint: disable=no-name-in-module
from mypy.options import Options
from mypy.plugin import AttributeContext, Plugin
from mypy.types import CallableType, Instance
from mypy.types import Type as MypyType
from typing_extensions import Final


BAKERY_FULLNAME: Final[str] = "bakery.bakery.Bakery"
CAKEABLE_FULLNAME: Final[str] = "bakery.Cakeable"


def plugin(_: str) -> Type[Plugin]:
    """Plugin."""
    return BakeryPlugin


class BakeryPlugin(Plugin):
    """Bakery plugin."""

    def __init__(self, options: Options) -> None:
        super().__init__(options)
        if options.config_file is None:
            return
        # some manipulations on config_file
        # some optimizations here
        self.visible_modules: Final[Tuple[str, ...]] = tuple(
            str(path.with_suffix("")).replace("/", ".") for path in Path().rglob("*.py")
        )

    def get_class_attribute_hook(self, _fullname: str) -> Optional[Callable]:
        """Get class attribute hook."""
        # fullname including attribute name
        # e.g. test_app.bakery.MyBakery.some_cake
        # if _fullname.startswith(self.visible_modules):
        return self.class_attribute_hook

    def class_attribute_hook(self, ctx: AttributeContext) -> MypyType:
        """Attribute context."""
        if not (isinstance(ctx.type, CallableType) and isinstance(ctx.type.ret_type, Instance)):
            return ctx.default_attr_type

        for base in ctx.type.ret_type.type.bases:
            if base.type.fullname == BAKERY_FULLNAME:
                break
        else:
            return ctx.default_attr_type

        if ctx.context.name in ("aopen", "aclose", "__aenter__", "__aexit__"):  # type: ignore
            return ctx.default_attr_type

        smth_inst: Instance = ctx.api.named_type(CAKEABLE_FULLNAME).copy_modified(  # type: ignore
            args=(ctx.default_attr_type,),
        )
        return smth_inst
