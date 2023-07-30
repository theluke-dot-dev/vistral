from vistral.command_bus.command import TCommand


class CommandAlreadyRegisteredError(Exception):
    def __init__(self, command_cls: type[TCommand]):
        self.message = f"Command handler for {command_cls.__name__} already registered."


class CommandHandlerNotExists(Exception):
    def __init__(self, command_cls: type[TCommand]):
        self.message = f"Command handler for {command_cls.__name__} does not exist."
