from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Generic, TypeVar


@dataclass(frozen=True)
class Command:
    pass


TCommand = TypeVar("TCommand", bound=Command)
TCommandResult = TypeVar("TCommandResult")


class CommandHandler(Generic[TCommand, TCommandResult], ABC):
    @abstractmethod
    def handle(self, command: TCommand) -> TCommandResult:
        pass


# TODO: add some (mypy plugin?) logic to properly handle those generics
