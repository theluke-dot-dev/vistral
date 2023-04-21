from unittest.mock import MagicMock

import pytest

from vistral.commandbus.bus import CommandBus
from vistral.commandbus.exceptions import CommandAlreadyRegisteredError, CommandHandlerNotExists
from vistral.commandbus.resolver import Resolver


class TestCommandBus:
    @pytest.fixture
    def resolver(self):
        return MagicMock(spec=Resolver)

    @pytest.fixture
    def command_bus(self, resolver):
        return CommandBus(resolver=resolver)

    def test_register_handler(self, command_bus, command_cls, handler_cls):
        command_bus.register(command_cls, handler_cls)
        assert command_cls in command_bus._handlers
        assert command_bus._handlers[command_cls] == handler_cls

    def test_register_duplicate_handler_raises_error(self, command_bus, command_cls, handler_cls):
        command_bus.register(command_cls, handler_cls)
        with pytest.raises(CommandAlreadyRegisteredError):
            command_bus.register(command_cls, handler_cls)

    def test_handle_command(self, command_bus, command_cls, handler_cls, command_result, resolver):
        command_bus.register(command_cls, handler_cls)
        command = command_cls()
        handler = handler_cls()
        resolver.resolve_command_handler.return_value = handler
        result = command_bus.handle(command)
        assert result == command_result

        resolver.resolve_command_handler.assert_called_once_with(handler_cls=handler_cls)

    def test_handle_unregistered_command_raises_error(self, command_bus, command_cls):
        with pytest.raises(CommandHandlerNotExists):
            command_bus.handle(command_cls())
