# from typing import Any, Callable, Optional

from mypy.plugin import Plugin

# from mypy.types import FunctionLike


class VistralPlugin(Plugin):
    pass
    # def get_method_signature_hook(self, fullname: str) -> Optional[Callable[[MethodSigContext], FunctionLike]]:
    #     if all(x in fullname for x in ["vistral", "handle"]):
    #         return self._investigator
    #     return None
    #
    # def get_customize_class_mro_hook(self, fullname: str) -> Optional[Callable[[ClassDefContext], None]]:
    #     if all(x in fullname for x in ["vistral", "Bus"]):
    #         return self._investigator
    #     return None
    #
    # def _investigator(self, *args, **kwargs) -> Any:
    #     breakpoint()


def plugin(version: str) -> type[Plugin]:
    return VistralPlugin
