from abc import ABC, abstractmethod
from inspect import signature
from types import FunctionType

from pyobas.client import OpenBAS
from pyobas.configuration import Configuration
from pyobas.exceptions import OpenBASError
from pyobas.utils import logger


class BaseDaemon(ABC):
    def __init__(
        self,
        configuration: Configuration,
        callback: callable = None,
        logger=None,
        api_client=None,
    ):
        self._configuration = configuration
        self._callback = callback
        self.api = api_client or BaseDaemon.__get_default_api_client(
            url=self._configuration.get("openbas_url"),
            token=self._configuration.get("openbas_token"),
        )

        # logging
        # compatibility layer: in order for older configs to still work, search for legacy names
        actual_log_level = (
            self._configuration.get("log_level")
            or self._configuration.get("collector_log_level")
            or self._configuration.get("injector_log_level")
            or "info"
        )
        actual_log_name = (
            self._configuration.get("name")
            or self._configuration.get("collector_name")
            or self._configuration.get("injector_name")
            or "daemon"
        )
        self.logger = logger or BaseDaemon.__get_default_logger(
            actual_log_level.upper(),
            actual_log_name,
        )

    @abstractmethod
    def _setup(self):
        pass

    @abstractmethod
    def _start_loop(self):
        pass

    def _try_callback(self):
        try:
            # this is some black magic to allow injecting the collector daemon instance
            # into an arbitrary callback that has a specific argument name
            # this allow for avoiding subclassing the CollectorDaemon class just to provide the callback
            # Example:
            #
            # def standalone_func(collector):
            #   collector.api.call_openbas()
            #
            # CollectorDaemon(config=<pyboas.configuration.Configuration>, standalone_func).start()
            if (
                isinstance(self._callback, FunctionType)
                and "collector" in signature(self._callback).parameters
            ):
                self._callback(collector=self)
            else:
                self._callback()
        except Exception as err:  # pylint: disable=broad-except
            self.logger.error(f"Error calling: {err}")

    def start(self):
        if self._callback is None:
            raise OpenBASError("This daemon has no configured callback.")
        self._setup()
        self._start_loop()

    def set_callback(self, callback: callable):
        self._callback = callback

    def get_id(self):
        return (
            self._configuration.get("id")
            or self._configuration.get("collector_id")
            or self._configuration.get("injector_id")
        )

    @classmethod
    def __get_default_api_client(cls, url, token):
        return OpenBAS(url=url, token=token)

    @classmethod
    def __get_default_logger(cls, log_level, name):
        return logger(log_level)(name)
