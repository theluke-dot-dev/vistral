from vistral.command_bus.command import BoundCommandHandlerType, CommandType, TCommand
from vistral.command_bus.exceptions import CommandAlreadyRegisteredError, CommandHandlerNotExists
from vistral.command_bus.resolver import CommandHandlerResolver, DefaultResolver


class CommandBus:
    def __init__(self, resolver: CommandHandlerResolver = DefaultResolver()):
        self._resolver = resolver
        self._handlers: dict[CommandType, BoundCommandHandlerType] = {}

    def register(self, command_type: CommandType, handler_type: BoundCommandHandlerType) -> None:
        if command_type in self._handlers:
            raise CommandAlreadyRegisteredError.for_command(command_type)

        self._handlers[command_type] = handler_type

    def handle(self, command: TCommand) -> None:
        command_type = type(command)
        try:
            handler_cls = self._handlers[command_type]
        except KeyError:
            raise CommandHandlerNotExists.for_command(command_type)

        handler = self._resolver.resolve_command_handler(handler_cls)
        return handler(command=command)
