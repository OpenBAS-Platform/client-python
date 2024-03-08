import email.message
import logging
import urllib.parse
from typing import Any, Callable, Dict, Iterator, Literal, Optional, Union

import requests


class _StdoutStream:
    def __call__(self, chunk: Any) -> None:
        print(chunk)


def get_content_type(content_type: Optional[str]) -> str:
    message = email.message.Message()
    message["content-type"] = content_type

    return message.get_content_type()


class MaskingFormatter(logging.Formatter):
    """A logging formatter that can mask credentials"""

    def __init__(
        self,
        fmt: Optional[str] = logging.BASIC_FORMAT,
        datefmt: Optional[str] = None,
        style: Literal["%", "{", "$"] = "%",
        validate: bool = True,
        masked: Optional[str] = None,
    ) -> None:
        super().__init__(fmt, datefmt, style, validate)
        self.masked = masked

    def _filter(self, entry: str) -> str:
        if not self.masked:
            return entry

        return entry.replace(self.masked, "[MASKED]")

    def format(self, record: logging.LogRecord) -> str:
        original = logging.Formatter.format(self, record)
        return self._filter(original)


def response_content(
    response: requests.Response,
    streamed: bool,
    action: Optional[Callable[[bytes], None]],
    chunk_size: int,
    *,
    iterator: bool,
) -> Optional[Union[bytes, Iterator[Any]]]:
    if iterator:
        return response.iter_content(chunk_size=chunk_size)

    if streamed is False:
        return response.content

    if action is None:
        action = _StdoutStream()

    for chunk in response.iter_content(chunk_size=chunk_size):
        if chunk:
            action(chunk)
    return None


def copy_dict(
    *,
    src: Dict[str, Any],
    dest: Dict[str, Any],
) -> None:
    for k, v in src.items():
        if isinstance(v, dict):
            for dict_k, dict_v in v.items():
                dest[f"{k}[{dict_k}]"] = dict_v
        else:
            dest[k] = v


class EncodedId(str):
    def __new__(cls, value: Union[str, int, "EncodedId"]) -> "EncodedId":
        if isinstance(value, EncodedId):
            return value

        if not isinstance(value, (int, str)):
            raise TypeError(f"Unsupported type received: {type(value)}")
        if isinstance(value, str):
            value = urllib.parse.quote(value, safe="")
        return super().__new__(cls, value)


def remove_none_from_dict(data: Dict[str, Any]) -> Dict[str, Any]:
    return {k: v for k, v in data.items() if v is not None}
