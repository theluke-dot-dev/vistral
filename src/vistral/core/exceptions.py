from __future__ import annotations


class VistralError(Exception):
    message: str

    def __init__(self, message: str):
        self.message = message
