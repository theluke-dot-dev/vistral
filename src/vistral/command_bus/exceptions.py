from __future__ import annotations

from vistral.command_bus.command import TCommand
from vistral.core.exceptions import VistralError


class CommandAlreadyRegisteredError(VistralError):
    """Exception raised when a command handler is already registered for a command type."""

    @classmethod
    def for_command(cls, command_cls: type[TCommand], /) -> CommandAlreadyRegisteredError:
        """
        Creates a new instance of the exception for the given command class.

        :param command_cls: The command class for which a handler was already registered.
        :type command_cls: type[TCommand]
        :return: A new instance of the exception.
        :rtype: CommandAlreadyRegisteredError
        """
        return cls(f"Command handler for {command_cls.__name__} already registered.")


class CommandHandlerNotExists(VistralError):
    """Exception raised when no command handler is found for a command type."""

    @classmethod
    def for_command(cls, command_cls: type[TCommand], /) -> CommandHandlerNotExists:
        """
        Creates a new instance of the exception for the given command class.

        :param command_cls: The command class for which no handler was found.
        :type command_cls: type[TCommand]
        :return: A new instance of the exception.
        :rtype: CommandHandlerNotExists
        """
        return cls(f"Command handler for {command_cls.__name__} does not exist.")
