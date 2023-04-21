import pytest
from lagom import Container, injectable

from vistral.commandbus.command import Command, CommandHandler
from vistral.contrib.lagom import LagomResolver


class DummyService:
    pass


class DummyCommand(Command):
    pass


@pytest.fixture
def handler_cls():
    class DummyCommandHandler(CommandHandler[DummyCommand, bool]):
        def __init__(self, dummy_service: DummyService = injectable):
            self.dummy_service = dummy_service

        def handle(self, command: DummyCommand) -> bool:
            return True

    return DummyCommandHandler


@pytest.fixture
def container():
    return Container()


@pytest.fixture
def resolver(container):
    return LagomResolver(container=container)


class TestLagomResolver:
    def test_resolve_command_handler(self, container, handler_cls, resolver):
        handler = resolver.resolve_command_handler(handler_cls)
        assert isinstance(handler.dummy_service, DummyService)

    def test_resolved_command_handler_can_handle_commands(self, container, handler_cls, resolver):
        handler = resolver.resolve_command_handler(handler_cls)
        assert handler.handle(DummyCommand())
