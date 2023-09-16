import pytest

from vistral.command_bus.command import CommandHandler


class TestDefaultResolver:
    @pytest.fixture
    def resolver(self, resolver_cls):
        return resolver_cls()

    def test_resolve_command_handler(self, resolver, handler_cls):
        handler = resolver.resolve_command_handler(handler_cls)
        assert isinstance(handler, CommandHandler)
        assert isinstance(handler, handler_cls)

    def test_resolve_command_handler_returns_different_instance(self, resolver, handler_cls):
        handler1 = resolver.resolve_command_handler(handler_cls)
        handler2 = resolver.resolve_command_handler(handler_cls)
        assert handler1 is not handler2
