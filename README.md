# Vistral

A toolbox for your clean architecture application.

## Disclaimer

Please note that this library is in the early stages of development and is
subject to major changes. Use at your own risk.

## Conceptual Overview

Vistral aims to simplify the implementation of [Clean Architecture](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html) principles in Python applications. The core idea behind Clean Architecture is the separation of concerns, achieved by organizing software into layers, with business logic at the center (Entities and Use Cases) and external concerns (like frameworks, UI, and databases) at the periphery.

This library provides tools that facilitate this separation, focusing on patterns like Command Query Responsibility Segregation (CQRS) and enabling clear boundaries between your application's core logic and its infrastructure.

### Core Principles Supported:

*   **Separation of Concerns:** Vistral encourages decoupling your application's use cases (commands/queries) from the UI, database, and other infrastructure components.
*   **Dependency Inversion:** While Vistral itself is not a DI container, its components like `CommandHandlerResolver` are designed to integrate with dependency injection frameworks (e.g., `lagom-di`), allowing your core business logic to depend on abstractions rather than concrete implementations.
*   **Clear Flow of Control:** The `CommandBus` provides a distinct pathway for application commands, making it easier to understand how requests are processed and to introduce cross-cutting concerns (like logging or validation) in a centralized manner (though advanced interceptors/middleware are future considerations).

### Key Components:

*   **`CommandBus`:** At the heart of Vistral's current offerings, the `CommandBus` acts as a mediator to decouple command senders from command handlers. When a command is dispatched, the bus ensures it's routed to the appropriate registered handler.
*   **`Command` and `CommandHandler`:** These define a clear contract for application operations. `Command` objects encapsulate the data for an action, and `CommandHandler` classes contain the logic to process that action.
*   **`CommandHandlerResolver`:** This abstraction allows you to choose how command handlers are instantiated. Vistral provides:
    *   `SimpleCommandHandlerResolver`: For direct, no-dependency instantiation of handlers.
    *   `LagomResolver` (in `vistral.contrib.lagom`): An adapter for the `lagom-di` dependency injection container, allowing handlers to have their dependencies automatically injected.

### Benefits:

*   **Simplified Clean Architecture:** Provides ready-to-use components for common patterns, reducing boilerplate.
*   **Improved Testability:** Decoupled handlers are easier to test in isolation. Dependencies can be mocked when using DI-integrated resolvers.
*   **Flexibility:** The resolver system allows you to adapt handler instantiation to your project's needs, from simple direct instantiation to full DI.
*   **Maintainability:** Clear separation of command handling logic leads to a more organized and understandable codebase.

Vistral is evolving, with plans to introduce more tools and patterns to further support building robust, maintainable, and clean Python applications.

## Installation

Install via `pip`:

```shell
pip install vistral[lagom]
```

Or via `poetry`:

```shell
poetry add vistral --extras lagom
```
*Note: The `[lagom]` extra is required for `LagomResolver` usage if you plan to use dependency injection with `lagom-di`.* If you only need basic functionality without DI, the core `vistral` package is sufficient.

## Usage

This section demonstrates how to use the `CommandBus` for handling commands, showcasing two types of resolvers.

### Using `LagomResolver` (With Dependency Injection via `lagom-di`)

This resolver is ideal when your command handlers have dependencies that need to be injected by a DI container.

#### 1. Define your Command and CommandHandler (with Dependencies)

First, define the data your command will carry and the handler that will process it, including any services it depends on.

```python
from dataclasses import dataclass
from vistral.command_bus import Command, CommandHandler
from lagom import Container # For dependency injection

# Example Service (Dependency for the handler)
class NotificationService:
    def send(self, message: str) -> None:
        print(f"Notification sent: {message}")

# Define a Command
@dataclass(frozen=True)
class SendWelcomeEmail(Command):
    user_id: int
    user_email: str

# Define a CommandHandler for the Command
class SendWelcomeEmailHandler(CommandHandler[SendWelcomeEmail]):
    def __init__(self, notification_service: NotificationService):
        self._notification_service = notification_service

    def __call__(self, command: SendWelcomeEmail) -> None:
        print(f"Handler: Preparing to send welcome email to {command.user_email} (User ID: {command.user_id})")
        message = f"Welcome, user {command.user_id}!"
        self._notification_service.send(message)
        print(f"Handler: Welcome email process for {command.user_email} completed.")
```

**Explanation:**
*   `SendWelcomeEmail`: A command carrying data.
*   `NotificationService`: A service that `SendWelcomeEmailHandler` depends on.
*   `SendWelcomeEmailHandler`: Its `__init__` type-hints `NotificationService`, which `LagomResolver` uses for injection.

#### 2. Set up Dependency Injection and CommandBus

Configure the `lagom.Container`, then create the `LagomResolver` and `CommandBus`.

```python
from vistral.command_bus import CommandBus
from vistral.contrib.lagom import LagomResolver 

# Create a Lagom DI container
container = Container()
# Ensure NotificationService is resolvable by Lagom (often automatic for simple classes)
# For complex cases: container[NotificationService] = MyNotificationServiceImplementation

# Create the resolver and the bus
resolver = LagomResolver(container=container)
command_bus = CommandBus(resolver=resolver)
```

#### 3. Register your Handler

```python
command_bus.register(SendWelcomeEmail, SendWelcomeEmailHandler)
```

#### 4. Create and Handle a Command

```python
welcome_email_command = SendWelcomeEmail(user_id=123, user_email="test@example.com")
print("\nDispatching SendWelcomeEmail command (via LagomResolver)...")
command_bus.handle(welcome_email_command)
print("Command handled.")
```

This example provides a complete, runnable demonstration for `LagomResolver`.

### Using `SimpleCommandHandlerResolver` (No Dependency Injection)

This resolver is suitable for scenarios where command handlers do not have external dependencies, or their dependencies are managed internally or have default values in their constructors. It instantiates handlers directly without a DI container.

#### 1. Define your Command and CommandHandler (No Constructor Args or All Defaults)

```python
from dataclasses import dataclass
from vistral.command_bus import Command, CommandHandler, CommandBus
from vistral.command_bus.resolver import SimpleCommandHandlerResolver # Import the simple resolver

# Define a Command
@dataclass(frozen=True)
class LogInfo(Command):
    message: str

# Define a CommandHandler for the Command
# This handler has no __init__ arguments or all arguments have defaults.
class LogInfoHandler(CommandHandler[LogInfo]):
    def __init__(self, prefix: str = "[INFO]"): # Argument with default value
        self._prefix = prefix

    def __call__(self, command: LogInfo) -> None:
        print(f"{self._prefix} {command.message}")
```

**Explanation:**
*   `LogInfo`: A simple command to log a message.
*   `LogInfoHandler`:
    *   It handles `LogInfo` commands.
    *   Its `__init__` method either takes no arguments or all arguments have default values (like `prefix`). `SimpleCommandHandlerResolver` can instantiate this directly.

#### 2. Set up CommandBus with `SimpleCommandHandlerResolver`

No external DI container is needed.

```python
# Create the simple resolver and the bus
simple_resolver = SimpleCommandHandlerResolver()
command_bus_simple = CommandBus(resolver=simple_resolver)
```

#### 3. Register your Handler

```python
command_bus_simple.register(LogInfo, LogInfoHandler)
```

#### 4. Create and Handle a Command

```python
log_command = LogInfo(message="System processed a request.")
print("\nDispatching LogInfo command (via SimpleCommandHandlerResolver)...")
command_bus_simple.handle(log_command)
print("Command handled.")

# Example with a handler that has no __init__ arguments at all
class AnotherSimpleHandler(CommandHandler[LogInfo]):
    def __call__(self, command: LogInfo) -> None:
        print(f"AnotherSimpleHandler received: {command.message.upper()}")

command_bus_simple.register(LogInfo, AnotherSimpleHandler) # Overwrites previous registration for LogInfo
print("\nDispatching LogInfo command to AnotherSimpleHandler...")
command_bus_simple.handle(log_command) # Will now use AnotherSimpleHandler
print("Command handled.")
```

**Use Case for `SimpleCommandHandlerResolver`:**
*   When your command handlers are simple and don't require external dependencies to be injected.
*   For applications or parts of applications where a full DI container setup is overkill.
*   When handlers can manage their own dependencies or all constructor arguments have defaults.
*   If a handler requires arguments in its `__init__` without defaults, using `SimpleCommandHandlerResolver` will result in a `TypeError`.

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

### Development Setup
(Assuming you have Python and Poetry installed)

1.  Clone the repository:
    ```bash
    git clone https://github.com/your-username/vistral.git
    cd vistral
    ```
2.  Install dependencies:
    ```bash
    poetry install --all-extras
    ```
3.  Activate the virtual environment:
    ```bash
    poetry shell
    ```
4.  Run tests:
    ```bash
    pytest
    ```

## Credits

This project is maintained by [Your Name/Organization].

## License

Vistral is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contact

For questions or support, please open an issue on the GitHub repository.
