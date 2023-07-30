from abc import ABC, abstractmethod

from vistral.command_bus.command import CommandHandler, TCommand


class Resolver(ABC):
    @abstractmethod
    def resolve_command_handler(self, handler_cls: type[CommandHandler[TCommand]]) -> CommandHandler[TCommand]:
        pass


class DefaultResolver(Resolver):
    def resolve_command_handler(self, handler_cls: type[CommandHandler[TCommand]]) -> CommandHandler[TCommand]:
        return handler_cls()
