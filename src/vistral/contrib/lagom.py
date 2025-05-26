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
        # self._shared_deps = shared_deps # Store if specific per-call singleton logic is added later
        # self._container_updater = container_updater # Store if specific per-call update logic is added later

    def resolve_command_handler(
        self,
        handler_cls: BoundCommandHandlerType,
    ) -> BoundCommandHandler:
        """
        Resolves a command handler instance from its class using the Lagom container.

        :param handler_cls: The class of the command handler to resolve.
        :type handler_cls: BoundCommandHandlerType
        :raises UnresolvedDependencyError: If the Lagom container fails to resolve a dependency.
        :return: An instance of the command handler.
        :rtype: BoundCommandHandler
        """
        try:
            # Using resolve (or container[handler_cls]) is the direct way to ask Lagom to build the type.
            # It will automatically handle dependency resolution based on type hints in __init__.
            instance = self._container.resolve(handler_cls)
            return cast(BoundCommandHandler, instance)
        except UnresolvableType as e:
            # The 'e.dep_type' attribute of the caught Lagom UnresolvableType exception
            # indicates the specific type that Lagom reported it couldn't build at this level.
            # The full str(e) will include any deeper causal chain Lagom itself formats.
            lagom_reported_unresolvable_type_str = e.dep_type
            
            raise UnresolvedDependencyError(
                handler_cls=handler_cls,
                original_exception=e, 
                root_unresolvable_type_str=lagom_reported_unresolvable_type_str,
            ) from e
