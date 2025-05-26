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

    def test_resolve_handler_with_unresolvable_dependency_raises_error(self, resolver, container):
        # 1. Define a dependency that won't be in the container
        #    Make it require an argument that lagom won't know how to provide by default.
        class NonExistentService:
            def __init__(self, some_required_string: str):
                self.some_required_string = some_required_string

        # 2. Define a command and handler that requires the missing dependency
        class MissingDependencyCommand(Command):
            pass

        class HandlerWithMissingDependency(CommandHandler[MissingDependencyCommand]):
            def __init__(self, missing_service: NonExistentService):
                self.missing_service = missing_service

            def __call__(self, command: MissingDependencyCommand) -> None:
                pass  # The handler logic isn't important for this test

        # 3. Attempt to resolve the handler
        # We expect UnresolvedDependencyError, which wraps Lagom's UnresolvableType
        from vistral.contrib.exceptions import UnresolvedDependencyError
        from lagom.exceptions import UnresolvableType

        with pytest.raises(UnresolvedDependencyError) as exc_info:
            resolver.resolve_command_handler(HandlerWithMissingDependency)

        # 4. Optionally, check the exception details
        assert exc_info.value.handler_cls is HandlerWithMissingDependency
        assert isinstance(exc_info.value.original_exception, UnresolvableType)
        # Check the main part of our custom error message
        expected_msg_main = "Failed to resolve dependencies for handler 'HandlerWithMissingDependency'"
        assert expected_msg_main in str(exc_info.value)

        # Check that root_unresolvable_type_str (which is e.dep_type from the caught Lagom exception) is correctly stored
        # In this test case, Lagom's top-level UnresolvableType will be for HandlerWithMissingDependency.
        assert exc_info.value.root_unresolvable_type_str == "HandlerWithMissingDependency"
        
        # Check that the "Original lagom error for..." part is present in our custom exception's message
        # Note: The "Root cause: ..." part of UnresolvedDependencyError's message will not appear
        # because root_unresolvable_type_str is the same as original_exception.dep_type here.
        expected_msg_lagom_intro = "Original lagom error for 'HandlerWithMissingDependency':"
        assert expected_msg_lagom_intro in str(exc_info.value)
        
        # Check that the detailed string of the original Lagom exception (which contains the chain) 
        # is part of our custom exception's message.
        original_lagom_error_str = str(exc_info.value.original_exception)
        assert original_lagom_error_str in str(exc_info.value)
        
        # Verify that Lagom's own error message is present.
        # In this specific scenario (TypeError breaking the UnresolvableType chain),
        # Lagom's message for the top-level UnresolvableType might not explicitly list
        # the deeper "NonExistentService" or "str" if its get_unresolvable_deps_sequence
        # only returns the top-level type. However, the full str(original_exception) is included.
        # What we can be sure of is that original_lagom_error_str is what Lagom provides.

        # Also ensure the original_exception.dep_type attribute itself is for the top-level handler
        assert exc_info.value.original_exception.dep_type == "HandlerWithMissingDependency"
