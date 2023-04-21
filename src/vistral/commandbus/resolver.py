from abc import ABC, abstractmethod

from vistral.commandbus.command import CommandHandler, TCommand, TCommandResult


class Resolver(ABC):
    @abstractmethod
    def resolve_command_handler(
        self, handler_cls: type[CommandHandler[TCommand, TCommandResult]]
    ) -> CommandHandler[TCommand, TCommandResult]:
        pass


class DefaultResolver(Resolver):
    def resolve_command_handler(
        self, handler_cls: type[CommandHandler[TCommand, TCommandResult]]
    ) -> CommandHandler[TCommand, TCommandResult]:
        return handler_cls()
