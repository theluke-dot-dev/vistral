from typing import Any

from vistral.commandbus.command import Command, CommandHandler, TCommand, TCommandResult
from vistral.commandbus.exceptions import CommandAlreadyRegisteredError, CommandHandlerNotExists
from vistral.commandbus.resolver import DefaultResolver, Resolver


class CommandBus:
    def __init__(self, resolver: Resolver = DefaultResolver()):
        self._resolver = resolver
        self._handlers: dict[type[Command], type[CommandHandler]] = {}

    def register(
        self,
        command_type: type[TCommand],
        handler_type: type[CommandHandler[TCommand, TCommandResult]],
    ) -> None:
        if command_type in self._handlers:
            raise CommandAlreadyRegisteredError(command_cls=command_type)

        self._handlers[command_type] = handler_type

    def handle(self, command: TCommand) -> Any:
        command_cls = type(command)
        try:
            handler_cls = self._handlers[command_cls]
        except KeyError:
            raise CommandHandlerNotExists(command_cls=command_cls)

        handler = self._resolver.resolve_command_handler(handler_cls=handler_cls)
        return handler.handle(command=command)
