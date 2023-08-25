from __future__ import annotations

from vistral.command_bus.command import TCommand
from vistral.core.exceptions import VistralError


class CommandAlreadyRegisteredError(VistralError):
    @classmethod
    def for_command(cls, command_cls: type[TCommand], /) -> CommandAlreadyRegisteredError:
        return cls(f"Command handler for {command_cls.__name__} already registered.")


class CommandHandlerNotExists(VistralError):
    @classmethod
    def for_command(cls, command_cls: type[TCommand], /) -> CommandHandlerNotExists:
        return cls(f"Command handler for {command_cls.__name__} does not exist.")
