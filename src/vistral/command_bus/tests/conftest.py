import pytest

from vistral.command_bus.command import Command, CommandHandler


@pytest.fixture
def command_cls():
    class DummyCommand(Command):
        pass

    return DummyCommand


@pytest.fixture
def handler_cls(command_cls):
    class DummyHandler(CommandHandler[command_cls]):
        def __call__(self, command: command_cls) -> None:
            return None

    return DummyHandler
