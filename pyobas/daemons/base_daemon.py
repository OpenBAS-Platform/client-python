from abc import ABC, abstractmethod
from inspect import signature
from types import FunctionType

from pyobas.client import OpenBAS
from pyobas.configuration import Configuration
from pyobas.exceptions import OpenBASError
from pyobas.utils import logger


class BaseDaemon(ABC):
    """A base class for implementing a kind of daemon that periodically polls
    a given callback.

    :param configuration: configuration to provide the daemon
        (allowing for looking up values within the callback for example)
    :type configuration: Configuration
    :param callback: a method or function to periodically call, defaults to None.
    :type callback: callable, optional
    :param logger: a logger object, to log events. if not supplied, a default logger
        will be spawned to provide this functionality.
    :type logger: Any
    :param api_client: an API client that will provide connectivity with other systems.
    :type api_client: Any
    """

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
        """A run-once method that inheritors must implement. This serves to instantiate
        all useful objects and functionality for the implementor to run.
        """
        pass

    @abstractmethod
    def _start_loop(self):
        """Starts the daemon's main execution loop. Implementors should implement
        the main execution logic in here.
        """
        pass

    def _try_callback(self):
        """Tries to call the configured callback. Note that if any error is thrown,
        it is immediately swallowed (but still logged) allowing the collector to keep
        running. This is useful for any transient issue (e.g. API endpoint down...).
        """
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
        """Start the daemon. This will run the implementor's run-once setup method and
        follow-up with the main execution loop. Note that at this point, if there is no
        configured callback, the method will abort and kill the daemon.
        """
        if self._callback is None:
            raise OpenBASError("This daemon has no configured callback.")
        self._setup()
        self._start_loop()

    def set_callback(self, callback: callable):
        """Configures a callback to call in the main execution loop. If the callback
        was not provided in the daemon's ctor, this should be set before calling start().
        """
        self._callback = callback

    def get_id(self):
        """Returns the daemon instance's ID contained in configuration. Configuration
        must define any of these keys: `id`, `collector_id`, `injector_id`.
        """
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
