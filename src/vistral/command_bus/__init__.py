from vistral.command_bus.command import BoundCommandHandlerType, CommandType, TCommand
from vistral.command_bus.exceptions import CommandAlreadyRegisteredError, CommandHandlerNotExists
from vistral.command_bus.resolver import CommandHandlerResolver


class CommandBus:
    """
    A command bus that routes commands to their registered handlers.

    :param resolver: The command handler resolver to use for resolving handlers.
    :type resolver: CommandHandlerResolver
    """

    def __init__(self, resolver: CommandHandlerResolver):
        """
        Initializes a new instance of the CommandBus class.

        :param resolver: The command handler resolver.
        :type resolver: CommandHandlerResolver
        """
        self._resolver = resolver
        self._handlers: dict[CommandType, BoundCommandHandlerType] = {}

    def register(self, command_type: CommandType, handler_type: BoundCommandHandlerType) -> None:
        """
        Registers a command handler for a given command type.

        :param command_type: The type of command to register the handler for.
        :type command_type: CommandType
        :param handler_type: The handler type to register.
        :type handler_type: BoundCommandHandlerType
        :raises CommandAlreadyRegisteredError: If a handler for the command type is already registered.
        """
        if command_type in self._handlers:
            raise CommandAlreadyRegisteredError.for_command(command_type)

        self._handlers[command_type] = handler_type

    def handle(self, command: TCommand) -> None:
        """
        Handles a command by routing it to its registered handler.

        :param command: The command to handle.
        :type command: TCommand
        :raises CommandHandlerNotExists: If no handler is registered for the command type.
        :return: The result of handling the command.
        :rtype: Any
        """
        command_type = type(command)
        try:
            handler_cls = self._handlers[command_type]
        except KeyError:
            raise CommandHandlerNotExists.for_command(command_type)

        handler = self._resolver.resolve_command_handler(handler_cls)
        return handler(command=command)
