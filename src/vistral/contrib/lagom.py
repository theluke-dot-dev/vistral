from typing import Optional, cast

from lagom import Container
from lagom.container import CallTimeContainerUpdate

from vistral.commandbus.command import CommandHandler, TCommand, TCommandResult
from vistral.commandbus.resolver import Resolver


class LagomResolver(Resolver):
    def __init__(
        self,
        container: Container,
        shared_deps: Optional[list[type]] = None,
        container_updater: Optional[CallTimeContainerUpdate] = None,
    ):
        self._partial = lambda func: container.partial(
            func=func, shared=shared_deps, container_updater=container_updater
        )

    def resolve_command_handler(
        self,
        handler_cls: type[CommandHandler[TCommand, TCommandResult]],
    ) -> CommandHandler[TCommand, TCommandResult]:
        return cast(
            CommandHandler[TCommand, TCommandResult], self._partial(func=handler_cls)()
        )  # TODO: add validation and runtime error once not all arguments are bound
