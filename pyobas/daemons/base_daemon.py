from abc import ABC, abstractmethod
from pyobas.client import OpenBAS
from pyobas.utils import logger
from pyobas.configuration import Configuration

class BaseDaemon(ABC):
    def __init__(self, configuration: Configuration, callback: callable, logger=None, api_client=None):
        self._configuration = configuration
        self._callback = callback
        self.api = api_client or BaseDaemon.__get_default_api_client(
            url=self._configuration.get("openbas_url"),
            token=self._configuration.get("openbas_token"),
        )
        self.logger = logger or BaseDaemon.__get_default_logger(self._configuration.get("log_level"), self._configuration.get("collector_name"))

    @abstractmethod
    def _setup(self):
        pass

    @abstractmethod
    def _start_loop(self):
        pass

    def _try_callback(self):
        try:
            self._callback(self)
        except Exception as err:  # pylint: disable=broad-except
            self.logger.error(f"Error calling: {err}")

    def start(self):
        self._setup()
        self._start_loop()


    @classmethod
    def __get_default_api_client(cls, url, token):
        return OpenBAS(url=url, token=token)

    @classmethod
    def __get_default_logger(cls, log_level, name):
        return logger(log_level)(name)