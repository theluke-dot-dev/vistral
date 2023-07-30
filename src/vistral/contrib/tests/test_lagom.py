import pytest
from lagom import Container, injectable

from vistral.command_bus.command import Command, CommandHandler
from vistral.contrib.lagom import LagomResolver


class DummyService:
    def __init__(self):
        self._call_count = 0

    def __call__(self):
        self._call_count += 1

    @property
    def call_count(self):
        return self._call_count


class DummyCommand(Command):
    pass


@pytest.fixture
def handler_cls():
    class DummyCommandHandler(CommandHandler[DummyCommand]):
        def __init__(self, dummy_service: DummyService = injectable):
            self.dummy_service = dummy_service

        def __call__(self, command: DummyCommand):
            self.dummy_service()
            return None

    return DummyCommandHandler


@pytest.fixture
def container():
    return Container()


@pytest.fixture
def resolver(container):
    return LagomResolver(container=container)


class TestLagomResolver:
    def test_resolve_command_handler(self, container, handler_cls, resolver):
        assert container
        handler = resolver.resolve_command_handler(handler_cls)
        assert isinstance(handler.dummy_service, DummyService)

    def test_resolved_command_handler_can_handle_commands(self, container, handler_cls, resolver):
        assert container
        handler = resolver.resolve_command_handler(handler_cls)
        handler(DummyCommand())
        assert handler.dummy_service.call_count == 1
