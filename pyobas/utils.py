import dataclasses
import datetime
import email.message
import json
import logging
import urllib.parse
from typing import Any, Callable, Dict, Iterator, List, Optional, Tuple, Union

import requests
from pythonjsonlogger import jsonlogger


class _StdoutStream:
    def __call__(self, chunk: Any) -> None:
        print(chunk)


def get_content_type(content_type: Optional[str]) -> str:
    message = email.message.Message()
    message["content-type"] = content_type

    return message.get_content_type()


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


class EnhancedJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if dataclasses.is_dataclass(o):
            return dataclasses.asdict(o)
        return super().default(o)


@dataclasses.dataclass(frozen=True)
class RequiredOptional:
    required: Tuple[str, ...] = ()
    optional: Tuple[str, ...] = ()
    exclusive: Tuple[str, ...] = ()

    def validate_attrs(
        self,
        *,
        data: Dict[str, Any],
        excludes: Optional[List[str]] = None,
    ) -> None:
        if excludes is None:
            excludes = []

        if self.required:
            required = [k for k in self.required if k not in excludes]
            missing = [attr for attr in required if attr not in data]
            if missing:
                raise AttributeError(f"Missing attributes: {', '.join(missing)}")

        if self.exclusive:
            exclusives = [attr for attr in data if attr in self.exclusive]
            if len(exclusives) > 1:
                raise AttributeError(
                    f"Provide only one of these attributes: {', '.join(exclusives)}"
                )
            if not exclusives:
                raise AttributeError(
                    f"Must provide one of these attributes: "
                    f"{', '.join(self.exclusive)}"
                )


class CustomJsonFormatter(jsonlogger.JsonFormatter):
    def add_fields(self, log_record, record, message_dict):
        super(CustomJsonFormatter, self).add_fields(log_record, record, message_dict)
        if not log_record.get("timestamp"):
            # This doesn't use record.created, so it is slightly off
            now = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%fZ")
            log_record["timestamp"] = now
        if log_record.get("level"):
            log_record["level"] = log_record["level"].upper()
        else:
            log_record["level"] = record.levelname


def logger(level, json_logging=True):
    # Exceptions
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("pika").setLevel(logging.ERROR)
    # Exceptions
    if json_logging:
        log_handler = logging.StreamHandler()
        log_handler.setLevel(level)
        formatter = CustomJsonFormatter("%(timestamp)s %(level)s %(name)s %(message)s")
        log_handler.setFormatter(formatter)
        logging.basicConfig(handlers=[log_handler], level=level, force=True)
    else:
        logging.basicConfig(level=level)

    class AppLogger:
        def __init__(self, name):
            self.local_logger = logging.getLogger(name)

        @staticmethod
        def prepare_meta(meta=None):
            return None if meta is None else {"attributes": meta}

        @staticmethod
        def setup_logger_level(lib, log_level):
            logging.getLogger(lib).setLevel(log_level)

        def debug(self, message, meta=None):
            self.local_logger.debug(message, extra=AppLogger.prepare_meta(meta))

        def info(self, message, meta=None):
            self.local_logger.info(message, extra=AppLogger.prepare_meta(meta))

        def warning(self, message, meta=None):
            self.local_logger.warning(message, extra=AppLogger.prepare_meta(meta))

        def error(self, message, meta=None):
            # noinspection PyTypeChecker
            self.local_logger.error(
                message, exc_info=1, extra=AppLogger.prepare_meta(meta)
            )

    return AppLogger
