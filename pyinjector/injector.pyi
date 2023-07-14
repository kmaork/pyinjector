from typing import Any, Optional


class Injector:
    def __init__(self) -> None: ...

    def attach(self, pid: int) -> None: ...
    def inject(self, path: bytes) -> Any: ...
    def uninject(self, handle: Any) -> None: ...
    def detach(self) -> None: ...

    # If defined(__APPLE__) || defined(__linux)
    def call(self, handle: Any, name: str) -> None: ...

class InjectorError(Exception):
    error_number: int
    error_string: Optional[str]

    def __init__(self, error_number: int, error_string: str) -> None: ...
    def __str__(self) -> str: ...
