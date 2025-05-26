from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Generic, TypeVar

from typing_extensions import TypeAlias


@dataclass(frozen=True)
class Command:
    """Base class for all commands."""

    pass


TCommand = TypeVar("TCommand", bound=Command)
"""Type variable representing a command type."""


class CommandHandler(Generic[TCommand], ABC):
    """
    Abstract base class for command handlers.

    :param TCommand: The type of command this handler can process.
    :type TCommand: TypeVar
    """

    @abstractmethod
    def __call__(self, command: TCommand) -> None:
        """
        Handles the given command.

        :param command: The command to handle.
        :type command: TCommand
        """
        pass


CommandType: TypeAlias = type[Command]
"""Type alias for command types."""
BoundCommandHandler: TypeAlias = CommandHandler[TCommand]
"""Type alias for a command handler bound to a specific command type."""
BoundCommandHandlerType: TypeAlias = type[BoundCommandHandler]
"""Type alias for the type of a bound command handler."""
