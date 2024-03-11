import functools
from typing import TYPE_CHECKING, Any, Callable, Optional, Type, TypeVar, Union, cast


class OpenBASError(Exception):
    def __init__(
        self,
        error_message: Union[str, bytes] = "",
        response_code: Optional[int] = None,
        response_body: Optional[bytes] = None,
    ) -> None:
        Exception.__init__(self, error_message)
        # Http status code
        self.response_code = response_code
        # Full http response
        self.response_body = response_body
        try:
            # if we receive str/bytes we try to convert to unicode/str to have
            # consistent message types (see #616)
            if TYPE_CHECKING:
                assert isinstance(error_message, bytes)
            self.error_message = error_message.decode()
        except Exception:
            if TYPE_CHECKING:
                assert isinstance(error_message, str)
            self.error_message = error_message

    def __str__(self) -> str:
        if self.response_code is not None:
            return f"{self.response_code}: {self.error_message}"
        return f"{self.error_message}"


class OpenBASAuthenticationError(OpenBASError):
    pass


class OpenBASHttpError(OpenBASError):
    pass


class OpenBASParsingError(OpenBASError):
    pass


class RedirectError(OpenBASError):
    pass


class OpenBASHeadError(OpenBASError):
    pass


class OpenBASGetError(OpenBASError):
    pass


class OpenBASUpdateError(OpenBASError):
    pass


class OpenBASListError(OpenBASError):
    pass


class OpenBASCreateError(OpenBASError):
    pass


# For an explanation of how these type-hints work see:
# https://mypy.readthedocs.io/en/stable/generics.html#declaring-decorators
#
# The goal here is that functions which get decorated will retain their types.
__F = TypeVar("__F", bound=Callable[..., Any])


def on_http_error(error: Type[Exception]) -> Callable[[__F], __F]:
    def wrap(f: __F) -> __F:
        @functools.wraps(f)
        def wrapped_f(*args: Any, **kwargs: Any) -> Any:
            try:
                return f(*args, **kwargs)
            except OpenBASHttpError as e:
                raise error(e.error_message, e.response_code, e.response_body) from e

        return cast(__F, wrapped_f)

    return wrap


# Export manually to keep mypy happy
__all__ = [
    "OpenBASAuthenticationError",
    "OpenBASHttpError",
    "OpenBASParsingError",
    "RedirectError",
    "OpenBASHeadError",
    "OpenBASListError",
    "OpenBASGetError",
    "OpenBASUpdateError",
]
