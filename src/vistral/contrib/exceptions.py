from typing import Optional
from vistral.core.exceptions import VistralError
from lagom.exceptions import UnresolvableType


class UnresolvedDependencyError(VistralError):
    """Raised when Lagom container fails to resolve a dependency for a command handler."""

    def __init__(
        self,
        handler_cls: type,
        original_exception: UnresolvableType,
        root_unresolvable_type_str: Optional[str] = None,
    ):
        self.handler_cls = handler_cls
        self.original_exception = original_exception
        self.root_unresolvable_type_str = root_unresolvable_type_str

        message = f"Failed to resolve dependencies for handler '{handler_cls.__name__}'."
        if root_unresolvable_type_str and root_unresolvable_type_str != original_exception.dep_type:
            # Add specific info if the root cause is deeper than the top-level handler
            message += f" Root cause: Could not resolve '{root_unresolvable_type_str}'."
        message += f" Original lagom error for '{original_exception.dep_type}': {original_exception}"
        super().__init__(message)
