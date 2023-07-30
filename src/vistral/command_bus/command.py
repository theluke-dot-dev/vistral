from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Generic, TypeVar


@dataclass(frozen=True)
class Command:
    pass


TCommand = TypeVar("TCommand", bound=Command)


class CommandHandler(Generic[TCommand], ABC):
    @abstractmethod
    def __call__(self, command: TCommand) -> None:
        pass
