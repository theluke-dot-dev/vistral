from typing import Optional, cast

try:
    from lagom import Container
    from lagom.container import CallTimeContainerUpdate
    from lagom.exceptions import UnresolvableType
except ImportError as import_error:
    raise ImportError(
        f"`lagom` dependency is missing: {import_error}. "
        + "To use LagomResolver, Re-install `vistral` with [lagom] extra dependency."
    ) from None

from vistral.command_bus.command import BoundCommandHandler, BoundCommandHandlerType
from vistral.command_bus.resolver import CommandHandlerResolver
from vistral.contrib.exceptions import UnresolvedDependencyError


class LagomResolver(CommandHandlerResolver):
    """
    A command handler resolver that uses a Lagom container to resolve handlers.

    :param container: The Lagom container instance.
    :type container: Container
    :param shared_deps: A list of types to be shared across all handlers.
    :type shared_deps: Optional[list[type]], optional
    :param container_updater: A function to update the container at call time.
    :type container_updater: Optional[CallTimeContainerUpdate], optional
    """

    def __init__(
        self,
        container: Container,
        shared_deps: Optional[list[type]] = None,  # Kept for potential future use, but not directly used by resolve
        container_updater: Optional[CallTimeContainerUpdate] = None,  # Kept for potential future use
    ):
        """
        Initializes a new instance of the LagomResolver class.

        :param container: The Lagom container instance.
        :type container: Container
        :param shared_deps: A list of types to be shared across all handlers. Defaults to None.
                           Note: With direct resolution via `container.resolve`, `shared_deps`
                           are typically managed by Lagom's singleton definitions if needed globally,
                           or would require more complex per-resolution context if truly temporary.
        :type shared_deps: Optional[list[type]], optional
        :param container_updater: A function to update the container at call time. Defaults to None.
                                 Note: This is not directly used by `container.resolve`.
                                 If per-call updates are needed, the container itself
                                 would need to be modified or a sub-container used.
        :type container_updater: Optional[CallTimeContainerUpdate], optional
        """
        self._container = container
        self._shared_deps = shared_deps
        self._container_updater = container_updater

        # Reconstruct self._partial using instance attributes
        self._partial = lambda func_to_wrap: self._container.partial(
            func=func_to_wrap,
            shared=self._shared_deps,
            container_updater=self._container_updater
        )

    def resolve_command_handler(
        self,
        handler_cls: BoundCommandHandlerType,
    ) -> BoundCommandHandler:
        """
        Resolves a command handler instance from its class using the Lagom container's partial application.

        :param handler_cls: The class of the command handler to resolve.
        :type handler_cls: BoundCommandHandlerType
        :raises UnresolvedDependencyError: If the Lagom container fails to resolve a dependency
                                         when the partially applied handler factory is called.
        :return: An instance of the command handler.
        :rtype: BoundCommandHandler
        """
        resolved_handler_factory = self._partial(handler_cls) # Pass handler_cls as positional argument
        try:
            # When the factory is called, Lagom attempts to resolve dependencies
            # for the __init__ of handler_cls that were marked with `lagom.injectable`
            # or if `magic_partial` was used (which it's not here by default through `self._partial`).
            # If `handler_cls` has non-default, non-injectable args, this call itself might
            # raise TypeError before Lagom's UnresolvableType if those args aren't provided.
            # However, the goal is to catch Lagom's DI errors.
            handler_instance = resolved_handler_factory()
            return cast(BoundCommandHandler, handler_instance)
        except UnresolvableType as e:
            # If Lagom's partial application fails to resolve a dependency it was
            # supposed to inject (e.g., an argument marked `lagom.injectable`),
            # it will raise UnresolvableType. e.dep_type should refer to the
            # specific dependency that could not be resolved.
            lagom_reported_unresolvable_type_str = e.dep_type
            
            raise UnresolvedDependencyError(
                handler_cls=handler_cls, # The handler we attempted to build
                original_exception=e, 
                root_unresolvable_type_str=lagom_reported_unresolvable_type_str, # The specific dep Lagom failed on
            ) from e
        # Note: If handler_cls.__init__ has required arguments not managed by Lagom's partial
        # (i.e., not type-hinted for magic_partial or not marked `injectable` for `partial`),
        # resolved_handler_factory() might raise a TypeError directly.
        # The current subtask focuses on UnresolvableType. Catching TypeError here could be
        # ambiguous as it might hide programming errors in the handler's __init__ signature
        # versus actual DI failures for dependencies Lagom was expected to provide.
