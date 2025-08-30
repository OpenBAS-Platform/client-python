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
        # Start with the provided error message
        message = self.error_message

        # List of generic HTTP status messages that indicate we should look deeper
        generic_messages = (
            "Internal Server Error",
            "Bad Request",
            "Not Found",
            "Unauthorized",
            "Forbidden",
            "Service Unavailable",
            "Gateway Timeout",
            "Unknown error",
            "Validation Failed",
        )

        # Only try to extract from response body if message is truly generic
        # Don't override if we already have a specific error message
        if (
            not message or (message in generic_messages and len(message) < 30)
        ) and self.response_body is not None:
            try:
                import json

                body = self.response_body.decode(errors="ignore")
                data = json.loads(body)
                extracted_msg = None

                if isinstance(data, dict):
                    # Try various common error fields
                    if "error" in data:
                        err = data.get("error")
                        if isinstance(err, dict) and "message" in err:
                            extracted_msg = err.get("message")
                        elif isinstance(err, str):
                            extracted_msg = err
                    elif "message" in data:
                        extracted_msg = data.get("message")
                    elif "execution_message" in data:
                        extracted_msg = data.get("execution_message")
                    elif "detail" in data:
                        extracted_msg = data.get("detail")
                    elif "errors" in data:
                        errs = data.get("errors")
                        if isinstance(errs, list) and errs:
                            # Join any messages in the list
                            parts = []
                            for item in errs:
                                if isinstance(item, dict) and "message" in item:
                                    parts.append(str(item.get("message")))
                                else:
                                    parts.append(str(item))
                            extracted_msg = "; ".join(parts)
                        elif isinstance(errs, dict):
                            # Handle nested validation errors structure
                            if "children" in errs:
                                validation_errors = []
                                children = errs.get("children", {})
                                for field, field_errors in children.items():
                                    if (
                                        isinstance(field_errors, dict)
                                        and "errors" in field_errors
                                    ):
                                        field_error_list = field_errors.get(
                                            "errors", []
                                        )
                                        if field_error_list:
                                            for err_msg in field_error_list:
                                                validation_errors.append(
                                                    f"{field}: {err_msg}"
                                                )
                                if validation_errors:
                                    base_msg = data.get("message", "Validation Failed")
                                    extracted_msg = (
                                        f"{base_msg}: {'; '.join(validation_errors)}"
                                    )
                            else:
                                # Try to get any string representation
                                parts = []
                                for key, value in errs.items():
                                    if value:
                                        parts.append(f"{key}: {value}")
                                if parts:
                                    extracted_msg = "; ".join(parts)
                        elif isinstance(errs, str):
                            extracted_msg = errs

                # Use extracted message if it's better than what we have
                if extracted_msg and extracted_msg not in generic_messages:
                    message = str(extracted_msg)
                elif not message:
                    # Last resort: use the raw body
                    message = body[:500]

            except json.JSONDecodeError:
                # Not JSON, use raw text if we don't have a good message
                if not message or message in generic_messages:
                    try:
                        decoded = self.response_body.decode(errors="ignore")[:500]
                        if decoded and decoded not in generic_messages:
                            message = decoded
                    except Exception:
                        pass
            except Exception:
                pass

        # Final fallback
        if not message:
            message = "Unknown error"

        # Clean up the message - remove extra whitespace and newlines
        message = " ".join(message.split())

        if self.response_code is not None:
            return f"{self.response_code}: {message}"
        return f"{message}"


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


class ConfigurationError(OpenBASError):
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
    "ConfigurationError",
    "OpenBASAuthenticationError",
    "OpenBASHttpError",
    "OpenBASParsingError",
    "RedirectError",
    "OpenBASHeadError",
    "OpenBASListError",
    "OpenBASGetError",
    "OpenBASUpdateError",
]
