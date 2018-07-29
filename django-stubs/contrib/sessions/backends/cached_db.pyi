from typing import (
    Any,
    Dict,
    Optional,
)


class SessionStore:
    def __init__(self, session_key: Optional[str] = ...) -> None: ...
    @property
    def cache_key(self) -> str: ...
    def delete(self, session_key: Optional[str] = ...) -> None: ...
    def exists(self, session_key: str) -> bool: ...
    def flush(self) -> None: ...
    def load(self) -> Dict[Any, Any]: ...
    def save(self, must_create: bool = ...) -> None: ...