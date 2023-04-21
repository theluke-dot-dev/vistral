from typing import NewType

import pytest

from vistral.commandbus.command import Command, CommandHandler

CommandResultType = NewType("CommandResultType", str)


@pytest.fixture
def command_result():
    return CommandResultType("CommandResult")


@pytest.fixture
def command_cls():
    class DummyCommand(Command):
        pass

    return DummyCommand


@pytest.fixture
def handler_cls(command_cls, command_result):
    class DummyHandler(CommandHandler[command_cls, CommandResultType]):
        def handle(self, command: command_cls):
            return command_result

    return DummyHandler
