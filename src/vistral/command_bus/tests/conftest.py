import pytest

from vistral.command_bus import CommandHandlerResolver
from vistral.command_bus.command import Command, CommandHandler


@pytest.fixture
def resolver_cls():
    class DefaultResolver(CommandHandlerResolver):
        def resolve_command_handler(self, handler_cls, /):
            return handler_cls()

    return DefaultResolver


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
