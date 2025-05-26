import pytest
from dataclasses import dataclass # Moved to top, before usage

from vistral.command_bus.command import Command, CommandHandler
from vistral.command_bus.resolver import SimpleCommandHandlerResolver

# --- Test Fixtures ---

@dataclass(frozen=True)
class SimpleCommand(Command):
    data: str = "default"

class SimpleNoArgHandler(CommandHandler[SimpleCommand]):
    def __init__(self):
        self.handled_command_data = None

    def __call__(self, command: SimpleCommand) -> None:
        self.handled_command_data = command.data
        # print(f"SimpleNoArgHandler handled: {self.handled_command_data}")

class HandlerWithArgs(CommandHandler[SimpleCommand]):
    def __init__(self, dependency: str, another_dep: int = 5):
        self.dependency = dependency
        self.another_dep = another_dep
        self.handled_command_data = None

    def __call__(self, command: SimpleCommand) -> None:
        self.handled_command_data = command.data
        # print(f"HandlerWithArgs handled: {self.handled_command_data} with {self.dependency} and {self.another_dep}")

class HandlerWithDefaultArgs(CommandHandler[SimpleCommand]):
    def __init__(self, dependency: str = "default_dep"):
        self.dependency = dependency
        self.handled_command_data = None

    def __call__(self, command: SimpleCommand) -> None:
        self.handled_command_data = command.data

@pytest.fixture
def simple_resolver() -> SimpleCommandHandlerResolver:
    return SimpleCommandHandlerResolver()

# --- Test Cases ---

def test_resolve_handler_returns_instance_of_handler_cls(simple_resolver):
    """Test that resolve_command_handler returns an instance of the provided handler_cls."""
    handler_instance = simple_resolver.resolve_command_handler(SimpleNoArgHandler)
    assert isinstance(handler_instance, SimpleNoArgHandler)

def test_resolve_handler_returns_new_instance_each_time(simple_resolver):
    """Test that it returns a new instance each time it's called."""
    handler1 = simple_resolver.resolve_command_handler(SimpleNoArgHandler)
    handler2 = simple_resolver.resolve_command_handler(SimpleNoArgHandler)
    assert handler1 is not handler2

def test_resolve_handler_with_required_args_raises_typeerror(simple_resolver):
    """
    Test behavior with handlers that have required __init__ arguments.
    It should raise a TypeError as this resolver doesn't do DI.
    """
    with pytest.raises(TypeError) as exc_info:
        simple_resolver.resolve_command_handler(HandlerWithArgs)
    # Check if the error message is somewhat related to missing arguments
    # Exact message can vary between Python versions / environments
    assert "required positional argument" in str(exc_info.value) or "__init__() missing" in str(exc_info.value)


def test_resolve_handler_with_only_default_args_succeeds(simple_resolver):
    """
    Test that handlers with all __init__ arguments having defaults can be resolved.
    """
    try:
        handler_instance = simple_resolver.resolve_command_handler(HandlerWithDefaultArgs)
        assert isinstance(handler_instance, HandlerWithDefaultArgs)
        assert handler_instance.dependency == "default_dep"
    except TypeError:
        pytest.fail("TypeError raised unexpectedly for HandlerWithDefaultArgs")

def test_resolved_handler_can_be_called(simple_resolver):
    """Test that a resolved handler (with no args) can actually handle a command."""
    handler = simple_resolver.resolve_command_handler(SimpleNoArgHandler)
    command_instance = SimpleCommand(data="test_data")
    handler(command_instance)
    assert handler.handled_command_data == "test_data"
