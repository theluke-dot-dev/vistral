from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Generic, TypeVar

from typing_extensions import TypeAlias


@dataclass(frozen=True)
class Command:
    pass


TCommand = TypeVar("TCommand", bound=Command)


class CommandHandler(Generic[TCommand], ABC):
    @abstractmethod
    def __call__(self, command: TCommand) -> None:
        pass


CommandType: TypeAlias = type[Command]
BoundCommandHandler: TypeAlias = CommandHandler[TCommand]
BoundCommandHandlerType: TypeAlias = type[BoundCommandHandler]
