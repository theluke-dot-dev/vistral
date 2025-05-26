from abc import ABC, abstractmethod

from vistral.command_bus.command import CommandHandler, TCommand


class CommandHandlerResolver(ABC):
    """Abstract base class for command handler resolvers."""

    @abstractmethod
    def resolve_command_handler(self, handler_cls: type[CommandHandler[TCommand]], /) -> CommandHandler[TCommand]:
        """
        Resolves a command handler instance from its class.

        :param handler_cls: The class of the command handler to resolve.
        :type handler_cls: type[CommandHandler[TCommand]]
        :return: An instance of the command handler.
        :rtype: CommandHandler[TCommand]
        """
        pass


class SimpleCommandHandlerResolver(CommandHandlerResolver):
    """
    A simple command handler resolver that instantiates handlers directly.

    This resolver does not perform any dependency injection. If a handler
    requires arguments in its `__init__` method, instantiation will likely
    fail with a `TypeError` unless those arguments have default values.
    """

    def resolve_command_handler(self, handler_cls: type[CommandHandler[TCommand]], /) -> CommandHandler[TCommand]:
        """
        Resolves a command handler instance by direct instantiation.

        :param handler_cls: The class of the command handler to resolve.
        :type handler_cls: type[CommandHandler[TCommand]]
        :return: An instance of the command handler.
        :rtype: CommandHandler[TCommand]
        :raises TypeError: If the `handler_cls` requires arguments in its constructor
                           that are not provided (i.e., no default values).
        """
        return handler_cls()
