from __future__ import annotations


class VistralError(Exception):
    """
    Base class for all Vistral exceptions.

    :param message: The error message.
    :type message: str
    """

    message: str

    def __init__(self, message: str):
        """
        Initializes a new instance of the VistralError class.

        :param message: The error message.
        :type message: str
        """
        super().__init__(message)
        self.message = message
