import logging.config
from typing import Any, Callable, Dict, Optional, Type

from django.core.management.color import Style

request_logger: Any
DEFAULT_LOGGING: Any

def configure_logging(logging_config: str, logging_settings: Dict[str, Any]) -> None: ...

class AdminEmailHandler(logging.Handler):
    include_html: bool = ...
    email_backend: Optional[str] = ...
    reporter_class: Type[Any]
    def __init__(
        self, include_html: bool = ..., email_backend: Optional[str] = ..., reporter_class: Optional[Type[Any]] = ...
    ) -> None: ...
    def send_mail(self, subject: str, message: str, *args: Any, **kwargs: Any) -> None: ...
    def connection(self) -> Any: ...
    def format_subject(self, subject: str) -> str: ...

class CallbackFilter(logging.Filter):
    callback: Callable = ...
    def __init__(self, callback: Callable) -> None: ...

class RequireDebugFalse(logging.Filter): ...
class RequireDebugTrue(logging.Filter): ...

class ServerFormatter(logging.Formatter):
    style: Style = ...
    def uses_server_time(self) -> bool: ...

def log_response(
    message: str,
    *args: Any,
    response: Optional[Any] = ...,
    request: Optional[Any] = ...,
    logger: Any = ...,
    level: Optional[Any] = ...,
    exc_info: Optional[Any] = ...
) -> None: ...
