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
            def __init__(self, some_required_string: str):  # This will cause NonExistentService to be unresolvable
                self.some_required_string = some_required_string

        # 2. Define a command and handler that requires the missing dependency
        #    The missing_service parameter is marked `injectable` so that `container.partial` attempts to resolve it.
        class MissingDependencyCommand(Command):
            pass

        class HandlerWithMissingDependency(CommandHandler[MissingDependencyCommand]):
            def __init__(self, missing_service: NonExistentService = injectable):  # Marked for injection
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

        # Check that root_unresolvable_type_str (which is e.dep_type from the caught Lagom exception) is correctly stored.
        # When using `partial` and `injectable`, `e.dep_type` from the UnresolvableType
        # should be the dependency that `partial` was trying to inject and failed for, i.e., NonExistentService.
        assert exc_info.value.root_unresolvable_type_str == "NonExistentService"

        # Check that the "Original lagom error for..." part is present in our custom exception's message
        # This refers to original_exception.dep_type, which is NonExistentService.
        expected_msg_lagom_intro = "Original lagom error for 'NonExistentService':"
        assert expected_msg_lagom_intro in str(exc_info.value)

        # Check that the detailed string of the original Lagom exception (which contains the chain)
        # is part of our custom exception's message.
        original_lagom_error_str = str(exc_info.value.original_exception)
        assert original_lagom_error_str in str(exc_info.value)

        # Verify that Lagom's own error message for NonExistentService (now part of our message)
        # contains the deeper unresolvable type 'str'.
        # Lagom's UnresolvableType.__str__ should format this as "...: NonExistentService => str"
        assert "NonExistentService" in original_lagom_error_str  # The type it failed to build
        assert "str" in original_lagom_error_str  # The root cause for NonExistentService

        # The original_exception.dep_type attribute itself should be for NonExistentService.
        assert exc_info.value.original_exception.dep_type == "NonExistentService"

    def test_shared_deps_provides_same_instance(self, container):
        """
        Tests that when a dependency is listed in shared_deps and resolved via
        the container (e.g. as a singleton), the same instance is injected into
        handlers resolved multiple times by the same resolver.
        """

        class SharedService:
            pass

        class HandlerWithSharedDep(CommandHandler[DummyCommand]):
            def __init__(self, shared_service: SharedService = injectable):
                self.shared_service = shared_service

            def __call__(self, command: DummyCommand) -> None:
                pass

        # Register SharedService as a singleton in the main container
        # Lagom's `partial` with `shared=[SharedService]` makes instances of SharedService
        # singletons *within the context of a single call to the partially applied function*.
        # To test if the resolver provides the same instance across multiple calls to
        # `resolve_command_handler`, the service should be a singleton in the *main container*
        # and `shared=[SharedService]` ensures it's treated as shared if it were constructed
        # per-call otherwise by `partial`.
        # The key is that `container.partial` when `shared` types are provided, will try to
        # reuse instances for those types if they are resolved multiple times *within one resolution process*.
        # However, LagomResolver creates a new partial for each call to resolve_command_handler.
        # The `shared_deps` in LagomResolver's context is more about how `container.partial`
        # itself manages shared instances during *its* resolution of a single function call,
        # not across multiple calls to `LagomResolver.resolve_command_handler`.
        # For the same instance across `resolve_command_handler` calls, it must be a singleton
        # in the underlying container.

        # Let's clarify the test: shared_deps in `container.partial` means that if the dependency
        # is resolved multiple times *during the construction of a single handler instance* (e.g. if multiple
        # __init__ args took SharedService, or a deeper dependency also took SharedService), those would be
        # the same instance for that one handler.
        # To test that `LagomResolver` consistently uses the container's singletons when specified
        # as shared, we make it a singleton in the container.

        shared_instance = SharedService()
        container[SharedService] = shared_instance  # Make it a singleton in the container

        # Pass SharedService to shared_deps for LagomResolver
        resolver_with_shared = LagomResolver(container=container, shared_deps=[SharedService])

        handler1 = resolver_with_shared.resolve_command_handler(HandlerWithSharedDep)
        handler2 = resolver_with_shared.resolve_command_handler(HandlerWithSharedDep)

        assert isinstance(handler1.shared_service, SharedService)
        assert isinstance(handler2.shared_service, SharedService)
        # Both handlers should get the exact same instance from the container because it's a singleton.
        # The role of shared_deps=[SharedService] in LagomResolver's partial ensures that if partial
        # itself were to create SharedService (if not a singleton in container), it would be
        # a temporary singleton for that one resolve_command_handler call. But since it IS a singleton,
        # this is what we expect.
        assert handler1.shared_service is handler2.shared_service
        assert handler1.shared_service is shared_instance

    def test_container_updater_successful_resolution(self, container):
        """
        Tests that container_updater can successfully add a dependency
        that is then resolved for the handler.
        """

        class DynamicService:
            pass

        class HandlerWithDynamicDep(CommandHandler[DummyCommand]):
            def __init__(self, dynamic_service: DynamicService = injectable):
                self.dynamic_service = dynamic_service

            def __call__(self, command: DummyCommand) -> None:
                pass

        dynamic_instance = DynamicService()

        def my_updater(writable_container, _args, _kwargs):
            # Register DynamicService only when the updater is called
            writable_container[DynamicService] = dynamic_instance
            # Note: For container_updater in lagom.partial, the writable_container
            # is a temporary, per-call clone of the original container.
            # Changes here won't affect the original container passed to LagomResolver.

        resolver_with_updater = LagomResolver(container=container, container_updater=my_updater)

        handler = resolver_with_updater.resolve_command_handler(HandlerWithDynamicDep)

        assert isinstance(handler.dynamic_service, DynamicService)
        # Because the updater provides a specific instance into the temporary container
        # used by `partial` for that call.
        assert handler.dynamic_service is dynamic_instance

    def test_container_updater_unsuccessful_resolution(self, container):
        """
        Tests that if container_updater does not provide a required dependency,
        UnresolvedDependencyError is raised.
        """

        class StillMissingService:
            def __init__(self, some_arg_that_cannot_be_provided: str):  # Add unresolvable arg
                self.some_arg_that_cannot_be_provided = some_arg_that_cannot_be_provided

        class HandlerWithStillMissingDep(CommandHandler[DummyCommand]):
            def __init__(self, missing_service: StillMissingService = injectable):
                self.missing_service = missing_service

            def __call__(self, command: DummyCommand) -> None:
                pass

        def non_providing_updater(writable_container, _args, _kwargs):
            # This updater does NOT register StillMissingService
            pass

        resolver_with_non_providing_updater = LagomResolver(
            container=container, container_updater=non_providing_updater
        )

        from vistral.contrib.exceptions import UnresolvedDependencyError
        from lagom.exceptions import UnresolvableType

        with pytest.raises(UnresolvedDependencyError) as exc_info:
            resolver_with_non_providing_updater.resolve_command_handler(HandlerWithStillMissingDep)

        assert exc_info.value.handler_cls is HandlerWithStillMissingDep
        assert isinstance(exc_info.value.original_exception, UnresolvableType)
        # e.dep_type from lagom should be StillMissingService as that's what `partial`
        # was trying to inject due to `injectable` marker.
        assert exc_info.value.root_unresolvable_type_str == "StillMissingService"
        assert "StillMissingService" in str(exc_info.value.original_exception)
